# Skill router

Choose the lane that matches the work, then open the linked skill. Summaries paraphrase each skill’s frontmatter; the skill and its reference file remain the source of truth. Handoffs below name only neighbors that those files explicitly name.

## Agent runtime

| Skill | Description |
| --- | --- |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Builds bounded agent tool loops with execution ordering, tool-error recovery, history budgets, and explicit stopping conditions. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md) | Defines typed tool schemas, capability gates, input validation, timeouts, normalized results, and invocation logs. |
| [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Implements safe agent and CLI file access with workspace boundaries, path and symlink checks, race defenses, bounded reads, and scoped caches. |
| [observability-designer](../observability-designer/SKILL.md) | Gives CLI, loop, model, and tool layers consistent structured logs, correlation IDs, metrics, trace boundaries, and shared redaction. |

### Agentic Loop Engineer

**Use this when:** You are building the model/tool execution loop, fixing repeated calls or runaway history, choosing parallel versus dependent execution, shaping tool failures, or setting token budgets and stop conditions. This skill owns tool argument/validation failure classification and tool-class backoff; validation failures are non-retryable.

**Hand off:**

- [llm-client-architect](../llm-client-architect/SKILL.md): Handle provider HTTP 429/5xx, HTTP retry/backoff, and shared log redaction.
- [tool-registry-architect](../tool-registry-architect/SKILL.md): Define tool schemas and capability flags, and use the registry error taxonomy with the shared normalized result contract.
- [prompt-engineer](../prompt-engineer/SKILL.md): Write prompt wording and assign message roles.
- [observability-designer](../observability-designer/SKILL.md): Define the per-iteration NDJSON log fields.
- [integration-tester](../integration-tester/SKILL.md): Exercise the loop through fake transport tests that share the canonical agent types.
- [typescript-cli-architect](../typescript-cli-architect/SKILL.md): Map CLI exit codes or consult the reference composition chain for a new agent CLI.

Source: [agentic-loop-engineer/SKILL.md](../agentic-loop-engineer/SKILL.md); [agentic-loop-engineer/reference.md](../agentic-loop-engineer/reference.md).

### Tool Registry Architect

**Use this when:** You are adding tools, validating model arguments before handlers run, gating read/write/exec/network capabilities, propagating cancellation through per-tool timeouts, or normalizing tool results. Registry validation returns a shaped, non-retryable failure.

**Hand off:**

- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Use the canonical tool-call/result types and let the loop classify results and decide recovery.
- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): Implement filesystem handlers with the shared path and bounded-read helpers from its reference contract.
- [llm-client-architect](../llm-client-architect/SKILL.md): Reuse the shared redaction rules for invocation logs.
- [prompt-engineer](../prompt-engineer/SKILL.md): Review model-visible schema and capability descriptions as prompt text.
- [integration-tester](../integration-tester/SKILL.md): Test the full loop and registry wiring.

Source: [tool-registry-architect/SKILL.md](../tool-registry-architect/SKILL.md).

### Secure Filesystem Access

**Use this when:** You are implementing or fixing file-read, write, list, or delete tools; path traversal or symlink defenses; race-resistant opens; workspace isolation; or file size and type policies. This is the implementation owner for the path guard.

**Hand off:**

- [typescript-security-auditor](../typescript-security-auditor/SKILL.md): After the filesystem pipeline exists, perform the wider OWASP review and translate threat-coverage gaps into severity-ranked OWASP/CWE findings.
- [program-performance-optimizer](../program-performance-optimizer/SKILL.md): Measure whether a hot read path warrants the scoped realpath cache before adding it.

