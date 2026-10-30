# Skill router

Choose the lane that matches the work, then open the linked skill. Summaries paraphrase each skill’s frontmatter; the skill and its reference file remain the source of truth. Handoffs below name only neighbors that those files explicitly name.

## Agent runtime

| Skill | Description |
| --- | --- |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Builds bounded agent tool loops with execution ordering, tool-error recovery, history budgets, and explicit stopping conditions. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md) | Defines typed tool schemas, capability gates, input validation, timeouts, normalized results, and invocation logs. |
| [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Implements safe agent and CLI file access with workspace boundaries, path and symlink checks, race defenses, bounded reads, and scoped caches. |
| [observability-designer](../observability-designer/SKILL.md) | Gives CLI, loop, model, and tool layers consistent structured logs, correlation IDs, metrics, trace boundaries, and shared redaction. |

## Model I/O

| Skill | Description |
| --- | --- |
| [llm-client-architect](../llm-client-architect/SKILL.md) | Builds provider adapters with HTTP timeouts, retries, model fallback, streaming, and secret redaction. |
| [prompt-engineer](../prompt-engineer/SKILL.md) | Writes role-specific prompts with output contracts, examples, reasoning boundaries, tool instructions, and refusal behavior. |

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
