import fs from "node:fs";
import { execFile } from "node:child_process";
import { randomUUID } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import { detectPromptOptimizerTrigger } from "./trigger-detection.mjs";

const PLUGIN_ID = "prompt-optimizer-router";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const execFileAsync = promisify(execFile);
const SILENT_REPLY_TOKEN = "NO_REPLY";
const DEFAULT_SPECIALIST_AGENT_ID = "prompt_optimizer";
const DEFAULT_SPECIALIST_THINKING = "low";
const DUPLICATE_ROUTE_WINDOW_MS = 5000;
const pendingRoutes = new Map();
const VALID_THINKING_LEVELS = new Set([
  "off",
  "minimal",
  "low",
  "medium",
  "high",
  "xhigh",
]);

let cachedSkill = {
  file: "",
  mtimeMs: 0,
  text: "",
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function expandHome(input) {
  if (typeof input !== "string") return input;
  if (input === "~") return process.env.HOME || input;
  if (input.startsWith("~/")) return path.join(process.env.HOME || "", input.slice(2));
  return input;
}

function normalizePositiveInteger(value, fallback) {
  if (typeof value !== "number" || !Number.isFinite(value)) return fallback;
  const rounded = Math.max(1, Math.floor(value));
  return rounded;
}

function normalizeCliPath(...values) {
  for (const value of values) {
    if (typeof value !== "string") continue;
    const trimmed = value.trim();
    if (!trimmed) continue;
    if (/^\d+$/.test(trimmed)) continue;
    return trimmed;
  }
  return "openclaw";
}

function normalizeThinkingLevel(value, fallback) {
  if (typeof value !== "string") return fallback;
  const normalized = value.trim().toLowerCase();
  return VALID_THINKING_LEVELS.has(normalized) ? normalized : fallback;
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
    "For this run, switch into prompt-optimizer mode.",
    "Treat wrapper phrases such as “优化提示词” and “帮我优化” as invocation metadata, not as task content.",
    "Ignore unrelated host-agent rituals, status blurbs, memory chatter, or extra offers.",
    "Output only the final optimized prompt body, not commentary around it.",
    "Do not execute the task itself.",
    "<normalized-raw-material>",
    normalized,
    "</normalized-raw-material>",
    "</prompt-optimizer-routing>",
  ].join("\n");
}

function buildSilentSystemPrompt() {
  return [
    "You are an internal routing shim for OpenClaw.",
    "A dedicated specialist agent is preparing the user-visible answer.",
    `Reply with exactly ${SILENT_REPLY_TOKEN} and nothing else.`,
    "Do not call tools.",
    "Do not add commentary, markdown fences, or status text.",
  ].join("\n");
}

function buildRuntimeConfig(cfg) {
  return {
    skillFile: expandHome(cfg.skillFile || resolveDefaultSkillFile()),
    cliPath: expandHome(normalizeCliPath(cfg.cliPath, process.env.OPENCLAW_CLI)),
    specialistAgentId:
      typeof cfg.specialistAgentId === "string" && cfg.specialistAgentId.trim()
        ? cfg.specialistAgentId.trim()
        : DEFAULT_SPECIALIST_AGENT_ID,
    specialistThinking: normalizeThinkingLevel(
      cfg.specialistThinking,
      DEFAULT_SPECIALIST_THINKING,
    ),
    specialistTimeoutMs: normalizePositiveInteger(cfg.specialistTimeoutMs, 5 * 60 * 1000),
    rpcTimeoutMs: normalizePositiveInteger(cfg.rpcTimeoutMs, 10 * 1000),
    abortWaitMs: normalizePositiveInteger(cfg.abortWaitMs, 1500),
    bridgeMaxAgeMs: normalizePositiveInteger(cfg.bridgeMaxAgeMs, 3 * 60 * 1000),
  };
}

function pruneExpiredRoutes(maxAgeMs) {
  const now = Date.now();
  for (const [sessionKey, route] of pendingRoutes.entries()) {
    if (now - route.createdAt > maxAgeMs) pendingRoutes.delete(sessionKey);
  }
}

