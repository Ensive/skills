# TypeScript CLI composition example

Use this only when building an agent CLI. First discover the target repository; an existing frontend, service or library keeps its own architecture. This sequence is an **implementation example**, not required sibling loading. No skill dependency is introduced, and missing neighbors do not require generating unused stubs.

1. Establish validated configuration and the CLI's flags, streams, exits and cancellation boundary.
2. If models are required, wire the existing provider adapter and project message/tool contracts.
3. If an agent loop is required, define bounded orchestration and tool invocation authorization.
4. If filesystem tools exist, establish their OS-specific containment and size limits.
5. Connect diagnostics through the project's logger/export policy. NDJSON/stderr and AsyncLocalStorage are Node CLI options.
6. Verify parser behavior, affected integration flows and exposed security boundaries using installed tools.

Optional help for these concerns is enumerated in [SKILL.md](SKILL.md) under Handoffs. Follow only the relevant boundary and return to the task. For maintenance, pin affected behavior before a structural change; do not force the rest of a greenfield assembly sequence onto a small edit.
