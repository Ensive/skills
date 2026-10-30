# Maintainer FAQ

Maintainer-written answers to four skill-selection questions. Start with the [router](router.md) for the full list; use the [boundary table](boundaries.md) to trace a handoff to its source. These answers summarize the linked files.

## Which skill implements a file-read path guard, and which audits it?

Use [secure-filesystem-access](../secure-filesystem-access/SKILL.md#when-to-use) to implement or repair workspace boundaries, path and symlink checks, and safe file-open mechanics. Once that pipeline exists, use [typescript-security-auditor](../typescript-security-auditor/SKILL.md#when-to-use) for the broader security review and OWASP/CWE findings. A finding that requires changing the path guard goes back to the filesystem skill.

## Which skill owns an HTTP 429 retry, and which owns a tool validation error?

Use [llm-client-architect](../llm-client-architect/SKILL.md#core-principles) for provider HTTP 429/5xx, including bounded retries, jitter, and `Retry-After`. [tool-registry-architect](../tool-registry-architect/SKILL.md#when-to-use) validates tool arguments before invoking the handler and returns a normalized error. [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md#core-principles) classifies that result and controls recovery; an argument/validation failure is non-retryable. Keep provider retry policy at the HTTP boundary.

## Which skill covers a fake LLM transport and a golden transcript?

Use [integration-tester](../integration-tester/SKILL.md#when-to-use) for a scripted model, real loop/tool wiring, and golden agent transcripts or CLI output. It calls for deterministic fixtures, normalized unstable fields, and checking that every scripted step was consumed. Use [typescript-unit-tester](../typescript-unit-tester/SKILL.md#when-to-use) for isolated helpers, parsers, and focused module tests.

## When is a new folder a new skill instead of a section in a neighbor?

A new skill needs its own trigger and an explicit out-of-scope line. If those boundaries match a neighbor, extend that skill instead. The [new-skill checklist](add-a-skill.md) requires `SKILL.md`, `name` and `description` frontmatter, a router entry, boundary rows for named handoffs, and a README entry in the same change. [AGENTS.md](../AGENTS.md) also requires scope edits to update the matching router section and boundary row in the same pull request.
