# Cross-skill boundaries

Generated from each skill's Handoffs section and catalog required edges. Optional help and implementation examples are not installation dependencies. Return to the original task after a focused handoff; do not recursively load neighbors.

| Skill to leave | Relationship | Skill to open | Situation |
| --- | --- | --- | --- |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Own provider HTTP retries and protocol translation. |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [tool-registry-architect](../tool-registry-architect/SKILL.md) | Own schemas, invocation authorization and result classification. |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [prompt-engineer](../prompt-engineer/SKILL.md) | Own prompt wording and roles. |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Define event correlation and export policy. |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify loop behavior through real wiring. |
| [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#handoffs) | Optional | [typescript-cli-architect](../typescript-cli-architect/SKILL.md) | Map terminal outcomes to CLI exits when a CLI exists. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Choose recovery and termination from normalized outcomes. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Implement filesystem-capable handlers. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Keep redacted invocation diagnostics separate from allowlisted model-facing errors. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md#handoffs) | Optional | [prompt-engineer](../prompt-engineer/SKILL.md) | Review model-visible tool descriptions. |
| [tool-registry-architect](../tool-registry-architect/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify registry and application wiring. |
| [secure-filesystem-access](../secure-filesystem-access/SKILL.md#handoffs) | Optional | [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Review the wider threat model and severity for TypeScript systems. |
| [secure-filesystem-access](../secure-filesystem-access/SKILL.md#handoffs) | Optional | [program-performance-optimizer](../program-performance-optimizer/SKILL.md) | Measure a bottleneck before considering a scoped path cache. |
| [config-and-env-designer](../config-and-env-designer/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Consume approved provider settings and credentials. |
| [config-and-env-designer](../config-and-env-designer/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Enforce a configured workspace boundary. |
| [config-and-env-designer](../config-and-env-designer/SKILL.md#handoffs) | Optional | [typescript-cli-architect](../typescript-cli-architect/SKILL.md) | Wire explicit argv overrides and startup exits. |
| [config-and-env-designer](../config-and-env-designer/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Apply secret classification to exported logs. |
| [observability-designer](../observability-designer/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Instrument provider attempts and normalize reported usage. |
| [observability-designer](../observability-designer/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Emit loop progress and terminal reasons. |
| [observability-designer](../observability-designer/SKILL.md#handoffs) | Optional | [tool-registry-architect](../tool-registry-architect/SKILL.md) | Emit authorized invocation outcomes. |
| [observability-designer](../observability-designer/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify event ordering and correlation through application wiring. |
| [observability-designer](../observability-designer/SKILL.md#handoffs) | Optional | [program-performance-optimizer](../program-performance-optimizer/SKILL.md) | Investigate measured latency or resource bottlenecks. |
| [integration-tester](../integration-tester/SKILL.md#handoffs) | Optional | [typescript-unit-tester](../typescript-unit-tester/SKILL.md) | Test an isolated TypeScript helper. |
| [integration-tester](../integration-tester/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Repair a production filesystem guard. |
| [integration-tester](../integration-tester/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Repair loop ordering, retries or termination. |
| [integration-tester](../integration-tester/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Repair provider transport or partial-stream behavior. |
| [integration-tester](../integration-tester/SKILL.md#handoffs) | Optional | [frontend-contract-engineer](../frontend-contract-engineer/SKILL.md) | Repair UI state ownership or accessible interactions. |
| [frontend-contract-engineer](../frontend-contract-engineer/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify UI/API wiring, replay or browser flows. |
| [frontend-contract-engineer](../frontend-contract-engineer/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Instrument real interaction and rendering outcomes. |
| [frontend-contract-engineer](../frontend-contract-engineer/SKILL.md#handoffs) | Optional | [typescript-unit-tester](../typescript-unit-tester/SKILL.md) | Test an isolated TypeScript state/schema helper. |
| [frontend-contract-engineer](../frontend-contract-engineer/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Implement an explicitly requested model-provider adapter. |
| [llm-client-architect](../llm-client-architect/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Own tool retries, history and run termination. |
| [llm-client-architect](../llm-client-architect/SKILL.md#handoffs) | Optional | [prompt-engineer](../prompt-engineer/SKILL.md) | Author role messages and output instructions. |
| [llm-client-architect](../llm-client-architect/SKILL.md#handoffs) | Optional | [config-and-env-designer](../config-and-env-designer/SKILL.md) | Load approved endpoints, credentials and model policy. |
| [llm-client-architect](../llm-client-architect/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Exercise the client through the service or UI boundary. |
| [llm-client-architect](../llm-client-architect/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Own exported telemetry, redaction and cost-reporting semantics. |
| [prompt-engineer](../prompt-engineer/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Implement history and orchestration. |
| [prompt-engineer](../prompt-engineer/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Implement provider transport and capability checks. |
| [prompt-engineer](../prompt-engineer/SKILL.md#handoffs) | Optional | [tool-registry-architect](../tool-registry-architect/SKILL.md) | Enforce schemas and capability policy in code. |
| [prompt-engineer](../prompt-engineer/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Check prompt examples against actual tool fixtures. |
| [prompt-engineer](../prompt-engineer/SKILL.md#handoffs) | Optional | [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Review TypeScript trust boundaries and injection risks. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Implement orchestration only for an agent CLI. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [config-and-env-designer](../config-and-env-designer/SKILL.md) | Load validated settings and explicit overrides. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [llm-client-architect](../llm-client-architect/SKILL.md) | Wire a model adapter only when needed. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [prompt-engineer](../prompt-engineer/SKILL.md) | Write prompt messages only when needed. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [tool-registry-architect](../tool-registry-architect/SKILL.md) | Define tool invocation contracts for agent tools. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Implement workspace file operations. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [observability-designer](../observability-designer/SKILL.md) | Design diagnostic events and sinks. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [typescript-unit-tester](../typescript-unit-tester/SKILL.md) | Test parsing helpers and isolated functions with the established parser and runner. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Test complete CLI behavior. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Review exposed trust boundaries. |
| [typescript-cli-architect](../typescript-cli-architect/SKILL.md#handoffs) | Optional | [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md) | Preserve behavior during structural changes. |
| [typescript-unit-tester](../typescript-unit-tester/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify cross-module, UI/API or full agent/CLI flows using the project's existing runner. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [typescript-unit-tester](../typescript-unit-tester/SKILL.md) | Cover behavior at risk with existing tests or focused characterization at changed TypeScript seams. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [integration-tester](../integration-tester/SKILL.md) | Verify affected integration contracts. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Review changed authorization or validation boundaries. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Preserve filesystem policy when moving code. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [program-performance-optimizer](../program-performance-optimizer/SKILL.md) | Measure hot paths when performance is part of the task. |
| [typescript-refactoring-architect](../typescript-refactoring-architect/SKILL.md#handoffs) | Optional | [typescript-cli-architect](../typescript-cli-architect/SKILL.md) | Use the CLI composition example only for CLI work. |
| [typescript-security-auditor](../typescript-security-auditor/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Implement containment using the transport/OS filename contract; document race and platform limitations. |
| [typescript-security-auditor](../typescript-security-auditor/SKILL.md#handoffs) | Optional | [program-performance-optimizer](../program-performance-optimizer/SKILL.md) | Assess performance without weakening security. |
| [typescript-security-auditor](../typescript-security-auditor/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Check tool-error recovery against the threat model. |
| [typescript-security-auditor](../typescript-security-auditor/SKILL.md#handoffs) | Optional | [typescript-cli-architect](../typescript-cli-architect/SKILL.md) | Review CLI process and stream boundaries when present. |
| [program-performance-optimizer](../program-performance-optimizer/SKILL.md#handoffs) | Optional | [secure-filesystem-access](../secure-filesystem-access/SKILL.md) | Assess measured path-cache changes against filesystem threat assumptions. |
| [program-performance-optimizer](../program-performance-optimizer/SKILL.md#handoffs) | Optional | [typescript-security-auditor](../typescript-security-auditor/SKILL.md) | Review changed TypeScript security boundaries. |
| [program-performance-optimizer](../program-performance-optimizer/SKILL.md#handoffs) | Optional | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md) | Address agent history budgets and dependency ordering. |
