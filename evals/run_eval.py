#!/usr/bin/env python3
"""Run the prompt-optimizer exam (cases.json) with the Claude CLI.

For every case: run the optimizer (SKILL.md + references/methods.md as the
system prompt, no tools, no user settings), save its reply, and for cases with
an `effect` block run the same target model twice -- once on the raw request,
once on the optimized prompt -- in user-baseline mode with an identical neutral
system prompt. Optional system-deployment mode uses system/system for declared
deployment cases, with identical material as user input; report it separately.

Outputs go to --out. Judging is done afterwards by a person (or a reviewer that
reads the saved files); this script only records outputs and a few mechanical
checks. Usage:

    python3 run_eval.py --out DIR [--ids C01,C02] [--opt-model opus] [--target-model sonnet]
"""
import argparse
import concurrent.futures as cf
from contextlib import contextmanager
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / "SKILL.md"
METHODS = HERE.parent / "references" / "methods.md"
NEUTRAL_SYSTEM = "你是一个乐于助人的助手。"
CLI_FLAGS = [
    "--tools", "",
    "--setting-sources", "",
    "--disable-slash-commands",
    "--no-session-persistence",
    "--strict-mcp-config",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_claude(prompt, system_file, model, timeout):
    executable = shutil.which("claude")
    if executable is None:
        return {"text": "", "exit": 127, "stderr": "claude CLI not found", "seconds": 0}
    cmd = [executable, "-p", "--system-prompt-file", str(system_file),
           "--model", model, *CLI_FLAGS, "--", prompt]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout,
                              stdin=subprocess.DEVNULL)  # claude -p appends piped stdin to the prompt
        return {"text": proc.stdout.strip(), "exit": proc.returncode,
                "stderr": proc.stderr.strip()[-500:], "seconds": round(time.time() - start, 1)}
    except subprocess.TimeoutExpired:
        return {"text": "", "exit": None, "stderr": "timeout", "seconds": round(time.time() - start, 1)}
    except OSError as exc:
        return {"text": "", "exit": 127, "stderr": str(exc)[-500:], "seconds": round(time.time() - start, 1)}
    except UnicodeError:
        return {"text": "", "exit": 1, "stderr": "invalid UTF-8 CLI output", "seconds": round(time.time() - start, 1)}


LIMIT_MARKERS = ("hit your session limit", "rate limit", "usage limit")


def usable_text(text):
    value = text.strip().lower()
    # Reject standalone notices / explicit errors, not ordinary discussion of quotas.
    notice = value.rstrip(".!。！") in LIMIT_MARKERS
    error = re.match(r"^(?:(?:api\s+)?error:\s*(?:rate|usage|session) limit\b|(?:claude ai )?(?:rate|usage|session) limit (?:exceeded|reached)\b|(?:you(?:'ve| have) )?hit your (?:session|usage) limit\b)", value)
    return bool(value) and not (notice or error)


