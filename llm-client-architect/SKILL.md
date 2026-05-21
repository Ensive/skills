---
name: llm-client-architect
description: >-
  Designs provider-abstracted LLM clients for OpenAI-compatible APIs including
  OpenRouter, with timeouts, jittered retries, Retry-After honoring, model fallback,
  streaming, and secret redaction in logs. Use when wiring API clients, "OpenRouter",
  HTTP retries, Retry-After, rate limit, streaming tokens, or "redact API key in
  logs". For tool-class retry classification and loop termination, see
  agentic-loop-engineer. Not for agent loop orchestration, tool schemas, or
  filesystem path guards.
---

# LLM Client Architect

## When to use

- User adds or refactors HTTP client code for chat/completions APIs.
- User integrates OpenRouter, Anthropic-compatible gateways, or local OpenAI shims.
- User needs timeouts, retries, rate-limit handling, or fallback model chains.
- User implements streaming SSE or chunked responses to stdout/UI.
- User logs requests and must redact Authorization headers and API keys.

## Core principles

1. One thin adapter per provider; shared types for messages, tools, and usage metadata.
2. OpenAI-compatible base URL + paths as default; override only where spec diverges.
3. Every request has connect and response timeouts; abort via AbortSignal end-to-end.
4. Retry 429 and 5xx with exponential backoff, jitter, and Retry-After respect.
5. Model fallback is ordered list; fail over only on retryable errors, not 4xx validation.
6. Streaming: parse frames incrementally; surface tokens via async iterable callback.
7. Never log raw API keys; redact `Authorization`, `api-key`, and query tokens.
8. Normalize errors into `{ code, message, retryable }` for agentic-loop-engineer.
9. Record latency, model id, and token usage on every completion for budgets.
10. Prompt wording stays in prompt-engineer; loop orchestration and tool-class retry policy in agentic-loop-engineer.
11. Adapters emit the normalized tool-call/result shape declared in agentic-loop-engineer; do not leak provider field names (`tool_calls`, `tool_use`) past the adapter boundary.

## Checklist

- [ ] Define `LlmClient` interface: `complete`, `stream`, optional `embed`.
- [ ] Centralize base URL, default model, and headers from config-and-env-designer.
- [ ] Set `fetch` timeout or AbortController per attempt.
- [ ] Implement retry policy table: which status codes retry, max attempts.
- [ ] Implement fallback chain with logging of which model succeeded.
- [ ] Parse streaming protocol for provider (SSE data lines, JSON chunks).
- [ ] Map provider-specific tool_call blocks to internal normalized shape.
- [ ] Redact secrets in debug logs and error attachments.
- [ ] Handle empty choices, truncated JSON, and context-length errors distinctly.
- [ ] Expose hooks for tests: inject `fetch` mock (see integration-tester).

## Patterns

**Normalized error shape (required for loop + fallback)**

```typescript
export type LlmError = { code: string; message: string; retryable: boolean };

export async function toLlmError(res: Response): Promise<LlmError> {
  const retryable = res.status === 429 || res.status >= 500;
  let message = res.statusText;
  try {
    const body = (await res.json()) as { error?: { message?: string } };
    message = body.error?.message ?? message;
  } catch { /* non-JSON body */ }
  return {
    code: `http_${res.status}`,
    message,
    retryable,
  };
}
```

4xx validation errors (except 429): `retryable: false`. Context-length and auth failures: `retryable: false`.

**OpenAI-compatible client skeleton**

