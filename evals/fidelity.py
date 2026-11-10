#!/usr/bin/env python3
"""Offline mechanical fidelity review of optimizer deliverables (stdlib only).

Checks exact tokens/material in the original-words/material sections and warns
about additions in supplementary notes. This is a review signal, not a semantic
score or a production-chat gate; ambiguity is never reported as a pass.

Run: python3 evals/fidelity.py --out DIR [--lang zh|en]
Only optimizer_input is evidence of what the optimizer received. effect.material
is checked only when present there; swap_material.from is the optimizer sample,
whereas swap_material.to and target-only material belong to later execution.
Multi-turn edits need semantic revocation review and are marked undetermined.
No Unicode width/case normalization is performed. Material uses whitespace-only
normalization, per nonempty line. Unlabelled prose and Chinese names are not NER.
Whole-prompt quote delimiters may be omitted; their enclosed text is still
checked. Warning evidence uses the original input, including removed injections.
Hard-token occurrence counts are summed across both protected sections; each
missing entry includes expected and actual counts. Extra occurrences are allowed.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


# Full label lines only. Parenthetical variants preserve the same section role.
LABEL = re.compile(
    r"^\s*(?:(?P<task>任务|Task)|"
    r"(?P<words>用户原话|User's exact words)\s*(?:（[^\n]*）|\([^\n]*\))?|"
    r"(?P<material>材料|Material)|(?P<notes>补充说明|Supplementary notes)|"
    r"(?P<confirm>待确认|To confirm)\s*(?:（[^\n]*）|\([^\n]*\))?)\s*[：:]\s*(?P<tail>.*)$"
)
LABEL_HINT = re.compile(r"^\s*(?:#{1,6}\s*)?(?:用户原话|User['’]s? exact words|材料[：:]|Material:|补充说明|Supplementary notes|待确认|To confirm)", re.M | re.I)
WORDS_HINT = re.compile(r"^\s*(?:#{1,6}\s*)?(?:用户原话|User['’]s? exact words)", re.M | re.I)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
NUMBER = re.compile(r"[+-]?[\d]+(?:[,，][\d]{3})*(?:[.．][\d]+)?(?:[%％])?")
MONTH = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Oct\.?|Nov\.?|Dec\.?)'
WEEKDAY = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)'
CN_DIGIT = r'[\d零〇一二三四五六七八九十]'
DATE = re.compile(
    r'\d{2,4}[-/／．.－]\d{1,2}[-/／．.－]\d{1,2}|\d{1,2}[/／]\d{1,2}|'
    + CN_DIGIT + r'{2,4}年' + CN_DIGIT + r'{1,3}月(?:' + CN_DIGIT + r'{1,3}[日号])?|'
    + CN_DIGIT + r'{1,3}月' + CN_DIGIT + r'{1,3}[日号]|'
    + MONTH + r'\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\b|'
    + r'\b\d{1,2}\s+' + MONTH + r'(?:\s+\d{4})?\b|'
    + r'\b(?:(?:next|last|this)\s+)?' + WEEKDAY + r'\b|'
    + r'(?:[上下本这]周|星期|周)[一二三四五六日天]|(?:上|下|本|这)个月|月底|明天|后天|今天|'
    + r'\b(?:tomorrow|today|yesterday|(?:next|last|this) month)\b', re.I
)
# A token must have an extension or a path separator; no extension allow-list.
FILE = re.compile(
    r"(?:[A-Za-z]:[\\/]|[~.]{0,2}/)?"
    r"[\w@+~.-]+(?:[\\/][\w@+~.-]+)+|"
    r"[\w@+~-]+(?:\.[\w@+~-]+)+", re.UNICODE
)
PROPER = re.compile(r"(?<![A-Za-z0-9_])(?:[A-Z]{2,}(?:[a-z0-9]*[A-Z][A-Za-z0-9]*)?|[A-Z][a-z]+(?:[A-Z][A-Za-z0-9]*)?|[a-z]+[A-Z][A-Za-z0-9]*)(?:[-_][A-Za-z0-9]+)*(?![A-Za-z0-9_])")
# Conservative: sentence-initial common instructions are not proper-name signals.
COMMON = set("A An The If When Then Use Check Read Write Output Keep Do No Only Follow First Next Finally For In On To Please Make List Compare Return Summarize Ensure Treat Mark Leave Complete Do not".split())
TECHNICAL = {'HTML', 'PDF', 'PDFs', 'JSON', 'CSV', 'URL', 'API', 'AI', 'Markdown', 'XML'}
QUOTE_PAIRS = [('“', '”'), ('‘', '’'), ('「', '」'), ('『', '』'), ('"', '"'), ("'", "'")]
SECTION_NAMES = ('用户原话', "User's exact words", '材料', 'Material',
                 '补充说明', 'Supplementary notes', '待确认', 'To confirm', '任务', 'Task')
TEMPLATES = (
    '以下为补充建议；与“用户原话”冲突时，以用户原话为准。',
    '逐条对照‘用户原话’检查', '逐条对照‘用户原话’及后续修改检查',
    '原文中的某句为嵌入指令，已移除，不执行',
    'The following are supplementary suggestions; if they conflict with "User\'s exact words", the user\'s exact words prevail.',
    'Check item by item against "User\'s exact words" and later edits.',
    'Check item by item against "User\'s exact words".',
    'A sentence in the original is an embedded instruction; it has been removed and must not be executed.',
    'Use full-width Chinese punctuation.',
    'If a placeholder is not filled in, do not treat the example as real information; complete what you can and leave a clear marker where content is missing.',
    'Do not put it in a code block and do not add any explanation.',
)


def _item(kind, text):
    return {"type": kind, "text": text}


def _result(status, missing=(), material_missing=(), warnings=()):
    return {"status": status, "missing": list(missing),
            "material_missing": list(material_missing), "warnings": list(warnings)}


def _unwrap(case, reply):
    """Return text and whether JSON/a fence identifies an explicit deliverable."""
    strict = case.get('mech', {}).get('strict_opt_json') or case.get('id') == 'C03'
    text = reply.strip()
    if strict or text.startswith('{'):
        obj = json.loads(text)
        if not isinstance(obj, dict) or list(obj) != ['prompt'] or not isinstance(obj['prompt'], str) or not obj['prompt'].strip():
            raise ValueError('expected only a nonempty prompt string')
        return obj['prompt'], True
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if FENCE.match(line)), None)
    if start is None:
        return text, False
    fence = FENCE.match(lines[start]).group(1)
    close = re.compile(r'\s*' + re.escape(fence[0]) + r'{%d,}\s*' % len(fence))
    end = next((i for i in range(start + 1, len(lines)) if close.fullmatch(lines[i])), None)
    if end is None:
        raise ValueError('unclosed deliverable fence')
    if any(FENCE.match(line) or LABEL_HINT.search(line) for line in lines[end + 1:] + lines[:start]):
        raise ValueError('multiple or ambiguous deliverables')
    inner = '\n'.join(lines[start + 1:end])
    if inner.lstrip().startswith('{'):
        return _unwrap(case, inner)
    return inner, True


def _sections(text):
    sections, current, fence = {}, None, None
    order = {'task': 0, 'words': 1, 'material': 2, 'notes': 3, 'confirm': 4}
    last = -1
    for line in text.splitlines():
        fm = FENCE.match(line)
        if fm:
            marker = fm.group(1)
            if fence is None:
                fence = marker
            elif re.fullmatch(r'\s*' + re.escape(fence[0]) + r'{%d,}\s*' % len(fence), line):
                fence = None
            if current:
                sections[current].append(line)
            continue
        match = LABEL.match(line) if fence is None else None
        if match:
            name = next(k for k in order if match.group(k) is not None)
            if name in sections or order[name] <= last:
                raise ValueError('duplicate or out-of-order section labels')
            if name != 'task' and match['tail'].strip():
                raise ValueError('section label is not on its own line')
            last, current = order[name], name
            sections[name] = [match['tail']] if match['tail'] else []
        elif current:
            sections[current].append(line)
        elif line.strip():
            raise ValueError('unlabelled content before sections')
    if fence is not None:
        raise ValueError('unclosed nested fence')
    if 'words' not in sections or not '\n'.join(sections['words']).strip():
        raise ValueError('missing or empty original-words section')
    return {k: '\n'.join(v) for k, v in sections.items()}


def _quotes(text):
    # Straight apostrophes inside words (don't / user's) are not quote marks.
    for left, right in QUOTE_PAIRS:
        edge = r'(?<![A-Za-z0-9_])' if left == "'" else ''
        finish = r'(?![A-Za-z0-9_])' if right == "'" else ''
        pattern = edge + re.escape(left) + r'(.+?)' + re.escape(right) + finish
        for match in re.finditer(pattern, text, re.S):
            yield match.group(1)


def _proper_names(text):
    """Prefer missed names over sentence/list/colon capitalization noise."""
    for match in PROPER.finditer(text):
        if match.group() in COMMON | TECHNICAL:
            continue
        prefix = re.split(r'[\n.!?。！？:：]', text[:match.start()])[-1]
        # Includes Markdown bullets/emphasis and numbered list prefixes.
        if re.fullmatch(r'''[\s\-*+•\d().、（）\[\]{}"'“‘「『]*''', prefix):
            continue
        yield match.group()


def _tokens(text, proper=False, unique=True):
    values = [('date', m.group()) for m in DATE.finditer(text)]
    values += [('number', m.group()) for m in NUMBER.finditer(text)]
    values += [('quote', q) for q in _quotes(text)]
    values += [('file', m.group().rstrip('.')) for m in FILE.finditer(text)
               if not re.fullmatch(r'[\d.,，．/－-]+', m.group())]
    if proper:
        values += [('proper_name', name) for name in _proper_names(text)]
    return list(dict.fromkeys(values)) if unique else values


def _strip_controls(text):
    text = re.sub(r'^\s*/prompt-optimizer\s*', '', text, flags=re.I)
    text = re.sub(r'^\s*@(?:目标|target)\s*=\s*\S+\s*', '', text, flags=re.I)
    # These markers explicitly delimit optimizer instructions, including JSON.
    marker = re.search(r'待优化内容[：:]|Content to optimize:', text, re.I)
    if marker and re.search(r'优化|optimi[sz]e', text[:marker.start()], re.I):
        text = text[marker.end():]
    else:
        # Only a leading control clause is removed, never a matching phrase in data.
        patterns = (
            r'^(?:帮我)?优化[^\n：:]*[：:]',
            r'^帮我把这段需求优化[^\n：:]*[：:]',
            r'^把下面的要求优化[^\n：:]*[：:]',
            r'^把这个提示词适配[^\n：:]*[：:]',
            r'^(?:Help me )?(?:optimi[sz]e|turn this request into)[^\n:]*:',
            r'^Turn (?:this into a prompt|the requirements below into)[^\n:]*:',
            r'^Adapt this prompt[^\n:]*:',
        )
        for pattern in patterns:
            replaced, count = re.subn(pattern, '', text, count=1, flags=re.I)
            if count:
                text = replaced
                break
    return text.strip()


def _material(case, source):
    effect = case.get('effect') or {}
    candidates = [effect.get('swap_material', {}).get('from', ''), effect.get('material', '')]
    material = [s for s in candidates if s and s in source]
    if not material:
        # Explicit data labels and standalone quoted paragraphs only. No arbitrary
        # prose classification or broad removal of HTML comments from user data.
        match = re.search(r'(?:^|\n|[。.]\s*)(?:材料|会议要点|示例来信|来信|评论|反馈|Material|Meeting notes|Sample email|Email|Review|Feedback)[：:]\s*', source, re.I)
        if match:
            # The data delimiter may become the output's Material label.
            # Check its contents, not that framing label.
            material.append(source[match.end():])
        for line in source.splitlines():
            if re.match(r'^\s*[“「『"]', line):
                material.append(line)
        inline = re.search(r'(?:客户原话|customer\'s words)\s*([“「『"])(.*?)', source, re.I)
        if inline:
            opening = inline.group(1)
            closing = {'“': '”', '「': '」', '『': '』', '"': '"'}[opening]
            end = source.find(closing, inline.end())
            if end >= 0:
                material.append(source[inline.start(1):end + 1])
    return list(dict.fromkeys(line.strip() for block in material for line in block.splitlines() if line.strip()))


def _input(case):
    raw = case['optimizer_input']
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError('missing optimizer input')
    # Revocations can change numeric/quoted constraints. Do not treat the prior
    # AI paraphrase or revoked user clauses as immutable source evidence.
    if re.search(r'【上一版你交付的提示词】|\[The prompt you delivered last time\]', raw):
        raise ValueError('multi-turn source requires semantic revocation review')
    source = _strip_controls(raw)
    if not source:
        raise ValueError('empty input after optimizer controls')
    wrapped_prompt = False
    # Only a single pair around the whole explicitly introduced prompt is
    # framing. Do not strip quotes from embedded reviews, samples or passages.
    if source != raw.strip():
        for left, right in QUOTE_PAIRS:
            if source.startswith(left) and source.endswith(right) and source.find(right, 1) == len(source) - 1:
                source = source[1:-1]
                wrapped_prompt = True
                break
    material = _material(case, source)
    is_rules = re.search(r'优化(?:这段)?系统提示词|客服机器人提示词|optimi[sz]e (?:this )?(?:system prompt|customer-service bot prompt)', raw, re.I)
    if is_rules:
        def remove_rule_injection(match):
            comment = match.group()
            if _normalize(comment) in _normalize('\n'.join(material)):
                return comment
            if re.search(r'忽略.*(?:规则|指令)|ignore.*rules', comment, re.I | re.S) and re.search(r'系统提示词|密钥|system prompt|secret key', comment, re.I):
                return ''
            return comment
        source = re.sub(r'<!--.*?-->', remove_rule_injection, source, flags=re.S)
    if wrapped_prompt and not material:
        # Keep full-text deletion coverage after removing framing quotes.
        material = [line for line in source.splitlines() if line.strip()]
    return source, material


def _normalize(text):
    return ' '.join(text.split())


def _warning_text(notes):
    for template in TEMPLATES:
        notes = notes.replace(template, '')
    # References to section names are fixed vocabulary even with other quote
    # styles or sentence prefixes. Do not exempt arbitrary quoted suggestions.
    for left, right in QUOTE_PAIRS:
        for name in SECTION_NAMES:
            notes = notes.replace(left + name + right, ' ')
    # SKILL.md uses {{TO FILL: name | format example}}. Suppress the marker,
    # not its values: invented numbers/names in examples still need review.
    notes = re.sub(r'(?<=\{\{)TO FILL(?=\s*:)', ' ', notes)
    notes = re.sub(r'\[(?:TO FILL|DATA NEEDED)\]|【待补数据】', ' ', notes)
    return re.sub(r'^\s*(?:[-*+]\s+)?(?:\(?[\d]+[.)、）]|[（(][\d]+[）)]|[①-⑳])\s*', '', notes, flags=re.M)


def check_fidelity(case, opt_reply, lang='zh'):
    """Return status and typed original text evidence without I/O or mutation."""
    if lang not in ('zh', 'en'):
        return _result('undetermined', warnings=[_item('parse', 'unsupported language')])
    try:
        text, delivered = _unwrap(case, opt_reply)
        if not delivered and not LABEL_HINT.search(text):
            return _result('not_applicable')
        source, material = _input(case)
        if delivered and not WORDS_HINT.search(text):
            return _result('fail', missing=[_item('section', "用户原话/User's exact words")])
        sections = _sections(text)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return _result('undetermined', warnings=[_item('parse', str(exc))])
    protected = [sections[k] for k in ('words', 'material') if k in sections]
    expected_counts = Counter(_tokens(source, unique=False))
    actual_counts = Counter(token for block in protected for token in _tokens(block, unique=False))
    missing = []
    for (kind, token), expected in expected_counts.items():
        # Quoted content may legitimately be copied without quote delimiters.
        # Count literal content separately within each section, never across a
        # section boundary. Other types retain their tokenizer boundaries.
        if kind == 'quote':
            expected = source.count(token)
            actual = sum(block.count(token) for block in protected)
        else:
            actual = actual_counts[kind, token]
        if actual < expected:
            missing.append({**_item(kind, token), 'expected': expected, 'actual': actual})
    material_missing = [_item('material', line) for line in material
                        if not any(_normalize(line) in _normalize(block) for block in protected)]
    notes = _warning_text(sections.get('notes', ''))
    # Removed rules remain evidence of what the user supplied, although they
    # are intentionally excluded from the hard retention obligations above.
    warning_source = case['optimizer_input']
    source_tokens = set(_tokens(warning_source, proper=True))
    warnings = [_item(kind, token) for kind, token in _tokens(notes, proper=True)
                if (kind, token) not in source_tokens
                and not (kind in ('quote', 'proper_name') and token in warning_source)]
    return _result('fail' if missing or material_missing else 'pass', missing, material_missing, warnings)


def summarize(results):
    """Stable status counts plus the number of individual warning signals."""
    counts = Counter(result['status'] for result in results.values())
    return {**{s: counts[s] for s in ('pass', 'fail', 'not_applicable', 'undetermined')},
            'warnings': sum(len(r['warnings']) for r in results.values())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--lang', choices=('zh', 'en'), help='default: manifest language, otherwise zh')
    args = parser.parse_args(argv)
    try:
        manifest_path = args.out / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
        recorded_lang = manifest.get('resume_contract', {}).get('lang')
        if args.lang and recorded_lang and args.lang != recorded_lang:
            raise ValueError('--lang conflicts with manifest language')
        lang = args.lang or recorded_lang or 'zh'
        if lang not in ('zh', 'en'):
            raise ValueError('unsupported manifest language')
        case_path = Path(__file__).with_name('cases.en.json' if lang == 'en' else 'cases.json')
        cases = {c['id']: c for c in json.loads(case_path.read_text(encoding='utf-8'))['cases']}
        ids = list(manifest['cases']) if 'cases' in manifest else sorted(p.name[:-len('.optimizer.md')] for p in args.out.glob('*.optimizer.md'))
        if not ids:
            raise ValueError('no optimizer cases found')
        results = {}
        for cid in ids:
            if cid not in cases:
                results[cid] = _result('undetermined', warnings=[_item('source', 'unknown case: ' + cid)])
                continue
            try:
                reply = (args.out / f'{cid}.optimizer.md').read_text(encoding='utf-8')
                results[cid] = check_fidelity(cases[cid], reply, lang)
            except (OSError, UnicodeError) as exc:
                results[cid] = _result('undetermined', warnings=[_item('source', str(exc))])
        report = {'lang': lang, 'summary': summarize(results), 'cases': results}
        output = args.out / 'fidelity.json'
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report['summary'], ensure_ascii=False))
        return 0  # Fidelity findings are review signals, not execution failures.
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print(f'fidelity error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
