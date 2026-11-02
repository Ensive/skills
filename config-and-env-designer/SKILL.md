---
name: config-and-env-designer
description: Design validated configuration and secret handling for TypeScript or Python applications. Use for startup failures, environment schemas, precedence and client/server settings boundaries; exclude provisioning secrets, adding a backend to a static site and provider transport implementation.
---

# Config and Env Designer

## When to use

Introduce or repair runtime/build configuration, validation, precedence or secret separation. Own loading and failure behavior. A static site may need only public build settings; configuration work is not a reason to add a service or API key.

## Discover and decide

Read applicable instructions, runtime versions, manifests, current loaders, build tooling, CI and deployment injection. Find consumers before defining variables. Record precedence, when values are read, public/server boundaries, required settings and command/cwd. Inspect schema library versions before copying an API.

Preserve working precedence and dependencies. Default only non-secret values with safe, documented behavior. Require credentials for optional features only when enabled. Missing deployment details allow an injectable local loader; unknown public exposure blocks shipping that value to a browser.

## Workflow

1. Produce a **configuration inventory**: key, type, source, owner, secret/public status, required condition, default and consumer. Include rotation/reload needs if present.
2. Define precedence from the application's contract. An argv → environment → defaults order is a CLI example, not a universal rule. Distinguish unset/empty and parse booleans/numbers intentionally.
3. Implement a loader at the appropriate entry boundary and pass validated settings to consumers. Use existing dependency injection/lifecycle; a process singleton is optional. Load [TypeScript/Python examples](references/loaders.md) only where relevant.
4. Keep secrets out of browser bundles, public prefixes, committed examples, logs and validation errors. Report field names and safe error codes, not rejected values. Type annotations alone do not sanitize objects at runtime.
5. Produce **loader changes**, a synthetic **example configuration** and **startup behavior documentation**. Do not change a developer's real environment or secret store.
6. Verify missing/empty/invalid values, precedence, disabled features, public exposure and safe failures with isolated mappings. Run discovered checks; list unexecuted deployment checks separately.

## Tools and acceptance

Requires repository reading and local test tools for verification. Synthetic values suffice; secret-store access is unnecessary for designing a loader. If the runtime is unavailable, provide unexecuted tests. Provisioning/rotation needs separate authorization.

Accept when invalid required settings fail at the documented boundary, isolated tests avoid environment leakage, secrets cannot reach public output, and each default has a reason. Watch for truthy `"false"`, import-time reads, empty input coerced to zero and entire validator exceptions in logs.

## Handoffs

Required sibling skills: none.

- Optional: `llm-client-architect` — Consume approved provider settings and credentials.
- Optional: `secure-filesystem-access` — Enforce a configured workspace boundary.
- Optional: `typescript-cli-architect` — Wire explicit argv overrides and startup exits.
- Optional: `observability-designer` — Apply secret classification to exported logs.