```typescript
type ChatRequest = { model: string; messages: unknown[]; tools?: unknown[] };
type ChatResponse = LlmResponse; // from project types module — see agentic-loop-engineer/reference.md

type LlmClient = {
  complete(req: ChatRequest, opts?: { signal?: AbortSignal }): Promise<ChatResponse>;
  stream(req: ChatRequest, opts?: StreamOpts): AsyncIterable<ChatDelta>;
};

function asLlmError(e: unknown): LlmError {
  if (e && typeof e === "object" && "retryable" in e && "code" in e) return e as LlmError;
  return { code: "unknown", message: e instanceof Error ? e.message : String(e), retryable: false };
}

async function postJson(url: string, body: unknown, init: RequestInit) {
  const res = await fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
    body: JSON.stringify(body),
    signal: init.signal,
  });
  if (!res.ok) throw await toLlmError(res);
  return res.json();
}

async function postJsonWithRetry(
  url: string,
  body: unknown,
  init: RequestInit,
  opts: { maxAttempts: number; baseMs: number; maxMs: number },
): Promise<unknown> {
  let lastRes: Response | undefined;
  for (let attempt = 0; attempt < opts.maxAttempts; attempt++) {
    const res = await fetch(url, {
      ...init,
      headers: { "Content-Type": "application/json", ...init.headers },
      body: JSON.stringify(body),
      signal: init.signal,
    });
    if (res.ok) return res.json();
    lastRes = res;
    const err = await toLlmError(res);
    if (!err.retryable || attempt === opts.maxAttempts - 1) throw err;
    await new Promise((r) => setTimeout(r, delayFor(res, attempt, opts)));
  }
  throw await toLlmError(lastRes!);
}
```

**Delay with Retry-After + jittered backoff**

```typescript
function parseRetryAfter(res: Response): number | undefined {
  const h = res.headers.get("retry-after");
  if (!h) return undefined;
  const secs = Number(h);
  if (Number.isFinite(secs)) return Math.max(0, secs * 1000);
  const date = Date.parse(h);
  return Number.isFinite(date) ? Math.max(0, date - Date.now()) : undefined;
}

function delayFor(res: Response | undefined, attempt: number, opts: {
  baseMs: number; maxMs: number;
}): number {
  const expo = opts.baseMs * 2 ** attempt * (0.5 + Math.random() * 0.5);
  const hinted = res ? parseRetryAfter(res) : undefined;
  return Math.min(opts.maxMs, Math.max(expo, hinted ?? 0));
}
```

**Redacted headers and body**

Place in `src/llm/redact.ts` (path configurable). Export `safeHeaders` and `safeBody`; `observability-designer` imports `safeBody` from this module.

```typescript
const SECRET_HEADERS = new Set([
  "authorization", "proxy-authorization", "cookie", "set-cookie",
  "api-key", "x-api-key", "openai-api-key", "anthropic-api-key",
  "openai-organization", "x-goog-api-key",
]);
const SECRET_KEY_RX = /key|token|secret|password|authorization/i;

export function safeHeaders(h: HeadersInit): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of new Headers(h)) {
    out[k] = SECRET_HEADERS.has(k.toLowerCase()) ? "[REDACTED]" : v;
  }
  return out;
}

export function safeBody(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(safeBody);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = SECRET_KEY_RX.test(k) ? "[REDACTED]" : safeBody(v);
    }
    return out;
  }
  return value;
}
```

**Fallback chain (never returns undefined)**

```typescript
async function completeWithFallback(
  req: ChatRequest,
  models: readonly string[],
): Promise<ChatResponse> {
  if (models.length === 0) throw new Error("fallback chain is empty");
  let lastError: LlmError | undefined;
  for (const model of models) {
    try {
      return await complete({ ...req, model });
    } catch (e) {
      const err = asLlmError(e);
      if (!err.retryable) throw err;
      lastError = err;
    }
  }
  throw lastError ?? new Error("fallback chain exhausted");
}
```

## Anti-patterns

- **Hard-coding provider URLs in call sites** — drift; read from config.
- **Infinite retry on 400** — waste; only retry retryable codes.
- **Logging full request bodies with secrets** — leakage; redact and truncate.
- **Buffering entire stream before UI update** — latency; incremental parse.
- **Different error shapes per call site** — loops cannot recover; normalize errors.
- **Casting caught errors with `as LlmError`** — mis-classifies failures; use `asLlmError(e)` helper.
- **Mixing fetch and SDK without abort wiring** — hung requests; one signal path.

## Output format

```markdown
# LLM client design: <project>

## Interface
- Methods: <list>
- Config keys: <env vars>

## Providers
| Provider | Base URL | Notes |
|----------|----------|-------|

## Resilience
- Timeout: <ms>
- Retries: <policy>
- Fallback models: <ordered list>

## Streaming
- Protocol: <SSE/chunk>
- Consumer API: <signature>

## Logging
- Redacted fields: <list>
```

## Escalation

- Ask which providers and whether tools/streaming are required day one.
- Ask data residency or logging restrictions before choosing hosted gateway.
- Proceed with OpenAI-compatible adapter when provider list is incomplete.
