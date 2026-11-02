# Skill architecture

## Decision

Keep one owned source at the existing top-level skill paths. A skill's `SKILL.md` owns its description, triggers and optional handoffs. Its local references contain specialist recipes. Target project instructions supply conventions and domain constraints. Assistant discovery and installation belong in repository documentation, not in each workflow.

`catalog.json` is only an ownership, lane and bundle manifest. It is not assistant metadata or a runtime dependency resolver. The validation script derives README, router and boundary sections from the skill text; it checks required edges for cycles. All current skills have **no required sibling skills**. Cross-skill help is optional; names resolve through the host's available skills. Local Markdown references are required resources bundled with their own skill.

Do not recursively load handoffs. Load a neighbor only when the task crosses that boundary and the neighbor is available. An implementation example demonstrates a possible shape; it does not require its library, path, provider, runtime or sibling skill. No shared runtime library, hooks, MCP configuration or new assistant metadata is introduced.

## Workflow coverage

| Skill | Coverage |
| --- | --- |
| integration-tester | Full contract migration: TypeScript, Python/FastAPI and browser/publishing integration; local recipes |
| observability-designer | Full contract migration: browser, service and CLI sinks; TypeScript/Python context; honest usage |
| config-and-env-designer | Full contract migration: repository discovery, TypeScript/Python loaders, client/server secrets |
| llm-client-architect | Full contract migration: explicit provider, capabilities, retry budgets, partial streams and attribution |
| Other nine owned names | Focused discovery/permission/handoff repairs and correction of demonstrated unsafe assumptions; retain TypeScript recipes and existing scope |
| frontend-contract-engineer | One focused workflow for implementing existing frontend contracts, accessible interactions and publishing layouts; React and static-site references |

The TypeScript CLI, unit-test, refactoring and security names remain TypeScript-specific. Filesystem recipes remain explicitly Node/POSIX-oriented; broader OS and Python implementations require further verification. Python support is concentrated where service testing, configuration, clients and instrumentation need it.

## Installation choice

Compared the official assistant folder routes and [Vercel's skills CLI](https://github.com/vercel-labs/skills) on 2026-10-30. The ecosystem CLI supplies discovery, agent selection, updates/removal and lock tooling, but introduces a Node dependency and additional installation state. Its broader lifecycle is useful for large catalogs; this repository only needs selected folders from a pinned local checkout.

Choose a small standard-library Python **link installer**, with explicit source and destination, preview by default, preflight conflicts, repeatable links and guarded removal. It neither downloads code nor changes settings. Full skill directories remain at one canonical source. Updates are an explicit reviewed change of the source checkout's commit; the installer reports its revision and dirty state. Local edits remain visible there rather than diverging in copies. Symlink support on a filesystem is required; copy-based and cloud/plugin distribution remain unsupported by this installer.

This is a deliberate local installation route, not a plugin marketplace implementation. Plugin packaging is deferred until distribution demand justifies another release surface. The repository now carries the maintainer's MIT license. Assistant runtimes must be tested separately from creating links in their documented directories.