function getActiveRoute(sessionKey) {
  if (!sessionKey) return null;
  return pendingRoutes.get(sessionKey) || null;
}

function isCurrentRoute(route) {
  if (!route?.sessionKey || !route?.bridgeId) return false;
  return pendingRoutes.get(route.sessionKey)?.bridgeId === route.bridgeId;
}

function clearRoute(route) {
  if (!isCurrentRoute(route)) return;
  pendingRoutes.delete(route.sessionKey);
}

function buildSilentDelegatePrompt() {
  return {
    systemPrompt: buildSilentSystemPrompt(),
  };
}

function parseJsonOutput(stdout) {
  const trimmed = String(stdout || "").trim();
  if (!trimmed) throw new Error("empty JSON output");
  return JSON.parse(trimmed);
}

function formatExecFailure(error) {
  const parts = [];
  const stdout = String(error?.stdout || "").trim();
  const stderr = String(error?.stderr || "").trim();
  if (error?.message) parts.push(String(error.message));
  if (stderr) parts.push(stderr);
  if (stdout) parts.push(stdout);
  return parts.filter(Boolean).join(" | ") || "unknown exec failure";
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function buildSpecialistSessionKey(agentId, bridgeId) {
  const safeAgentId = String(agentId || DEFAULT_SPECIALIST_AGENT_ID).trim().toLowerCase();
  const safeBridgeId = String(bridgeId || randomUUID()).trim().toLowerCase();
  return `agent:${safeAgentId}:router-${safeBridgeId}`;
}

async function runOpenClawJson(cliPath, args, timeoutMs) {
  const command = [cliPath, ...args].map(shellQuote).join(" ");
  const result = await execFileAsync("/bin/zsh", ["-lc", command], {
    timeout: timeoutMs,
    maxBuffer: 8 * 1024 * 1024,
  });
  return parseJsonOutput(result.stdout);
}

function extractSpecialistText(payload) {
  const firstPayload = payload?.result?.payloads?.find?.(
    (item) => typeof item?.text === "string" && item.text.trim(),
  );
  if (firstPayload?.text) return firstPayload.text.trim();
  if (typeof payload?.result?.text === "string" && payload.result.text.trim()) {
    return payload.result.text.trim();
  }
  return "";
}

async function runSpecialistAgent(runtimeCfg, route) {
  route.specialistSessionKey = buildSpecialistSessionKey(
    runtimeCfg.specialistAgentId,
    route.bridgeId,
  );

  const params = JSON.stringify({
    agentId: runtimeCfg.specialistAgentId,
    sessionKey: route.specialistSessionKey,
    message: route.normalized,
    thinking: runtimeCfg.specialistThinking,
    idempotencyKey: route.bridgeId,
  });

  return runOpenClawJson(
    runtimeCfg.cliPath,
    [
      "gateway",
      "call",
      "agent",
      "--expect-final",
      "--json",
      "--timeout",
      String(runtimeCfg.specialistTimeoutMs),
      "--params",
      params,
    ],
    runtimeCfg.specialistTimeoutMs + 5000,
  );
}

async function injectMessage(runtimeCfg, route, message, logger) {
  const params = JSON.stringify({
    sessionKey: route.sessionKey,
    message,
  });
  await runOpenClawJson(
    runtimeCfg.cliPath,
    ["gateway", "call", "chat.inject", "--json", "--timeout", String(runtimeCfg.rpcTimeoutMs), "--params", params],
    runtimeCfg.rpcTimeoutMs + 2000,
  );
  logger.info?.(
    `[${PLUGIN_ID}] injected specialist reply into session=${route.sessionKey} bridge=${route.bridgeId}`,
  );
}

async function cleanupSpecialistSession(runtimeCfg, route, logger) {
  if (!route?.specialistSessionKey) return;
  try {
    const params = JSON.stringify({
      key: route.specialistSessionKey,
      deleteTranscript: true,
    });
    await runOpenClawJson(
      runtimeCfg.cliPath,
      [
        "gateway",
        "call",
        "sessions.delete",
        "--json",
        "--timeout",
        String(runtimeCfg.rpcTimeoutMs),
        "--params",
        params,
      ],
      runtimeCfg.rpcTimeoutMs + 2000,
    );
    logger.info?.(
      `[${PLUGIN_ID}] cleaned temporary specialist session=${route.specialistSessionKey} bridge=${route.bridgeId}`,
    );
  } catch (error) {
    logger.warn?.(
      `[${PLUGIN_ID}] failed to clean specialist session=${route.specialistSessionKey} bridge=${route.bridgeId}: ${formatExecFailure(error)}`,
    );
  }
}

async function abortHostRun(runtimeCfg, route, logger) {
  if (!route.runId) return;
  if (route.abortPromise) {
    try {
      await route.abortPromise;
    } catch {
      // ignored: a failed abort should not block the specialist bridge
    }
    return;
  }

  const params = JSON.stringify({
    sessionKey: route.sessionKey,
    runId: route.runId,
  });

  route.abortPromise = runOpenClawJson(
    runtimeCfg.cliPath,
    ["gateway", "call", "chat.abort", "--json", "--timeout", String(runtimeCfg.rpcTimeoutMs), "--params", params],
    runtimeCfg.rpcTimeoutMs + 2000,
  )
    .then((payload) => {
      logger.info?.(
        `[${PLUGIN_ID}] abort requested for session=${route.sessionKey} run=${route.runId} bridge=${route.bridgeId} aborted=${Boolean(payload?.aborted)}`,
      );
    })
    .catch((error) => {
      logger.warn?.(
        `[${PLUGIN_ID}] failed to abort host run for session=${route.sessionKey} bridge=${route.bridgeId}: ${formatExecFailure(error)}`,
      );
    });

  await route.abortPromise;
}

async function waitForAbortWindow(runtimeCfg, route) {
  const deadline = Date.now() + runtimeCfg.abortWaitMs;
  while (isCurrentRoute(route) && Date.now() < deadline) {
    if (route.abortPromise) {
      try {
        await Promise.race([route.abortPromise, sleep(100)]);
      } catch {
        // ignored on purpose
      }
      return;
    }
    await sleep(50);
  }
}

async function runBridgeTask(runtimeCfg, route, logger) {
  try {
    await waitForAbortWindow(runtimeCfg, route);
    if (!isCurrentRoute(route)) return;

    if (route.runId && !route.abortPromise) {
      await abortHostRun(runtimeCfg, route, logger);
      if (!isCurrentRoute(route)) return;
    }

    logger.info?.(
      `[${PLUGIN_ID}] bridge start session=${route.sessionKey} bridge=${route.bridgeId} specialist=${runtimeCfg.specialistAgentId} thinking=${runtimeCfg.specialistThinking}`,
    );

    const specialistPayload = await runSpecialistAgent(runtimeCfg, route);
    if (!isCurrentRoute(route)) return;

    const specialistText = extractSpecialistText(specialistPayload);
    if (!specialistText) {
      throw new Error("specialist returned no text payload");
    }

    await injectMessage(runtimeCfg, route, specialistText, logger);
  } catch (error) {
    if (!isCurrentRoute(route)) return;
    const message = `提示词优化器路由失败：${formatExecFailure(error)}`;
    logger.warn?.(
      `[${PLUGIN_ID}] bridge failed for session=${route.sessionKey} bridge=${route.bridgeId}: ${message}`,
    );
    try {
      await injectMessage(runtimeCfg, route, message, logger);
    } catch (injectError) {
      logger.error?.(
        `[${PLUGIN_ID}] bridge error injection failed for session=${route.sessionKey} bridge=${route.bridgeId}: ${formatExecFailure(injectError)}`,
      );
    }
  } finally {
    await cleanupSpecialistSession(runtimeCfg, route, logger);
    clearRoute(route);
  }
}

const promptOptimizerRouterPlugin = {
  id: PLUGIN_ID,
  name: "Prompt Optimizer Router",
  description:
    "Detect prompt-optimizer trigger phrases in ordinary OpenClaw chats and bridge the request through the dedicated specialist agent.",
  kind: "utility",

  register(api) {
    const cfg = api.pluginConfig || {};
    const runtimeCfg = buildRuntimeConfig(cfg);
    const enabledAgentIds = Array.isArray(cfg.enabledAgentIds)
      ? cfg.enabledAgentIds.filter((value) => typeof value === "string" && value.trim())
      : [];

    const shouldHandleAgent = (ctx) => {
      if (!ctx?.agentId) return enabledAgentIds.length === 0;
      if (ctx.agentId === "prompt_optimizer") return false;
      return enabledAgentIds.length === 0 || enabledAgentIds.includes(ctx.agentId);
    };

    const buildInlineFallback = (match) => {
      const systemPrompt = loadSkillText(runtimeCfg.skillFile, api.logger);
      if (!systemPrompt) return;
      return {
        systemPrompt,
        prependContext: buildPrependContext(match),
      };
    };

    const injectPromptOptimizer = async (event, ctx) => {
      if (!event?.prompt) return;
      if (ctx?.trigger && ctx.trigger !== "user") return;
      if (!shouldHandleAgent(ctx)) return;
      pruneExpiredRoutes(runtimeCfg.bridgeMaxAgeMs);

      const match = detectPromptOptimizerTrigger(event.prompt);
      if (!match.matched) return;
      if (!ctx?.sessionKey) return buildInlineFallback(match);

      const normalized = (match.extracted || match.raw || "").trim();
      if (!normalized) return buildInlineFallback(match);

      const existingRoute = getActiveRoute(ctx.sessionKey);
      if (
        existingRoute &&
        existingRoute.agentId === (ctx.agentId || "main") &&
        existingRoute.normalized === normalized &&
        Date.now() - existingRoute.createdAt <= DUPLICATE_ROUTE_WINDOW_MS
      ) {
        api.logger.info?.(
          `[${PLUGIN_ID}] duplicate bridge suppressed on agent=${ctx?.agentId || "unknown"} session=${ctx?.sessionKey || ctx?.sessionId || "unknown"} bridge=${existingRoute.bridgeId}`,
        );
        return buildSilentDelegatePrompt();
      }

      const route = {
        bridgeId: randomUUID(),
        sessionKey: ctx.sessionKey,
        agentId: ctx.agentId || "main",
        createdAt: Date.now(),
        normalized,
        triggerKind: match.kind,
        triggerLabel: match.label,
        runId: null,
        abortPromise: null,
      };
      pendingRoutes.set(route.sessionKey, route);

      setTimeout(() => {
        void runBridgeTask(runtimeCfg, route, api.logger);
      }, 0);

      api.logger.info(
        `[${PLUGIN_ID}] bridge armed ${match.kind}/${match.label} on agent=${ctx?.agentId || "unknown"} session=${ctx?.sessionKey || ctx?.sessionId || "unknown"} bridge=${route.bridgeId}`,
      );

      return buildSilentDelegatePrompt();
    };

    const onLlmInput = async (event, ctx) => {
      pruneExpiredRoutes(runtimeCfg.bridgeMaxAgeMs);
      const route = getActiveRoute(ctx?.sessionKey);
      if (!route || ctx?.agentId !== route.agentId) return;
      if (!route.runId && event?.runId) route.runId = event.runId;
      if (!route.runId) return;
      if (!route.abortPromise) await abortHostRun(runtimeCfg, route, api.logger);
    };

    const suppressHostTranscript = (event, ctx) => {
      pruneExpiredRoutes(runtimeCfg.bridgeMaxAgeMs);
      const route = getActiveRoute(ctx?.sessionKey);
      if (!route || ctx?.agentId !== route.agentId) return;
      const role = event?.message?.role;
      if (role !== "assistant" && role !== "toolResult") return;
      api.logger.info?.(
        `[${PLUGIN_ID}] suppressed host transcript role=${role} session=${route.sessionKey} bridge=${route.bridgeId}`,
      );
      return { block: true };
    };

    api.on("before_prompt_build", injectPromptOptimizer, { priority: 1000 });
    api.on("llm_input", onLlmInput, { priority: 1000 });
    api.on("before_message_write", suppressHostTranscript, { priority: 1000 });
  },
};

export default promptOptimizerRouterPlugin;
