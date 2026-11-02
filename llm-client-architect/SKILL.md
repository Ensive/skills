---
name: llm-client-architect
description: Design TypeScript or Python provider adapters with explicit model capabilities, bounded retries, cancellation, streaming, fallback and usage attribution. Use when wiring or repairing model API clients; exclude prompt wording, tool execution policy and general application SSE unrelated to models.
---

# LLM Client Architect

## When to use

Implement or repair a model-provider boundary. Own protocol translation, request budgets, capabilities, provider errors and raw usage attribution. The application owns domain state; the client does not define tool authorization or loop termination.

## Discover and decide

Read applicable instructions, existing adapters/types, manifests/lockfiles, fake transports, deployment constraints and approved providers. Verify the installed SDK and official provider contract before changing wire formats. Record modalities, tools, structured output, streaming, context limits, residency and latency/cost constraints.

Reuse the existing provider/SDK when suitable. OpenAI-compatible HTTP is an example, never a default for an unspecified provider. If selection is unresolved, implement the internal boundary and fake transport; ask only for provider/data-transfer decisions that block integration. Missing credentials do not block offline tests.

## Workflow

1. Produce an **adapter contract** in project types: messages, tool calls, deltas, terminal states, errors and usage. Translate provider fields at the adapter, not the registry. Define a capability map with evidence/version and explicit unsupported states.
2. Define a **resilience table** by operation/error: retry eligibility, attempt cap, total deadline, connect/read limits, cancellation and idempotency. Account for SDK retries so layers do not multiply attempts. Auth, invalid arguments and unsupported capabilities do not automatically retry or switch models.
3. Respect Retry-After. If its delay exceeds the remaining deadline, stop or schedule later rather than clamping it downward. Cancellation interrupts requests and backoff. A timeout may have incurred cost or side effects; uncertainty does not establish retry safety.
4. Define **stream transitions**: unopened → active → completed/failed/cancelled. Parse incrementally with bounded buffers/backpressure and close resources. After partial delivery, surface an incomplete result; restart/fallback needs application policy preventing duplicate text, actions and charges. Read [transport recipes](references/transports.md).
5. Fallback only to approved models satisfying capabilities, privacy/residency and quality constraints. Preserve attempted/selected IDs. Capture usage per attempt, reconcile terminal totals and distinguish unknown/estimated/reported. Cost estimates need a dated pricing source.
6. Produce **implementation and tests**: injected transports, fragmented/malformed frames, deadlines, cancellation during request/backoff, exhausted attempts, unsupported models, partial output and missing usage. Read [provider verification](references/providers.md). Report exact commands/results and unverified live behavior.

## Tools and acceptance

Needs repository reading and existing runtime/test tools. Without documentation access, preserve known contracts and label unresolved APIs. Paid calls, credentials, external deployment and data transfer require authorization beyond a fake test.

Accept when project types are preserved, unsupported capabilities fail explicitly, time/attempts/buffering are bounded, cancellation releases resources and partial work never restarts silently. Test synthetic secrets in errors/headers; prefer allowlisted metadata to arbitrary-body redaction.

## Handoffs

Required sibling skills: none.

- Optional: `agentic-loop-engineer` — Own tool retries, history and run termination.
- Optional: `prompt-engineer` — Author role messages and output instructions.
- Optional: `config-and-env-designer` — Load approved endpoints, credentials and model policy.
- Optional: `integration-tester` — Exercise the client through the service or UI boundary.
- Optional: `observability-designer` — Own exported telemetry, redaction and cost-reporting semantics.
