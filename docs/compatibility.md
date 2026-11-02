# Compatibility and official sources

Rechecked the Agent Skills specification and official OpenAI/Claude/Cursor documentation on **2026-11-01**; ecosystem installer references were verified on 2026-10-30. Documentation describes current behavior; installed assistant versions may lag it. These skills use only `name` and `description` frontmatter. No common invocation-policy, hook, tool-approval or dependency field is assumed across assistants.

| Surface | Route / status |
| --- | --- |
| Agent Skills format | Required frontmatter and local relative resources structurally tested; no claim of certification |
| Codex local CLI / native discovery | **Executed and passed**: 0.163.0 explicit integration-tester invocation and Python reference loading through a project `.agents/skills` link. Native `skills/list` additionally found all 14 owned `~/.codex/skills` symlinks exactly once, enabled at user scope, from two unrelated temporary projects, with zero discovery errors and no model turn. Automatic selection and all-skill task execution remain untested |
| Claude Code local CLI | **Executed and passed, limited smoke test**: 2.1.316, macOS, `claude-haiku-4-5-20251001`, `--effort low`. Explicit frontend-contract-engineer request completed; discovery listed the skill and the trace read its publishing reference through a user `.claude/skills` link. No separate SKILL.md read event was emitted for slash expansion. Project/user precedence, implicit routing and other skills remain untested |
| Cursor local CLI | **Executed and passed**: 2026.10.19-6bbf2c4, macOS, explicit frontend-contract-engineer request; read the skill and publishing reference through a project `.cursor/skills` symlink and produced a read-only fixture review. Implicit routing, other skills and editor UI untested; `.agents/skills` is a documented alternative |
| Assistant cloud/plugin distribution | Unsupported by this installer |
| Windows | Unsupported by this installer pending OS-specific tests |

Sources:

- [Agent Skills specification](https://agentskills.io/specification): frontmatter, naming and resource structure. The repository validator intentionally accepts a narrow YAML profile, not every legal YAML document or optional standard field.
- [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills): local discovery, symlinks, explicit/implicit invocation and plugin distribution guidance. The legacy developer documentation path redirects here. Optional `agents/openai.yaml` is unnecessary for this tranche.
- [Codex app server](https://learn.chatgpt.com/docs/app-server): native `skills/list` discovery with `cwds` and `forceReload`; no model turn is required for this check.
- [Claude Code skills](https://code.claude.com/docs/en/skills): project/user paths, linked folders and host-specific invocation behavior. Do not transfer Claude's optional frontmatter into other hosts without verification.
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config): model selection and effort controls; availability depends on the installed version, provider and account.
- [Cursor skills](https://cursor.com/docs/skills): local `.cursor/skills` and `.agents/skills`, recursive discovery and local/cloud differences. Local path compatibility does not imply automatic cloud availability.
- [Vercel skills CLI](https://github.com/vercel-labs/skills): ecosystem installer capabilities; considered but not required or executed.

Skills are workflow instructions and optional resources. Project instructions supply context. Executable tools perform actions under host permissions; MCP exposes external capabilities; hooks run at lifecycle events; runtime libraries belong to target applications. These packages request no additional tool permissions; actions remain subject to host permissions.

The Claude and Cursor tasks were read-only reviews of the synthetic publishing fixture. Both left fixture contents unchanged and supplied commands independently verified to pass its three tests; neither assistant ran those tests. Claude's single successful attempt took 20.9 seconds and reported $0.0505 usage under a $0.50 cap, with hooks/MCP disabled and Read/Glob/Grep/Skill tools only. User settings were enabled; a project link and a matching personal link were present, so this does not establish isolated project discovery or duplicate precedence. Earlier Claude 2.1.146 model-access failures are superseded only for this tested configuration, not diagnosed by it.

Use the [verification commands](../tests/README.md) and [behavioral evaluation procedure](../tests/evaluation.md) to reproduce checks; keep raw run artifacts local. A manual walkthrough or installed directory is not evidence of model routing or assistant-runtime compatibility. Python 3.12 is tested; Linux CI is configured but has not been executed here. Native Windows, WSL and cloud/editor surfaces were not runtime-tested. A successful explicit invocation does not establish automatic routing or reliability across the catalog.
