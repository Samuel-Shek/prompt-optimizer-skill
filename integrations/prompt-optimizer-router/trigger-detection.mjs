const PREFIX_RULES = [
  {
    label: "优化提示词",
    kind: "recommended-prefix",
    re: /^\s*优化提示词\s*[:：]\s*([\s\S]+?)\s*$/u,
  },
  {
    label: "帮我优化",
    kind: "recommended-prefix",
    re: /^\s*帮我优化\s*[:：]\s*([\s\S]+?)\s*$/u,
  },
  {
    label: "调用提示词优化器",
    kind: "semantic-prefix",
    re: /^\s*(?:调用|使用|用|请用)\s*(?:提示词优化器|prompt optimizer)(?:\s*(?:来|去|处理|优化|帮我处理|帮我优化))?\s*[:：]\s*([\s\S]+?)\s*$/iu,
  },
  {
    label: "Prompt Optimizer",
    kind: "semantic-prefix",
    re: /^\s*(?:invoke|call|use|run)\s*prompt optimizer(?:\s*(?:to|for|on))?\s*[:：]\s*([\s\S]+?)\s*$/iu,
  },
];

const SUFFIX_RULES = [
  {
    label: "——优化提示词",
    kind: "recommended-suffix",
    re: /^\s*([\s\S]+?)\s*(?:——|—|--|-)\s*优化提示词\s*$/u,
  },
  {
    label: "——帮我优化",
    kind: "recommended-suffix",
    re: /^\s*([\s\S]+?)\s*(?:——|—|--|-)\s*帮我优化\s*$/u,
  },
];

export const RECOMMENDED_TRIGGER_EXAMPLES = [
  "优化提示词：做个全球股票近况的调研",
  "帮我优化：做个全球股票近况的调研",
  "做个全球股票近况的调研——优化提示词",
  "做个全球股票近况的调研——帮我优化",
];

export const SEMANTIC_TRIGGER_EXAMPLES = [
  "调用提示词优化器：做个全球股票近况的调研",
  "调用 Prompt Optimizer：做个全球股票近况的调研",
  "使用提示词优化器：把这段口语需求整理成 Claude 可直接执行的 prompt",
];

function normalizeExtractedText(text) {
  return String(text || "").replace(/\r\n/g, "\n").trim();
}

function buildPromptCandidates(raw) {
  const candidates = new Set();
  const push = (value) => {
    const normalized = normalizeExtractedText(value);
    if (normalized) candidates.add(normalized);
  };

  push(raw);

  const memoryTail = raw.split("</relevant-memories>").pop();
  if (memoryTail && memoryTail !== raw) push(memoryTail);

  const lines = raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length > 0) {
    push(lines[lines.length - 1]);
  }

  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const line = lines[index];
    const timestampMatch = line.match(/^\[[^\]]+\]\s*([\s\S]+)$/u);
    if (timestampMatch?.[1]) {
      push(timestampMatch[1]);
      break;
    }
  }

  return Array.from(candidates);
}

export function detectPromptOptimizerTrigger(prompt) {
  const raw = normalizeExtractedText(prompt);
  if (!raw) {
    return { matched: false, raw, extracted: "", kind: "none", label: "" };
  }

  const candidates = buildPromptCandidates(raw);

  for (const candidate of candidates) {
    for (const rule of PREFIX_RULES) {
      const match = candidate.match(rule.re);
      if (!match) continue;
      const extracted = normalizeExtractedText(match[1]);
      return {
        matched: true,
        raw,
        extracted: extracted || candidate,
        kind: rule.kind,
        label: rule.label,
      };
    }

    for (const rule of SUFFIX_RULES) {
      const match = candidate.match(rule.re);
      if (!match) continue;
      const extracted = normalizeExtractedText(match[1]);
      return {
        matched: true,
        raw,
        extracted: extracted || candidate,
        kind: rule.kind,
        label: rule.label,
      };
    }
  }

  return { matched: false, raw, extracted: "", kind: "none", label: "" };
}
