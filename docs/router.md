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

### TypeScript CLI Architect

**Use this when:** You are building or restructuring a Node/Bun entrypoint, parsing flags or subcommands, fixing exits/signals/broken pipes, supporting CI and non-TTY output, or packaging a compiled CLI.

**Hand off:**

The [reference composition chain](../typescript-cli-architect/reference.md#composition-chain-new-ts-agent-cli) orders assembly of a new agent CLI. Its destinations below apply to that broader task; a focused CLI edit uses the relevant boundary.

- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Implement agent tool orchestration behind the CLI and use the runner stage of the composition chain.
- [config-and-env-designer](../config-and-env-designer/SKILL.md): For a new agent CLI, start the composition chain with a validated config schema, separate secrets, and fail-fast loading.
- [llm-client-architect](../llm-client-architect/SKILL.md): In the composition chain, build the provider adapter that emits the shared normalized types.
- [prompt-engineer](../prompt-engineer/SKILL.md): In the composition chain, write the system prompt, tool preamble, and refusals.
- [tool-registry-architect](../tool-registry-architect/SKILL.md): In the composition chain, define tool schemas, capability flags, and per-tool timeouts.
- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): In the composition chain, implement filesystem-capable tools with the shared FS helpers.
- [observability-designer](../observability-designer/SKILL.md): In the composition chain, wire NDJSON logging and correlation with the shared redactor.
- [typescript-unit-tester](../typescript-unit-tester/SKILL.md): At the test stage of the composition chain, cover pure functions and parsers.
- [integration-tester](../integration-tester/SKILL.md): At the integration stage of the composition chain, cover fake-model end-to-end transcripts and goldens.
- [typescript-security-auditor](../typescript-security-auditor/SKILL.md): Finish the composition chain with the security review before release.
- [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md): For maintenance, refactor first, then re-enter the composition chain at its unit, integration, and audit passes.

Source: [typescript-cli-architect/SKILL.md](../typescript-cli-architect/SKILL.md); [typescript-cli-architect/reference.md#composition-chain-new-ts-agent-cli](../typescript-cli-architect/reference.md#composition-chain-new-ts-agent-cli).

### Config and Env Designer

**Use this when:** You are introducing environment variables or config files, validating typed configuration at startup, separating secrets from feature flags, defining defaults/profiles, or fixing configuration that fails only after deployment.

**Hand off:**

- [llm-client-architect](../llm-client-architect/SKILL.md): Feed provider keys and endpoints into the client and check secret names against its logging redaction.
- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): Pass workspace roots to the filesystem implementation.
- [typescript-cli-architect](../typescript-cli-architect/SKILL.md): Coordinate explicit argv overrides with parseArgs and follow the reference composition order; precedence is argv, then env, then schema defaults.

Source: [config-and-env-designer/SKILL.md](../config-and-env-designer/SKILL.md).

### TypeScript Unit Tester

**Use this when:** You are testing isolated TypeScript modules, parsers, or pure functions, choosing Bun/Vitest, controlling time and randomness, or adding boundary mocks and characterization tests before a refactor.

**Hand off:**

- [integration-tester](../integration-tester/SKILL.md): Move full agent/CLI flows, fake LLM transports, golden transcripts, and golden CLI output to the integration suite.

Source: [typescript-unit-tester/SKILL.md](../typescript-unit-tester/SKILL.md).

### Integration Tester

**Use this when:** You need an end-to-end prompt/model/tool/final-answer scenario, a scripted or fake LLM transport, tool fixtures, golden agent transcripts or CLI output, or control of ordering and timing flakes. This skill owns the fake transport and golden transcript; the harness verifies that all scripted steps were consumed.

**Hand off:**

- [typescript-unit-tester](../typescript-unit-tester/SKILL.md): Test pure helpers separately and reuse its deterministic time, randomness, and environment practices.
- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): Isolate test workspaces and temporary directories per scenario.
- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Import the shared NormalizedToolCall and LlmResponse types for the scripted transport.

Source: [integration-tester/SKILL.md](../integration-tester/SKILL.md).

### TypeScript Refactoring Architect

**Use this when:** You are changing TypeScript structure while preserving behavior: extracting modules or reusable abstractions, untangling dependencies, or moving/renaming public APIs. Pin behavior with characterization tests before taking small mechanical steps.

**Hand off:**

- [typescript-unit-tester](../typescript-unit-tester/SKILL.md): Write characterization tests before changing structure.
- [integration-tester](../integration-tester/SKILL.md): Run integration coverage after each step, following build, type-check, and unit tests.
- [typescript-security-auditor](../typescript-security-auditor/SKILL.md): Review security-sensitive changes and proposed removal of validation, capability gates, or path guards.
- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): Preserve the filesystem implementation and move path checks with the code that needs them.
- [program-performance-optimizer](../program-performance-optimizer/SKILL.md): Run the performance pass when the refactor touches hot paths or calls for performance work.
- [typescript-cli-architect](../typescript-cli-architect/SKILL.md): Consult the reference composition chain when deciding the target layering.

Source: [typescript-refactoring-architect/SKILL.md](../typescript-refactoring-architect/SKILL.md).

### TypeScript Security Auditor

**Use this when:** You need a TypeScript/Node security review, threat model, OWASP/CWE mapping, or examination of dependencies, outbound HTTP, uploads, shell execution, secrets, or prototype pollution. Audit an existing filesystem pipeline here; implement or fix its path guard through the filesystem skill.

**Hand off:**

- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): Implement or repair safe file opens and path guards, and verify filesystem race/TOCTOU concerns with the canonical pipeline.
- [program-performance-optimizer](../program-performance-optimizer/SKILL.md): Consult performance work without weakening security; its high ROI risk is a performance concern unless a guard was removed.
- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Use the loop error code, FS layer, and non-retryable classification as evidence when aligning the audit finding.
- [typescript-cli-architect](../typescript-cli-architect/SKILL.md): Consult the reference composition chain to place the audit as the final review for a new agent CLI.

Source: [typescript-security-auditor/SKILL.md](../typescript-security-auditor/SKILL.md).

### Program Performance Optimizer

**Use this when:** You need to investigate latency, CPU, memory, or slow agent reads, or assess caching, batching, pooling, and parallel I/O. Measure a baseline and profile hot paths first, then rank changes by impact, effort, and risk; preserve validation and security checks.

**Hand off:**

- [secure-filesystem-access](../secure-filesystem-access/SKILL.md): After measuring slow file reads, implement its request/turn-scoped realpath cache, invalidated on writes or root changes, while retaining prefix, realpath, and fd-stat checks.
- [typescript-security-auditor](../typescript-security-auditor/SKILL.md): Check that performance work preserves correctness, authorization, and security.
- [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): Address history pruning for token cost and respect dependency ordering before parallelizing tool work.

Source: [program-performance-optimizer/SKILL.md](../program-performance-optimizer/SKILL.md).
