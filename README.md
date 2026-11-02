# Reusable engineering skills

Owned workflows for TypeScript applications, Python AI services, agent runtimes and frontend/publishing work. Start with the target repository's conventions; add only the skills your task needs. No provider, backend, frontend framework or deployment platform is required across the catalog.

1. Start with the [worked usage example](docs/usage.md), or choose a workflow in the [router](docs/router.md). The [boundary table](docs/boundaries.md) and [maintainer FAQ](docs/maintainer-faq.md) explain handoffs.
2. Keep project facts in existing instructions or the small [context template](docs/project-context.md). Shared skill instructions stay unchanged across projects.
3. Use the [local installation guide](docs/installation.md) for Codex, Claude Code or Cursor. Install one skill or a selected bundle from a pinned checkout.
4. Give the assistant a concrete outcome and acceptance criteria, then inspect its evidence and unexecuted checks.

Example: “Use integration-tester to verify cancellation in this service. Follow the repository's test command and use synthetic provider responses.” The same workflow can test a TypeScript UI, a Python API or a static publishing interface by discovering each project's boundaries.

## Catalog

Integration testing, observability, configuration and model clients have complete workflow contracts with conditional stack references. Nine specialist skills retain their technical scope with discovery and verification guidance. `frontend-contract-engineer` covers frontend contracts and publishing interfaces. All 14 can be installed independently with their local references; no required sibling skills exist.

<!-- catalog:start -->
| Skill | Purpose and trigger |
| --- | --- |
| [agentic-loop-engineer](agentic-loop-engineer/SKILL.md) | Engineers reliable agent tool-calling loops with iteration caps, parallel vs sequential execution, tool-class retry classification, tool-error shaping, history growth control, token budgets, and deterministic termination. |
| [tool-registry-architect](tool-registry-architect/SKILL.md) | Designs the tool registry for an agent runner: typed tool schemas (Zod or JSON Schema), capability flags (read/write/exec/network), input validation, per-tool timeouts with AbortSignal propagation, normalized result shape, and audit logging. |
| [secure-filesystem-access](secure-filesystem-access/SKILL.md) | Designs and reviews safe filesystem access for agents and CLIs: workspace roots, input-boundary decoding, control-byte rejection, realpath and symlink escape defenses, O_NOFOLLOW, same-descriptor metadata checks with explicit race limitations, bounded reads, write-parent checks, threat-aware scoped caches, size and MIME guards, temp-directory isolation, and sandbox options (subprocess, container, chroot). |
| [config-and-env-designer](config-and-env-designer/SKILL.md) | Design validated configuration and secret handling for TypeScript or Python applications. |
| [observability-designer](observability-designer/SKILL.md) | Design logs, metrics and traces for browser, service, CLI and AI workflows in TypeScript or Python. |
| [integration-tester](integration-tester/SKILL.md) | Design and run deterministic integration tests across real application boundaries in TypeScript or Python, including UI interactions, API contracts, agent flows and stream cancellation. |
| [frontend-contract-engineer](frontend-contract-engineer/SKILL.md) | Implement or repair an existing frontend or publishing interface from explicit state, content and interaction contracts. |
| [llm-client-architect](llm-client-architect/SKILL.md) | Design TypeScript or Python provider adapters with explicit model capabilities, bounded retries, cancellation, streaming, fallback and usage attribution. |
| [prompt-engineer](prompt-engineer/SKILL.md) | Crafts system, user, and tool-role prompts with structured outputs, few-shot examples, chain-of-thought boundaries, JSON contracts, and safe refusal patterns. |
| [typescript-cli-architect](typescript-cli-architect/SKILL.md) | Designs TypeScript CLIs around the existing parser, process lifecycle and output contracts. |
| [typescript-unit-tester](typescript-unit-tester/SKILL.md) | Writes and reviews TypeScript unit tests using the project's existing runner, boundary mocks and deterministic fixtures. |
| [typescript-refactoring-architect](typescript-refactoring-architect/SKILL.md) | Plans and executes behavior-preserving TypeScript refactors for modularity and reusability: existing coverage or focused characterization, small mechanical steps, module boundary and public-export discipline, dependency direction, dead-code and circular-dep detection, generic-type reusability, dependency injection at adapter seams, and codemods via ts-morph or jscodeshift. |
| [typescript-security-auditor](typescript-security-auditor/SKILL.md) | Audits TypeScript and Node.js code for OWASP Top 10 risks including injection, prototype pollution, SSRF, secret leakage, and supply-chain exposure. |
| [program-performance-optimizer](program-performance-optimizer/SKILL.md) | Optimizes programs by measuring first, identifying hot paths, and applying async I/O, caching tiers, and batching with ROI-ranked recommendations—never trading away correctness or security for speed. |
<!-- catalog:end -->

## Maintenance and evidence

```bash
python3 scripts/catalog.py
python3 -m unittest discover -s tests -v
```

Python 3.12+ is supported for repository tooling. See [contributing](CONTRIBUTING.md), [architecture](docs/architecture.md), [follow-up work](https://github.com/Ensive/skills/issues), and [verification procedure](tests/README.md). Assistant documentation sources and compatibility levels are in [compatibility](docs/compatibility.md).

Owned content is [MIT licensed](LICENSE). The skill distribution contains only catalog-owned packages; ignored third-party installations remain local and untracked. See [provenance](docs/provenance.md) for source and data restrictions.
