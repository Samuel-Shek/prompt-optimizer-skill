#!/usr/bin/env python3
"""Test host skill selection, not optimizer output quality (standard library only).

Usage: python3 evals/trigger_eval.py --out NEW_DIR [--lang zh|en|all]
An absent or empty output directory is required; existing results are never resumed.
Exit 0 means all selected cases matched, 1 means evaluation failures, 2 a setup error.
"""
import argparse
import concurrent.futures as cf
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil


HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / "SKILL.md"
CASES = HERE / "trigger_cases.json"
# Load by absolute file path: works from any cwd and under file-based test loaders.
_spec = importlib.util.spec_from_file_location("_trigger_run_eval", HERE / "run_eval.py")
_runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_runner)
run_claude = _runner.run_claude
CLI_FLAGS = _runner.CLI_FLAGS


def read_description(skill):
    """Read a top-level frontmatter string without requiring a YAML dependency.

    Supports plain/single-quoted/JSON-double-quoted scalars and indented > or |
    blocks (including +/- chomping indicators). Other YAML forms fail explicitly.
    Only the frontmatter is read as metadata; the skill body is not a host prompt.
    """
    lines = Path(skill).read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("SKILL.md frontmatter is not closed") from None
    positions = [i for i in range(1, end) if lines[i].startswith("description:")]
    if len(positions) != 1:
        raise ValueError("frontmatter must contain exactly one description")
    start = positions[0]
    value = lines[start].partition(":")[2].strip()
    if re.fullmatch(r"[>|][+-]?", value):
        block = []
        for line in lines[start + 1:end]:
            if line and not line.startswith(" "):
                break
            block.append(line)
        nonempty = [line for line in block if line.strip()]
        indent = min((len(line) - len(line.lstrip(" ")) for line in nonempty), default=0)
        block = [line[indent:] for line in block]
        # Paragraph breaks and more-indented lines remain separate in folded YAML.
        text = ""
        for i, line in enumerate(block):
            text += line
            if i + 1 < len(block):
                following = block[i + 1]
                fold = value[0] == ">" and line and following and not line.startswith(" ") and not following.startswith(" ")
                text += " " if fold else "\n"
        value = text.strip()
    elif value.startswith('"'):
        value = json.loads(value)
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1].replace("''", "'")
    elif not value or value[0] in "[{&*!>|'" or value in ("null", "~", "true", "false"):
        raise ValueError("unsupported description scalar; use a > block or quoted string")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("frontmatter description must be a nonempty string")
    return value


def host_prompt(description):
    return (
        "You are a general-purpose assistant selecting a skill for a standalone user request.\n"
        "Available skills (name and description):\n"
        + json.dumps([
            {"name": "prompt-optimizer", "description": description},
            {"name": "fictional-orbit-catalog", "description": "Look up catalog identifiers for fictional spacecraft models."},
            {"name": "fictional-quilt-index", "description": "Find inventory codes in a fictional quilt pattern archive."},
        ], ensure_ascii=False, indent=2)
        + "\nDecide whether to select prompt-optimizer for the user request.\n"
        "Output exactly SKILL: prompt-optimizer or SKILL: none on the first line.\n"
        "You may stop after that line; answering the request is optional.\n"
    )


def parse_selection(text):
    """Only an exact first-line marker is valid; never search later lines."""
    first = text.splitlines()[0] if text else ""
    return {"SKILL: prompt-optimizer": "invoke", "SKILL: none": "direct"}.get(first)


def score_result(case, result, output_path):
    parsed = parse_selection(result["text"])
    return {
        "lang": case["lang"], "expected": case["expected"],
        "output_path": str(output_path), "parsed": parsed,
        "matches": parsed is not None and parsed == case["expected"] and result["exit"] == 0,
        "exit": result["exit"], "stderr": result.get("stderr", ""),
        "seconds": result.get("seconds"), "status": "finished",
    }


def summarize(records):
    rows = list(records.values())
    def metric(expected):
        group = [r for r in rows if r["expected"] == expected]
        correct = sum(r["matches"] for r in group)
        return {"correct": correct, "total": len(group),
                "rate": correct / len(group) if group else None}
    return {
        "total": len(rows), "passed": sum(r["matches"] for r in rows),
        "invoke_recall": metric("invoke"), "direct_accuracy": metric("direct"),
        "parse_failures": sum(r["parsed"] is None for r in rows),
        "exit_failures": sum(r["exit"] != 0 for r in rows),
    }


def prepare_output(out):
    out = Path(out)
    if out.is_symlink() or (out.exists() and (not out.is_dir() or any(out.iterdir()))):
        raise ValueError("--out must be a new or empty directory (not a symlink)")
    out.mkdir(parents=True, exist_ok=True)
    return out.resolve()


def select_cases(lang, ids):
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    seen = set()
    for case in cases:
        cid = case["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in seen:
            raise ValueError("unsafe or duplicate case ID")
        seen.add(cid)
        if case["lang"] not in ("zh", "en") or case["expected"] not in ("invoke", "direct"):
            raise ValueError("invalid case language or expected selection")
        if any(not isinstance(case[k], str) or not case[k].strip() for k in ("user_message", "reason")):
            raise ValueError("case message and reason must be nonempty strings")
    cases = [c for c in cases if lang == "all" or c["lang"] == lang]
    if ids:
        wanted = {cid.strip() for cid in ids.split(",")}
        unknown = wanted - {c["id"] for c in cases}
        if unknown:
            raise ValueError("unknown case IDs for selected language: " + ",".join(sorted(unknown)))
        cases = [c for c in cases if c["id"] in wanted]
    if not cases:
        raise ValueError("no cases selected")
    return cases


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--skill", type=Path, default=SKILL)
    ap.add_argument("--lang", choices=("zh", "en", "all"), default="all")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--ids", default="", help="comma-separated case IDs")
    args = ap.parse_args(argv)
    if min(args.workers, args.timeout) < 1:
        ap.error("workers and timeout must be positive")
    try:
        description = read_description(args.skill)
        cases = select_cases(args.lang, args.ids)
        if shutil.which("claude") is None:
            raise ValueError("claude CLI not found; no model calls made")
        out = prepare_output(args.out)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error(str(exc))

    system_file = out / "host_system.md"
    system_file.write_text(host_prompt(description), encoding="utf-8")
    manifest_path = out / "trigger_manifest.json"
    manifest = {
        "status": "in_progress", "model": args.model, "skill": str(args.skill.resolve()),
        "description": description, "lang": args.lang, "workers": args.workers,
        "timeout": args.timeout, "cli_flags": CLI_FLAGS,
        "host_system_sha256": hashlib.sha256(system_file.read_bytes()).hexdigest(),
        "cases": {c["id"]: {"status": "pending", "expected": c["expected"]} for c in cases},
    }
    _runner.atomic_json(manifest_path, manifest)
    with _runner.worker_pool(args.workers) as pool:
        pending = {pool.submit(run_claude, c["user_message"], system_file, args.model, args.timeout): c for c in cases}
        for future in cf.as_completed(pending):
            case = pending[future]
            result = future.result()
            output = out / (case["id"] + ".output.txt")
            output.write_text(result["text"], encoding="utf-8")
            manifest["cases"][case["id"]] = score_result(case, result, output)
            _runner.atomic_json(manifest_path, manifest)
    manifest["summary"] = summarize(manifest["cases"])
    manifest["status"] = "completed"
    _runner.atomic_json(manifest_path, manifest)
    print(json.dumps(manifest["summary"], ensure_ascii=False, indent=2))
    return 0 if manifest["summary"]["passed"] == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