Source: [secure-filesystem-access/SKILL.md](../secure-filesystem-access/SKILL.md); [secure-filesystem-access/reference.md#scoped-realpath-cache-perf-safe](../secure-filesystem-access/reference.md#scoped-realpath-cache-perf-safe); [secure-filesystem-access/reference.md#threat-coverage-template](../secure-filesystem-access/reference.md#threat-coverage-template).

### Observability Designer

**Use this when:** You need consistent logs, metrics, or traces across the CLI, loop, model client, and tools; correlation across one invocation; stable aggregator fields; or normalized timestamps and IDs for golden output.

**Hand off:**

- [llm-client-architect](../llm-client-architect/SKILL.md): Implement or import the shared safeBody redactor and instrument model request start/end events.
- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Emit iteration start/end events with tool counts, token usage, and duration from the loop.
- [tool-registry-architect](../tool-registry-architect/SKILL.md): Emit tool-call start/end events with the tool, call ID, outcome, and duration.
- [integration-tester](../integration-tester/SKILL.md): Use normalized timestamps and IDs in integration golden comparisons.

Source: [observability-designer/SKILL.md](../observability-designer/SKILL.md).

## Model I/O

| Skill | Description |
| --- | --- |
| [llm-client-architect](../llm-client-architect/SKILL.md) | Builds provider adapters with HTTP timeouts, retries, model fallback, streaming, and secret redaction. |
| [prompt-engineer](../prompt-engineer/SKILL.md) | Writes role-specific prompts with output contracts, examples, reasoning boundaries, tool instructions, and refusal behavior. |

### LLM Client Architect

**Use this when:** You are adding or changing a provider HTTP adapter, handling rate limits and fallback, streaming responses, or redacting credentials. Provider HTTP 429/5xx retries belong here, including backoff, jitter, and Retry-After handling.

**Hand off:**

- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Handle tool-class retries, history, and termination; use its shared normalized call/result types at the adapter boundary.
- [prompt-engineer](../prompt-engineer/SKILL.md): Author prompt wording.
- [config-and-env-designer](../config-and-env-designer/SKILL.md): Load base URL, default model, and headers through centralized configuration.
- [integration-tester](../integration-tester/SKILL.md): Exercise injected transport/fetch hooks in integration tests.
- [observability-designer](../observability-designer/SKILL.md): Reuse the exported safeBody function in the shared observability layer.

Source: [llm-client-architect/SKILL.md](../llm-client-architect/SKILL.md).

### Prompt Engineer

**Use this when:** You are writing or revising role-based messages, strict output contracts, tool-use instructions, examples, reasoning visibility, or refusal behavior.

**Hand off:**

- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Implement loop orchestration and history mechanics.
- [llm-client-architect](../llm-client-architect/SKILL.md): Implement provider HTTP behavior and retry policy.
- [tool-registry-architect](../tool-registry-architect/SKILL.md): Define tool schemas and capability allowlists; prompt instructions describe behavior without duplicating the registry gates.
- [integration-tester](../integration-tester/SKILL.md): Cross-check tool names in examples against the actual registry fixtures.
- [typescript-security-auditor](../typescript-security-auditor/SKILL.md): Review the broader threat model for injection and tool-mediated exfiltration.

Source: [prompt-engineer/SKILL.md](../prompt-engineer/SKILL.md).

## TypeScript delivery

| Skill | Description |
| --- | --- |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md) | Builds TypeScript command-line interfaces with argument parsing, exit codes, signal handling, reliable streams, and binary packaging. |
| [config-and-env-designer](../config-and-env-designer/SKILL.md) | Defines validated, typed startup configuration with explicit defaults and separate handling for secrets and settings. |
| [typescript-unit-tester](../typescript-unit-tester/SKILL.md) | Tests TypeScript modules with Bun or Vitest using focused assertions, boundary mocks, deterministic inputs, and coverage goals. |
| [integration-tester](../integration-tester/SKILL.md) | Tests complete agent and CLI flows with scripted model transports, tool fixtures, golden comparisons, and flake controls. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md) | Preserves behavior while improving TypeScript module boundaries, reuse, dependency direction, and public APIs through tested mechanical changes. |
| [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Reviews TypeScript and Node.js for OWASP risks such as injection, prototype pollution, SSRF, secret exposure, and unsafe dependencies. |
| [program-performance-optimizer](../program-performance-optimizer/SKILL.md) | Measures bottlenecks before ranking and applying I/O, caching, and batching improvements that preserve correctness and security. |
