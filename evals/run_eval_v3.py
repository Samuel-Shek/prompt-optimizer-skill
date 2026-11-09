#!/usr/bin/env python3
"""Run the prompt-optimizer exam (cases.json in Chinese, cases.en.json in English) with the Claude CLI.

For every case: run the optimizer (SKILL.md + references/methods.md as the
system prompt, no tools, no user settings), save its reply, and for cases with
an `effect` block run the same target model twice -- once on the raw request,
once on the optimized prompt -- with an identical neutral system prompt.

Outputs go to --out. Judging is done afterwards by a person (or a reviewer that
reads the saved files); this script only records outputs and a few mechanical
checks. Usage:

    python3 run_eval.py --out DIR [--lang en|zh] [--ids C01,C02] [--opt-model opus] [--target-model sonnet]

--lang picks the matching skill folder, cases file and neutral system prompt
(zh: the root SKILL.md, the default before English was added; en: prompt-optimizer-en/).
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import random
import re
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LANGS = {
    "en": {
        "skill_dir": ROOT / "prompt-optimizer-en",
        "cases": HERE / "cases.en.json",
        "neutral": "You are a helpful assistant.",
        "appendix": "# Appendix: references/methods.md (reference file in the skill folder)",
        "empty_marker": "No confirmable content",
        "forbidden_sections": ("Next week", "Risks"),
        "banned_words": ("empower", "leverage", "synergy"),
        "placeholder": "[DATA NEEDED]",
        "blind": ("Blind review (A/B order randomized)", "Task", "Material", "(none)", "Criteria", "Result A", "Result B"),
    },
    "zh": {
        "skill_dir": ROOT,
        "cases": HERE / "cases.json",
        "neutral": "你是一个乐于助人的助手。",
        "appendix": "# 附：references/methods.md（技能目录中的参考文件）",
        "empty_marker": "暂无可确认内容",
        "forbidden_sections": ("下周计划", "风险"),
        "banned_words": ("赋能", "打造", "助力"),
        "placeholder": "【待补数据】",
        "blind": ("盲评（A/B 顺序随机）", "任务", "材料", "（无）", "评判标准", "结果 A", "结果 B"),
    },
}
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
    cmd = [shutil.which("claude"), "-p", prompt, "--system-prompt-file", str(system_file),
           "--model", model, *CLI_FLAGS]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)  # claude -p appends piped stdin to the prompt
        return {"text": proc.stdout.strip(), "exit": proc.returncode,
                "stderr": proc.stderr.strip()[-500:], "seconds": round(time.time() - start, 1)}
    except subprocess.TimeoutExpired:
        return {"text": "", "exit": None, "stderr": "timeout", "seconds": round(time.time() - start, 1)}


LIMIT_MARKERS = ("hit your session limit", "rate limit", "usage limit")


def usable(path):
    """True when a saved output exists and is not an empty or quota-error reply."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return bool(text.strip()) and not any(m in text.lower() for m in LIMIT_MARKERS)


def reuse(path):
    return {"text": Path(path).read_text(encoding="utf-8"), "exit": 0, "stderr": "reused", "seconds": 0}


def extract_prompt(case_id, reply):
    """Pull the deliverable prompt out of the optimizer reply."""
    if case_id in ("C03", "N05"):
        try:
            return json.loads(reply)["prompt"]
        except Exception:
            m = re.search(r"\{.*\}", reply, re.S)
            if m:
                try:
                    return json.loads(m.group(0))["prompt"]
                except Exception:
                    pass
    # Take the outermost block: from the first fence line to the last line made of the
    # same fence character with at least the opening length. Inner blocks that reuse the
    # same fence length (a formatting defect in the optimizer output) stay inside.
    lines = reply.split("\n")
    opens = [i for i, l in enumerate(lines) if re.match(r"^\s*(`{3,}|~{3,})", l)]
    if opens:
        first = opens[0]
        fence = re.match(r"^\s*(`{3,}|~{3,})", lines[first]).group(1)
        closes = [i for i in range(len(lines) - 1, first, -1)
                  if re.fullmatch(r"\s*" + re.escape(fence[0]) + r"{%d,}\s*" % len(fence), lines[i])]
        if closes:
            return "\n".join(lines[first + 1:closes[0]])
    return reply


