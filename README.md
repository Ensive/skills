# Owned agent skills

This repository holds the 13 owned agent skills for TypeScript agent runtimes. Folder names listed in `.gitignore` are local skill installs and are not part of this repository.

| Folder | Skill name | Description |
| --- | --- | --- |
| [agentic-loop-engineer](agentic-loop-engineer/) | Agentic Loop Engineer | Builds bounded agent tool loops with execution ordering, tool-error recovery, history budgets, and explicit stopping conditions. |
| [tool-registry-architect](tool-registry-architect/) | Tool Registry Architect | Defines typed tool schemas, capability gates, input validation, timeouts, normalized results, and invocation logs. |
| [secure-filesystem-access](secure-filesystem-access/) | Secure Filesystem Access | Implements safe agent and CLI file access with workspace boundaries, path and symlink checks, race defenses, bounded reads, and scoped caches. |
| [observability-designer](observability-designer/) | Observability Designer | Gives CLI, loop, model, and tool layers consistent structured logs, correlation IDs, metrics, trace boundaries, and shared redaction. |
| [llm-client-architect](llm-client-architect/) | LLM Client Architect | Builds provider adapters with HTTP timeouts, retries, model fallback, streaming, and secret redaction. |
| [prompt-engineer](prompt-engineer/) | Prompt Engineer | Writes role-specific prompts with output contracts, examples, reasoning boundaries, tool instructions, and refusal behavior. |
| [typescript-cli-architect](typescript-cli-architect/) | TypeScript CLI Architect | Builds TypeScript command-line interfaces with argument parsing, exit codes, signal handling, reliable streams, and binary packaging. |
| [config-and-env-designer](config-and-env-designer/) | Config and Env Designer | Defines validated, typed startup configuration with explicit defaults and separate handling for secrets and settings. |
| [typescript-unit-tester](typescript-unit-tester/) | TypeScript Unit Tester | Tests TypeScript modules with Bun or Vitest using focused assertions, boundary mocks, deterministic inputs, and coverage goals. |
| [integration-tester](integration-tester/) | Integration Tester | Tests complete agent and CLI flows with scripted model transports, tool fixtures, golden comparisons, and flake controls. |
| [typescript-refactoring-architect](typescript-refactoring-architect/) | TypeScript Refactoring Architect | Preserves behavior while improving TypeScript module boundaries, reuse, dependency direction, and public APIs through tested mechanical changes. |
| [typescript-security-auditor](typescript-security-auditor/) | TypeScript Security Auditor | Reviews TypeScript and Node.js for OWASP risks such as injection, prototype pollution, SSRF, secret exposure, and unsafe dependencies. |
| [program-performance-optimizer](program-performance-optimizer/) | Program Performance Optimizer | Measures bottlenecks before ranking and applying I/O, caching, and batching improvements that preserve correctness and security. |

Start with the [skill router](docs/router.md) to choose a skill. Use the [cross-skill boundary table](docs/boundaries.md) when work changes owners, and the [new-skill checklist](docs/add-a-skill.md) when adding a folder.