def usable(path):
    """True when a saved output exists and is not an empty or quota-error reply."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return usable_text(text)


def strict_opt_json(case):
    return case.get("mech", {}).get("strict_opt_json", False) or case["id"] == "C03"


def extract_prompt(case, reply):
    """Pull the deliverable prompt out of the optimizer reply."""
    if strict_opt_json(case) or reply.lstrip().startswith("{"):
        try:
            obj = json.loads(reply)
            if isinstance(obj, dict) and list(obj) == ["prompt"] and isinstance(obj["prompt"], str) and obj["prompt"].strip():
                return obj["prompt"]
        except (ValueError, TypeError):
            pass
        if strict_opt_json(case):
            raise ValueError("optimizer_format_failed: expected pure JSON with only a nonempty string prompt")
    # One top-level fenced deliverable only; shorter inner fences remain verbatim.
    lines = reply.split("\n")
    opens = [i for i, l in enumerate(lines) if re.match(r"^\s*(`{3,}|~{3,})", l)]
    if opens:
        first = opens[0]
        fence = re.match(r"^\s*(`{3,}|~{3,})", lines[first]).group(1)
        closes = [i for i in range(first + 1, len(lines))
                  if re.fullmatch(r"\s*" + re.escape(fence[0]) + r"{%d,}\s*" % len(fence), lines[i])]
        if closes:
            if any(i > closes[0] for i in opens):
                raise ValueError("multi_block: ambiguous optimizer deliverable")
            return "\n".join(lines[first + 1:closes[0]])
        raise ValueError("optimizer_format_failed: unclosed code fence")
    return reply


def mechanical_checks(case, opt_reply, target_outputs):
    """A few objective checks; everything else is judged by reading."""
    out = {}
    case_id = case["id"]
    mech = case.get("mech", {})
    try:
        prompt = extract_prompt(case, opt_reply)
    except ValueError:
        prompt = ""
    if strict_opt_json(case):
        try:
            obj = json.loads(opt_reply)
            out["optimizer_pure_json_only_prompt"] = (isinstance(obj, dict) and list(obj) == ["prompt"]
                and isinstance(obj["prompt"], str) and bool(obj["prompt"].strip()))
        except (ValueError, TypeError):
            out["optimizer_pure_json_only_prompt"] = False
    for key in ("keep", "carry"):
        if key in mech:
            out[f"optimizer_{key}_missing"] = [s for s in mech[key] if s not in prompt]
    if "widen_signals" in mech:
        out["optimizer_widen_signals"] = [s for s in mech["widen_signals"] if s in prompt]
    if "max_extra_headings" in mech:
        count = len(re.findall(r"^\s{0,3}#{1,6}\s+", prompt, re.M))
        out["optimizer_extra_headings"] = count
        out["optimizer_extra_headings_ok"] = count <= mech["max_extra_headings"]
    if "effective_split" in mech:
        out["effective_split_status"] = "not_implemented: historical semantics unknown"
    for side, text in target_outputs.items():
        for key in ("banned", "ask_signals"):
            if key in mech:
                out[f"{side}_{key}"] = [s for s in mech[key] if s in text]
        if "keep" in mech:
            out[f"{side}_keep_missing"] = [s for s in mech["keep"] if s not in text]
        if "target_json_keys" in mech:
            try:
                obj = json.loads(text)
                out[f"{side}_json_keys_ok"] = isinstance(obj, dict) and sorted(obj) == sorted(mech["target_json_keys"])
            except (ValueError, TypeError):
                out[f"{side}_json_keys_ok"] = False
        if mech.get("zh_fullwidth"):
            out[f"{side}_halfwidth_punctuation_signals"] = sorted(set(re.findall(r"[,;:!?()]", text)))
        if case_id == "C01":
            out[f"{side}_chars"] = len(text)
        if case_id == "C02":
            try:
                obj = json.loads(text)
                out[f"{side}_json_keys_ok"] = isinstance(obj, dict) and sorted(obj) == ["budget", "company", "name", "need"]
                out[f"{side}_name_null"] = isinstance(obj, dict) and "name" in obj and obj["name"] is None
                out[f"{side}_budget"] = obj.get("budget") if isinstance(obj, dict) else None
            except (ValueError, TypeError):
                out[f"{side}_json_keys_ok"] = False
        if case_id == "C09":
            out[f"{side}_has_empty_marker"] = "暂无可确认内容" in text
            out[f"{side}_forbidden_section"] = any(w in text for w in ("下周计划", "风险"))
        if case_id == "H04":
            out[f"{side}_banned_words"] = [w for w in ("赋能", "打造", "助力") if w in text]
            out[f"{side}_placeholder_count"] = text.count("【待补数据】")
            out[f"{side}_chars"] = len(text)
    return out


def successful(result):
    return result["exit"] == 0 and usable_text(result["text"])


def result_meta(result):
    return {**{k: result[k] for k in ("exit", "seconds", "stderr")},
            "sha256": hashlib.sha256(result["text"].encode("utf-8")).hexdigest(),
            "usable": successful(result), "reused": result.get("reused", False)}


def cached_result(path, meta):
    # Text alone does not prove a successful run, or that it belongs to this run.
    if meta and meta.get("exit") == 0 and meta.get("usable") and usable(path) and sha256(path) == meta.get("sha256"):
        return {"text": path.read_text(encoding="utf-8"), "exit": 0,
                "stderr": meta["stderr"], "seconds": meta["seconds"], "reused": True}
    return None


def prepare_effect(case, prompt, mode):
    eff = case["effect"]
    material = eff.get("material", "")
    swap = eff.get("swap_material")
    if swap:
        old = swap["from"]
        if not old or swap["to"] != material or prompt.count(old) != 1 or (material and material in prompt):
            raise ValueError("verbatim_fail: material replacement is not unique and exact")
        prompt = prompt.replace(old, material, 1)
        if any(token in prompt for token in swap.get("residual_forbidden", [])):
            raise ValueError("verbatim_fail: residual example reference")
    role = "system" if mode == "system-deployment" and eff.get("deployment_role") == "system" else "user"
    raw = eff["task"]
    optimized = prompt
    if role == "user":
        raw += ("\n\n" + material) if material else ""
        if material and material not in optimized:
            optimized += "\n\n" + material
    elif material and material in optimized:
        # Deployment requires material in user only; avoid a hidden duplicate.
        if optimized.count(material) != 1:
            raise ValueError("verbatim_fail: deployment material is duplicated")
        optimized = optimized.replace(material, "", 1)
    return {"role": role, "raw": raw, "optimized": optimized, "material": material,
            "material_swapped": bool(swap)}


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
    temporary.replace(path)


@contextmanager
def worker_pool(workers):
    pool = cf.ThreadPoolExecutor(workers)
    try:
        yield pool
    except BaseException:
        # Already-running subprocesses may finish; prevent queued calls from starting.
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)


def derived_paths(out, cid, rounds):
    paths = [out / f"{cid}.optimized_prompt_used.md"]
    paths.extend(out / f"{cid}.{side}.system.md" for side in ("raw", "optimized"))
    for rnd in range(1, rounds + 1):
        sfx = "" if rnd == 1 else f".r{rnd}"
        paths.append(out / f"{cid}{sfx}.blind.md")
        paths.extend(out / f"{cid}.target.{side}{sfx}.md" for side in ("raw", "optimized"))
    return paths


def quarantine(out, paths, reason):
    existing = [p for p in paths if p.exists()]
    if not existing:
        return []
    stale = out / "stale"
    stale.mkdir(exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="derived-", dir=stale))
    records = []
    for path in existing:
        destination = folder / path.name
        path.replace(destination)
        records.append({"source": str(path.relative_to(out)),
                        "path": str(destination.relative_to(out)), "reason": reason})
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--opt-model", default="opus")
    ap.add_argument("--target-model", default="sonnet")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--rounds", type=int, default=1, help="target runs per side; optimizer runs once; round 2+ files get a .rN suffix")
    ap.add_argument("--skill", default=str(SKILL), help="optimizer SKILL.md to test")
    ap.add_argument("--methods", help="default: references/methods.md beside selected SKILL.md")
    ap.add_argument("--effect-mode", choices=("user-baseline", "system-deployment"), default="user-baseline")
    ap.add_argument("--resume", action="store_true", help="reuse only successful hash-verified outputs from the same sources and configuration")
    args = ap.parse_args()
    if min(args.rounds, args.workers, args.timeout) < 1:
        ap.error("rounds, workers and timeout must be positive")

    out = Path(args.out)
    skill = Path(args.skill)
    methods = Path(args.methods) if args.methods else skill.parent / "references" / "methods.md"
    sources = {"skill": skill, "methods": methods, "cases": HERE / "cases.json", "runner": Path(__file__)}
    source_bytes = {key: path.read_bytes() for key, path in sources.items()}
    cases = json.loads(source_bytes["cases"])["cases"]
    if args.ids:
        wanted = set(args.ids.split(","))
        unknown = wanted - {c["id"] for c in cases}
        if unknown:
            ap.error("unknown case IDs: " + ",".join(sorted(unknown)))
        cases = [c for c in cases if c["id"] in wanted]
    if not cases:
        ap.error("no cases selected")
    contract = {
        **{key + "_sha256": hashlib.sha256(data).hexdigest() for key, data in source_bytes.items()},
        "optimizer_model": args.opt_model, "target_model": args.target_model,
        "case_ids": [c["id"] for c in cases], "rounds": args.rounds, "optimizer_rounds": 1,
        "effect_mode": args.effect_mode, "seed": args.seed,
        "cli_flags": CLI_FLAGS, "neutral_system": NEUTRAL_SYSTEM,
        "methods_loading": "always_appended; differs from on-demand production loading",
    }
    previous = {}
    if args.resume:
        try:
            old = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            ap.error("resume refused: manifest missing or invalid; preserve this directory and use a new empty --out")
        if old.get("resume_contract") != contract:
            ap.error("resume refused: source/configuration mismatch or legacy manifest; use a new output directory")
        previous = old["cases"]
    elif out.exists() and any(out.iterdir()):
        ap.error("output directory is not empty; use --resume or a new directory")
    if shutil.which("claude") is None:
        ap.error("claude CLI not found; no model calls made")

    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        **{k: v for k, v in contract.items() if k.endswith("sha256") or k.endswith("_model")},
        "resume_contract": contract, "status": "in_progress", "phase": "optimizer",
        "started_note": f"one optimizer sample per case; {args.rounds} target run(s) per side per effect case; verified outputs may be reused",
        "evaluation_scope": "mechanical observations and review artifacts only; no automatic semantic quality or net-benefit judgment",
        "blind_note": "reproducible per-pair A/B shuffle only; give reviewers only *.blind.md, not this directory or blind_key.json",
        "cases": {c["id"]: {"group": c["group"], "type": c["type"], "status": "pending",
                            "valid_pairs": [], "isolated_artifacts": []} for c in cases},
    }
    atomic_json(out / "manifest.json", manifest)
    atomic_json(out / "blind_key.json", {})

    def isolate(cid, paths, reason):
        records = quarantine(out, paths, reason)
        manifest["cases"][cid]["isolated_artifacts"].extend(records)
        if records:
            atomic_json(out / "manifest.json", manifest)

    def remember(cid, key, result, path):
        path.write_text(result["text"], encoding="utf-8")
        manifest["cases"][cid][key] = result_meta(result)
        atomic_json(out / "manifest.json", manifest)

    opt_system = out / "optimizer_system.md"
    opt_system.write_text(source_bytes["skill"].decode("utf-8") + "\n\n---\n\n# 附：references/methods.md（技能目录中的参考文件）\n\n"
                          + source_bytes["methods"].decode("utf-8"), encoding="utf-8")
    neutral = out / "neutral_system.txt"
    neutral.write_text(NEUTRAL_SYSTEM, encoding="utf-8")

    # Stage 1: one optimizer sample per case, including on --rounds > 1.
    with worker_pool(args.workers) as pool:
        futs = {}
        opt = {}
        for c in cases:
            cid = c["id"]
            cached = cached_result(out / f"{cid}.optimizer.md", previous.get(cid, {}).get("optimizer"))
            if cached:
                opt[cid] = cached
                remember(cid, "optimizer", cached, out / f"{cid}.optimizer.md")
            else:
                isolate(cid, derived_paths(out, cid, args.rounds), "optimizer_rerun")
                futs[cid] = pool.submit(run_claude, c["optimizer_input"], opt_system, args.opt_model, args.timeout)
        for cid, future in futs.items():
            opt[cid] = future.result()
            remember(cid, "optimizer", opt[cid], out / f"{cid}.optimizer.md")

    manifest["phase"] = "target"
    atomic_json(out / "manifest.json", manifest)

    # Stage 2: a failed optimizer or unsafe material swap cannot create a pair.
    jobs, target, prepared, skipped = {}, {}, {}, {}
    with worker_pool(args.workers) as pool:
        for c in cases:
            cid = c["id"]
            if not successful(opt[cid]):
                skipped[cid] = "optimizer_failed"
                isolate(cid, derived_paths(out, cid, args.rounds), skipped[cid])
                continue
            if not c.get("effect") and not c.get("mech"):
                continue  # No extracted prompt is consumed by this case's checks.
            try:
                prompt = extract_prompt(c, opt[cid]["text"])
                if not prompt.strip():
                    raise ValueError("optimizer_format_failed: empty prompt")
                if not c.get("effect"):
                    continue
                inputs = prepared[cid] = prepare_effect(c, prompt, args.effect_mode)
            except ValueError as exc:
                skipped[cid] = str(exc)
                isolate(cid, derived_paths(out, cid, args.rounds), skipped[cid])
                continue
            (out / f"{cid}.optimized_prompt_used.md").write_text(inputs["optimized"], encoding="utf-8")
            systems = {}
            for side in ("raw", "optimized"):
                if inputs["role"] == "system":
                    systems[side] = out / f"{cid}.{side}.system.md"
                    systems[side].write_text(inputs[side], encoding="utf-8")
                else:
                    systems[side] = neutral
            for rnd in range(1, args.rounds + 1):
                sfx = "" if rnd == 1 else f".r{rnd}"
                for side in ("raw", "optimized"):
                    saved = out / f"{cid}.target.{side}{sfx}.md"
                    meta = previous.get(cid, {}).get(f"target_{side}{sfx}")
                    cached = cached_result(saved, meta) if opt[cid].get("reused") else None
                    key = (cid, side + sfx)
                    if cached:
                        target[key] = cached
                        remember(cid, f"target_{side}{sfx}", cached, saved)
                    else:
                        isolate(cid, [saved, out / f"{cid}{sfx}.blind.md"], "target_rerun")
                        user_text = inputs["material"] if inputs["role"] == "system" else inputs[side]
                        jobs[key] = pool.submit(run_claude, user_text, systems[side], args.target_model, args.timeout)
        for key, future in jobs.items():
            target[key] = future.result()
            cid, side = key
            remember(cid, f"target_{side}", target[key], out / f"{cid}.target.{side}.md")
    blind_key = {}
    errors = bool(skipped)
    for c in cases:
        cid = c["id"]
        entry = {"group": c["group"], "type": c["type"], "optimizer": result_meta(opt[cid]),
                 "status": skipped.get(cid, "completed"), "valid_pairs": [],
                 "isolated_artifacts": manifest["cases"][cid]["isolated_artifacts"]}
        if cid in prepared:
            inputs = prepared[cid]
            entry["effect"] = {"mode": args.effect_mode, "raw_role": inputs["role"], "optimized_role": inputs["role"],
                "baseline_note": c["effect"].get("baseline_note", "existing effect.task user baseline"),
                "material_swapped": inputs["material_swapped"],
                "input_chars": {k: len(inputs[k]) for k in ("raw", "optimized", "material")}}
        outputs = {}
        for rnd in range(1, args.rounds + 1):
            sfx = "" if rnd == 1 else f".r{rnd}"
            pair = {}
            for side in ("raw", "optimized"):
                result = target.get((cid, side + sfx))
                if result is not None:
                    (out / f"{cid}.target.{side}{sfx}.md").write_text(result["text"], encoding="utf-8")
                    entry[f"target_{side}{sfx}"] = result_meta(result)
                    if successful(result):
                        outputs[side + sfx] = pair[side] = result["text"]
                    else:
                        entry["status"] = "target_failed"
                        errors = True
            if len(pair) == 2:
                entry["valid_pairs"].append(rnd)
                order = ["raw", "optimized"]
                random.Random(f"{args.seed}:{cid}{sfx}").shuffle(order)
                blind_key[cid + sfx] = {"A": order[0], "B": order[1]}
                role = prepared[cid]["role"]
                (out / f"{cid}{sfx}.blind.md").write_text(
                    f"# {cid}{sfx} A/B 待评（{args.effect_mode}，双方 {role} 角色；非自动评分）\n\n## 任务\n\n{c['effect']['task']}\n\n## 材料\n\n{c['effect'].get('material') or '（无）'}\n\n"
                    f"## 评判标准\n\n" + "\n".join(f"- {x}" for x in c["effect"]["criteria"]) +
                    f"\n\n## 结果 A\n\n{pair[order[0]]}\n\n## 结果 B\n\n{pair[order[1]]}\n", encoding="utf-8")
            elif c.get("effect"):
                # Replaces any stale generated pair on resume with an explicit invalid marker.
                (out / f"{cid}{sfx}.blind.md").write_text("本轮无有效对照；原因见 manifest.json。\n", encoding="utf-8")
        entry["mechanical"] = mechanical_checks(c, opt[cid]["text"], outputs) if successful(opt[cid]) else {}
        entry["mechanical_status"] = "recorded; signal hits require review" if successful(opt[cid]) else "skipped: optimizer_failed"
        entry["target_checks_recorded_for"] = list(outputs)
        manifest["cases"][cid] = entry
    manifest["status"] = "error" if errors else "completed"
    manifest["phase"] = "finished"
    atomic_json(out / "blind_key.json", blind_key)
    atomic_json(out / "manifest.json", manifest)
    print(json.dumps({cid: {"status": e["status"], "valid_pairs": e["valid_pairs"], "mech": e["mechanical"]} for cid, e in manifest["cases"].items()}, ensure_ascii=False, indent=1))
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f"evaluation error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("interrupted; resume with the same arguments and --resume", file=sys.stderr)
        sys.exit(130)