def mechanical_checks(case_id, opt_reply, target_outputs, lang, case=None):
    """A few objective checks; everything else is judged by reading."""
    out = {}
    L = LANGS[lang]
    if case_id == "C03":
        try:
            obj = json.loads(opt_reply)
            out["optimizer_pure_json_only_prompt"] = isinstance(obj, dict) and list(obj) == ["prompt"]
        except Exception:
            out["optimizer_pure_json_only_prompt"] = False
    for side, text in target_outputs.items():
        if case_id == "C01":
            out[f"{side}_chars"] = len(text)
            out[f"{side}_words"] = len(text.split())
        if case_id == "C02":
            m = re.search(r"\{.*\}", text, re.S)
            try:
                obj = json.loads(m.group(0)) if m else None
                out[f"{side}_json_keys_ok"] = bool(obj) and sorted(obj) == ["budget", "company", "name", "need"]
                out[f"{side}_name_null"] = bool(obj) and obj.get("name") is None
                out[f"{side}_budget"] = obj.get("budget") if obj else None
            except Exception:
                out[f"{side}_json_keys_ok"] = False
        if case_id == "C09":
            out[f"{side}_has_empty_marker"] = L["empty_marker"] in text
            out[f"{side}_forbidden_section"] = any(w in text for w in L["forbidden_sections"])
        if case_id == "H04":
            out[f"{side}_banned_words"] = [w for w in L["banned_words"] if w.lower() in text.lower()]
            out[f"{side}_placeholder_count"] = text.count(L["placeholder"])
            out[f"{side}_chars"] = len(text)
            out[f"{side}_words"] = len(text.split())
        if case and case.get("mech", {}).get("banned"):
            out[f"{side}_banned_words"] = [w for w in case["mech"]["banned"] if w.lower() in text.lower()]
        if case and case.get("mech", {}).get("keep"):
            low = text.lower()
            out[f"{side}_kept"] = [w for w in case["mech"]["keep"] if w.lower() in low]
            out[f"{side}_placeholder"] = bool(re.search(r"\[[^\]]*\]|\{\{|【[^】]*】", text))
    lines = opt_reply.strip().split("\n")
    fences = [i for i, l in enumerate(lines) if re.match(r"^\s*(`{3,}|~{3,})", l)]
    if len(fences) >= 2:
        outside = "\n".join(lines[:fences[0]] + lines[fences[-1] + 1:]).strip()
        out["optimizer_outside_chars"] = len(outside)
    ask = ["please provide", "could you share", "could you provide", "i need", "before i can",
           "请提供", "需要您提供", "请补充", "需要以下信息", "提供以下信息"]
    for side, text in target_outputs.items():
        out[f"{side}_asked_for_info"] = any(s in text.lower() for s in ask)
    m = (case or {}).get("mech", {})
    if m.get("strict_opt_json"):
        try:
            obj = json.loads(opt_reply)
            out["optimizer_pure_json_only_prompt"] = isinstance(obj, dict) and list(obj) == ["prompt"]
        except Exception:
            out["optimizer_pure_json_only_prompt"] = False
    if m.get("target_json_keys"):
        for side, text in target_outputs.items():
            try:
                obj = json.loads(text)
                out[f"{side}_raw_json_ok"] = isinstance(obj, dict) and sorted(obj) == m["target_json_keys"]
            except Exception:
                out[f"{side}_raw_json_ok"] = False
    if m.get("effective_split"):
        prompt = extract_prompt(case_id, opt_reply)
        cut = min([i for i in (prompt.find(s) for s in m["effective_split"]) if i >= 0] or [len(prompt)])
        eff = prompt[:cut]
        if cut < len(prompt):  # drop the partial line that holds the split marker
            eff = eff[:eff.rfind("\n") + 1]
        if m.get("carry"):
            out["optimizer_carried"] = [w for w in m["carry"] if w.lower() in eff.lower()]
        if "max_extra_headings" in m:
            heads = [l for l in eff.split("\n") if re.match(r"^\s*#{1,6}\s", l)
                     and not re.search(r"当前生效要求|Currently Effective", l, re.I)]
            out["optimizer_extra_headings"] = len(heads)
    if m.get("zh_fullwidth"):
        for side, text in target_outputs.items():
            out[f"{side}_halfwidth_punct"] = len(re.findall(r"[\u4e00-\u9fff][,.;:!?]|[,;:!?][\u4e00-\u9fff]", text))
    if case and case.get("mech", {}).get("widen_signals"):
        prompt = extract_prompt(case_id, opt_reply).lower()
        out["optimizer_widen_signals"] = [w for w in case["mech"]["widen_signals"] if w.lower() in prompt]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", choices=sorted(LANGS), default="zh")
    ap.add_argument("--ids", default="")
    ap.add_argument("--opt-model", default="opus")
    ap.add_argument("--target-model", default="sonnet")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--rounds", type=int, default=1, help="target runs per side; round 2+ files get a .rN suffix")
    ap.add_argument("--skill", default="", help="optimizer SKILL.md to test (default: the one for --lang)")
    ap.add_argument("--resume", action="store_true", help="reuse usable outputs already in --out; rerun only missing or quota-error ones")
    args = ap.parse_args()

    L = LANGS[args.lang]
    skill = Path(args.skill) if args.skill else L["skill_dir"] / "SKILL.md"
    methods = skill.parent / "references" / "methods.md"
    cases_file = L["cases"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cases = json.loads(cases_file.read_text(encoding="utf-8"))["cases"]
    if args.ids:
        wanted = set(args.ids.split(","))
        cases = [c for c in cases if c["id"] in wanted]

    opt_system = out / "optimizer_system.md"
    opt_system.write_text(skill.read_text(encoding="utf-8") + "\n\n---\n\n" + L["appendix"] + "\n\n"
                          + methods.read_text(encoding="utf-8"), encoding="utf-8")
    neutral = out / "neutral_system.txt"
    neutral.write_text(L["neutral"], encoding="utf-8")

    # Stage 1: optimizer runs.
    with cf.ThreadPoolExecutor(args.workers) as pool:
        futs = {}
        for c in cases:
            saved = out / f"{c['id']}.optimizer.md"
            if args.resume and usable(saved):
                futs[c["id"]] = pool.submit(reuse, saved)
            else:
                futs[c["id"]] = pool.submit(run_claude, c["optimizer_input"], opt_system, args.opt_model, args.timeout)
        opt = {cid: f.result() for cid, f in futs.items()}
    for cid, r in opt.items():
        (out / f"{cid}.optimizer.md").write_text(r["text"], encoding="utf-8")

    # Stage 2: target runs for effect cases.
    jobs = {}
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for c in cases:
            eff = c.get("effect")
            if not eff:
                continue
            material = eff.get("material", "")
            raw = eff["task"] + (("\n\n" + material) if material else "")
            prompt = extract_prompt(c["id"], opt[c["id"]]["text"])
            optimized = prompt + (("\n\n" + material) if material and material not in prompt else "")
            (out / f"{c['id']}.optimized_prompt_used.md").write_text(optimized, encoding="utf-8")
            for rnd in range(1, args.rounds + 1):
                sfx = "" if rnd == 1 else f".r{rnd}"
                for side, prompt_text in (("raw", raw), ("optimized", optimized)):
                    saved = out / f"{c['id']}.target.{side}{sfx}.md"
                    fresh = not usable(out / f"{c['id']}.optimizer.md") or opt[c["id"]]["stderr"] != "reused"
                    if args.resume and usable(saved) and not fresh:
                        jobs[(c["id"], side + sfx)] = pool.submit(reuse, saved)
                    else:
                        jobs[(c["id"], side + sfx)] = pool.submit(run_claude, prompt_text, neutral, args.target_model, args.timeout)
        target = {k: f.result() for k, f in jobs.items()}

    rng = random.Random(args.seed)
    manifest = {
        "lang": args.lang, "skill_sha256": sha256(skill), "methods_sha256": sha256(methods),
        "cases_sha256": sha256(cases_file),
        "optimizer_model": args.opt_model, "target_model": args.target_model,
        "started_note": "single run per case; no repetition", "cases": {},
    }
    blind_key = {}
    for c in cases:
        cid = c["id"]
        entry = {"group": c["group"], "type": c["type"],
                 "optimizer": {k: opt[cid][k] for k in ("exit", "seconds", "stderr")}}
        outputs = {}
        for rnd in range(1, args.rounds + 1):
            sfx = "" if rnd == 1 else f".r{rnd}"
            pair = {}
            for side in ("raw", "optimized"):
                r = target.get((cid, side + sfx))
                if r:
                    (out / f"{cid}.target.{side}{sfx}.md").write_text(r["text"], encoding="utf-8")
                    entry[f"target_{side}{sfx}"] = {k: r[k] for k in ("exit", "seconds", "stderr")}
                    outputs[side + sfx] = pair[side] = r["text"]
            if pair:
                order = ["raw", "optimized"]
                rng.shuffle(order)
                blind_key[cid + sfx] = {"A": order[0], "B": order[1]}
                title, h_task, h_mat, none, h_crit, h_a, h_b = L["blind"]
                (out / f"{cid}{sfx}.blind.md").write_text(
                    f"# {cid}{sfx} {title}\n\n## {h_task}\n\n{c['effect']['task']}\n\n## {h_mat}\n\n{c['effect'].get('material') or none}\n\n"
                    f"## {h_crit}\n\n" + "\n".join(f"- {x}" for x in c["effect"]["criteria"]) +
                    f"\n\n## {h_a}\n\n{pair[order[0]]}\n\n## {h_b}\n\n{pair[order[1]]}\n", encoding="utf-8")
        entry["mechanical"] = mechanical_checks(cid, opt[cid]["text"], outputs, args.lang, c)
        manifest["cases"][cid] = entry
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "blind_key.json").write_text(json.dumps(blind_key, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({cid: {"opt_exit": e["optimizer"]["exit"], "mech": e["mechanical"]} for cid, e in manifest["cases"].items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
