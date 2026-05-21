---
name: typescript-security-auditor
description: >-
  Audits TypeScript and Node.js code for OWASP Top 10 risks including injection,
  prototype pollution, SSRF, secret leakage, and supply-chain exposure. Use when
  the user asks for a security review, vulnerability scan, OWASP mapping, hardening
  advice, or phrases like "is this secure", "security audit", "find vulnerabilities",
  or "check for secrets". Not for implementing safe file-open/path-guard code — use
  secure-filesystem-access first, then this skill to map FS gaps to OWASP/CWE.
---

# TypeScript Security Auditor

## When to use

- User requests a security review or threat model for a TS/Node service or CLI.
- User mentions OWASP, CWE, injection, XSS, SSRF, or secrets in `.env` or logs.
- User adds a dependency, HTTP client, file upload, or dynamic `eval`/`Function`.
- User exposes an API route, webhook, or shell/exec surface (audit and map risks).
- User mentions path traversal in an **audit** context after implementation exists (if building/fixing guards → secure-filesystem-access).
- User asks whether prototype pollution or `Object.assign` from untrusted input is safe.

## Core principles

1. Treat all external input as hostile: HTTP bodies, headers, env, argv, tool args, LLM output.
2. Map findings to OWASP Top 10 categories with CWE IDs when possible.
3. Prefer safe APIs: parameterized queries, schema-validated parse, allowlists over blocklists.
4. Never log tokens, API keys, cookies, or PII; redact before persistence.
5. Pin and audit dependencies; flag postinstall scripts and typosquatting names.
6. Fail closed on authZ errors; default deny for new routes and tools.
7. Separate trust zones: browser, server, subprocess, filesystem, outbound network.
8. Assume LLM-generated code may be wrong; verify security properties independently.
9. Document residual risk when a fix needs architecture change.
10. Do not weaken security for performance; see also: program-performance-optimizer.

## Checklist

- [ ] Enumerate all input surfaces (HTTP, CLI, tools, env, files, child stdin).
- [ ] Check SQL/NoSQL/command/template injection; confirm parameterization or escaping.
- [ ] Check path operations: reject `..` (also `%2e%2e` and other percent-encodings), NUL and control bytes `0x00`–`0x1F`, absolute paths outside allowlist roots, Windows `:` alternate streams; normalize to NFC before comparisons. Implementation lives in secure-filesystem-access.
- [ ] Check `Object.assign`, spread, and `JSON.parse` on untrusted data for prototype pollution.
- [ ] Check outbound `fetch`/`http` for SSRF: block metadata IPs, file URLs, internal ranges.
- [ ] Check authN/authZ on every mutating route; verify session/token binding and expiry.
- [ ] Scan for hardcoded secrets; verify `.gitignore` and pre-commit secret hooks.
- [ ] Review `child_process`, `exec`, and shell string concatenation.
- [ ] Review dependency tree for known advisories and unnecessary native addons.
- [ ] Confirm security headers and cookie flags for any HTTP surface.
- [ ] Record severity (critical/high/medium/low/info) and exploitability per finding.

## Patterns

**Parameterized query (SQL)**

```typescript
const row = await db.query("SELECT * FROM users WHERE id = $1", [userId]);
```

**Safe path join under workspace root**

Do not reimplement here. Call `assertInsideRoot` + `realpath` from secure-filesystem-access; that skill owns the canonical pipeline (resolve, prefix guard, realpath re-check, fd-stat). Inlining a partial guard in audited code is itself a finding.

**Safe parse before merge (prototype pollution)**

`JSON.parse` drops `__proto__` in modern Node; risk is merging parsed objects onto prototypes or class instances.

```typescript
const parsed = JSON.parse(raw) as unknown;
const safe = MySchema.parse(parsed); // Zod/TypeBox — preferred
// Or: Object.assign(Object.create(null), parsed as Record<string, unknown>);
// structuredClone is for deep-copying already-validated objects, not pollution defense.
```

**SSRF guard on outbound URL**

```typescript
const host = new URL(url).hostname;
if (isPrivateOrMetadataHost(host)) throw new Error("blocked host");
```

**Secret from env only**

```typescript
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error("API_KEY required");
```

## Anti-patterns

- **String-built SQL or shell commands** — enables injection; use parameters or argv arrays.
- **`eval`, `new Function`, or `vm` on user/LLM text** — arbitrary code execution.
- **`fs.readFile(userPath)` without normalization** — path traversal; see secure-filesystem-access.
- **Logging full request bodies or Authorization headers** — credential and PII leakage.
- **`Object.assign(target, untrusted)` on class instances** — prototype pollution.
- **Trusting `Content-Type` or file extensions alone** — MIME spoofing; validate content.

## Output format

```markdown
# Security audit: <component or repo scope>

## Summary
- Critical: N | High: N | Medium: N | Low: N | Info: N

## Findings
### <ID>-<short-title> — <severity>
- **OWASP**: <category>
- **CWE**: <id or n/a>
- **Location**: `<path>` (lines if known)
- **Issue**: <what can go wrong>
- **Exploit sketch**: <minimal attack path>
- **Fix**: <concrete change>
- **Verification**: <how to confirm fixed>

## Supply chain
- <package>: <advisory or concern>

## Residual risk
- <accepted risks with rationale>

## Cross-skill reporting
When combining outputs from sibling skills, normalize to this audit's severity scale:

| Source skill | Source field | Maps to |
|--------------|--------------|---------|
| secure-filesystem-access | `done/gap` + exploit path | high or medium |
| secure-filesystem-access | `gap` on write/TOCTOU/symlink | high |
| program-performance-optimizer | ROI Risk = high | medium (perf), not security unless guard removed |
| agentic-loop-engineer | Error code, Retryable=no + FS layer | align with finding above |
| Informational hardening only | — | low or info |

Do not merge FS threat tables verbatim into Findings; translate each `gap` row into an `<ID>-<title>` finding with OWASP/CWE.
```

## Escalation

- Ask which deployment model (local CLI, server, edge) and trust boundaries if unclear.
- Ask whether third-party APIs or user-uploaded files are in scope before deep SSRF/upload review.
- Proceed with static review when code is available; flag dynamic tests needed for race/TOCTOU items (see secure-filesystem-access).
- For new TS agent CLIs, run this auditor as the final review pass in `typescript-cli-architect/reference.md`.
