#!/usr/bin/env node

import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { randomUUID } from "node:crypto";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const OPENCLAW_CLI = process.env.OPENCLAW_CLI || "openclaw";
const SEND_TIMEOUT_MS = Number(process.env.PROMPT_OPTIMIZER_E2E_SEND_TIMEOUT_MS || 10_000);
const HISTORY_TIMEOUT_MS = Number(process.env.PROMPT_OPTIMIZER_E2E_HISTORY_TIMEOUT_MS || 30_000);
const WAIT_TIMEOUT_MS = Number(process.env.PROMPT_OPTIMIZER_E2E_WAIT_TIMEOUT_MS || 180_000);
const POLL_INTERVAL_MS = Number(process.env.PROMPT_OPTIMIZER_E2E_POLL_INTERVAL_MS || 1_000);

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function extractText(message) {
  const content = Array.isArray(message?.content) ? message.content : [];
  return content
    .map((block) => (typeof block?.text === "string" ? block.text : ""))
    .join("\n")
    .trim();
}

async function runJson(args, timeoutMs) {
  const command = [OPENCLAW_CLI, ...args].map(shellQuote).join(" ");
  const result = await execFileAsync("/bin/zsh", ["-lc", command], {
    timeout: timeoutMs,
    maxBuffer: 8 * 1024 * 1024,
  });
  return JSON.parse(String(result.stdout || "").trim());
}

async function gatewayCall(method, params, timeoutMs) {
  return runJson(
    [
      "gateway",
      "call",
      method,
      "--json",
      "--timeout",
      String(timeoutMs),
      "--params",
      JSON.stringify(params),
    ],
    timeoutMs + 5_000,
  );
}

async function getHistory(sessionKey) {
  return gatewayCall("chat.history", { sessionKey }, HISTORY_TIMEOUT_MS);
}

async function deleteSession(key) {
  try {
    await gatewayCall(
      "sessions.delete",
      { key, deleteTranscript: true },
      SEND_TIMEOUT_MS,
    );
  } catch {
    // Best effort cleanup only.
  }
}

async function waitFor(label, timeoutMs, fn) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const value = await fn();
      if (value) return value;
    } catch {
      // When the gateway is busy under xhigh thinking, transient polling timeouts are acceptable.
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
  throw new Error(`timeout waiting for ${label}`);
}

const sessionKey = `agent:main:router-e2e-${Date.now()}`;
const firstMessage =
  "优化提示词：把“做个全球股票近况的调研”整理成适合 Claude 的终版提示词，要求结构化、结论优先。";
const secondMessage = "现在只回复四个字：正常对话";
const startedAt = Date.now();

try {
  await gatewayCall(
    "chat.send",
    {
      sessionKey,
      message: firstMessage,
      idempotencyKey: randomUUID(),
    },
    SEND_TIMEOUT_MS,
  );

  const routed = await waitFor("gateway-injected routed reply", WAIT_TIMEOUT_MS, async () => {
    const history = await getHistory(sessionKey);
    const injectedMessages = (history.messages || []).filter(
      (message) =>
        message?.role === "assistant" &&
        message?.provider === "openclaw" &&
        message?.model === "gateway-injected",
    );
    const injected = injectedMessages.find((message) => {
      const text = extractText(message);
      return /(任务目标|请基于|```markdown)/.test(text);
    });
    if (!injected) return null;
    return { history, injected, injectedMessages };
  });

  const routedText = extractText(routed.injected);
  assert.ok(routedText.length > 0, "expected routed reply text");
  assert.match(
    routedText,
    /(任务目标|请基于|```markdown)/,
    "expected routed reply to look like an optimized prompt",
  );

  const firstTurnMs = Date.now() - startedAt;

  await gatewayCall(
    "chat.send",
    {
      sessionKey,
      message: secondMessage,
      idempotencyKey: randomUUID(),
    },
    SEND_TIMEOUT_MS,
  );

  const plain = await waitFor("plain follow-up reply", WAIT_TIMEOUT_MS, async () => {
    const history = await getHistory(sessionKey);
    const assistantMessages = (history.messages || []).filter(
      (message) => message?.role === "assistant",
    );
    const latest = assistantMessages.at(-1);
    if (!latest) return null;
    const text = extractText(latest);
    if (!text.includes("正常对话")) return null;
    return { history, latest, text };
  });

  const injectedMessages = (plain.history.messages || []).filter(
    (message) =>
      message?.role === "assistant" &&
      message?.provider === "openclaw" &&
      message?.model === "gateway-injected",
  );
  const promptReplies = injectedMessages.filter((message) => {
    const text = extractText(message);
    return /(任务目标|请基于|```markdown)/.test(text);
  });
  const progressReplies = injectedMessages.filter((message) => {
    const text = extractText(message);
    return /正在分析原始需求|还在重写终版提示词/.test(text);
  });

  assert.equal(promptReplies.length, 1, "expected exactly one final optimized prompt reply");
  assert.ok(progressReplies.length >= 1, "expected at least one short progress note");
  assert.notEqual(
    plain.latest?.model,
    "gateway-injected",
    "expected the follow-up reply to come from the normal host agent path",
  );
  assert.match(plain.text, /正常对话/, "expected the follow-up reply to stay in normal chat mode");

  const totalMs = Date.now() - startedAt;
  console.log(
    `[ok] host-router E2E passed | first-turn=${firstTurnMs}ms | total=${totalMs}ms | session=${sessionKey}`,
  );
} finally {
  await deleteSession(sessionKey);
}
