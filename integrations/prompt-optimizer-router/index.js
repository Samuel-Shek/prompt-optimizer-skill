import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { detectPromptOptimizerTrigger } from "./trigger-detection.mjs";

const PLUGIN_ID = "prompt-optimizer-router";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

let cachedSkill = {
  file: "",
  mtimeMs: 0,
  text: "",
};

function expandHome(input) {
  if (typeof input !== "string") return input;
  if (input === "~") return process.env.HOME || input;
  if (input.startsWith("~/")) return path.join(process.env.HOME || "", input.slice(2));
  return input;
}

function resolveDefaultSkillFile() {
  return path.resolve(__dirname, "..", "..", "SKILL.md");
}

function loadSkillText(skillFile, logger) {
  try {
    const stat = fs.statSync(skillFile);
    if (
      cachedSkill.file === skillFile &&
      cachedSkill.mtimeMs === stat.mtimeMs &&
      cachedSkill.text
    ) {
      return cachedSkill.text;
    }

    const text = fs.readFileSync(skillFile, "utf8").trim();
    cachedSkill = {
      file: skillFile,
      mtimeMs: stat.mtimeMs,
      text,
    };
    return text;
  } catch (error) {
    logger.warn?.(
      `[${PLUGIN_ID}] failed to read skill file ${skillFile}: ${String(error)}`,
    );
    return "";
  }
}

function buildPrependContext(match) {
  const normalized = match.extracted || match.raw;
  return [
    "<prompt-optimizer-routing>",
    "The user intentionally invoked the prompt optimizer.",
    "Treat wrapper phrases such as “优化提示词” and “帮我优化” as invocation metadata, not as task content.",
    "Only optimize the normalized raw material below into a final prompt. Do not execute the task itself.",
    "<normalized-raw-material>",
    normalized,
    "</normalized-raw-material>",
    "</prompt-optimizer-routing>",
  ].join("\n");
}

const promptOptimizerRouterPlugin = {
  id: PLUGIN_ID,
  name: "Prompt Optimizer Router",
  description:
    "Detect prompt-optimizer trigger phrases in ordinary OpenClaw chats and inject the prompt optimizer system prompt for that run.",
  kind: "utility",

  register(api) {
    const cfg = api.pluginConfig || {};
    const skillFile = expandHome(cfg.skillFile || resolveDefaultSkillFile());
    const enabledAgentIds = Array.isArray(cfg.enabledAgentIds)
      ? cfg.enabledAgentIds.filter((value) => typeof value === "string" && value.trim())
      : [];

    const shouldHandleAgent = (ctx) => {
      if (!ctx?.agentId) return enabledAgentIds.length === 0;
      if (ctx.agentId === "prompt_optimizer") return false;
      return enabledAgentIds.length === 0 || enabledAgentIds.includes(ctx.agentId);
    };

    const injectPromptOptimizer = async (event, ctx) => {
      if (!event?.prompt) return;
      if (ctx?.trigger && ctx.trigger !== "user") return;
      if (!shouldHandleAgent(ctx)) return;

      const match = detectPromptOptimizerTrigger(event.prompt);
      if (!match.matched) return;

      const systemPrompt = loadSkillText(skillFile, api.logger);
      if (!systemPrompt) return;

      api.logger.info(
        `[${PLUGIN_ID}] matched ${match.kind}/${match.label} on agent=${ctx?.agentId || "unknown"} session=${ctx?.sessionKey || ctx?.sessionId || "unknown"}`,
      );

      return {
        systemPrompt,
        prependContext: buildPrependContext(match),
      };
    };

    api.on("before_prompt_build", injectPromptOptimizer, { priority: 1000 });
    api.on("before_agent_start", injectPromptOptimizer, { priority: 1000 });
  },
};

export default promptOptimizerRouterPlugin;
