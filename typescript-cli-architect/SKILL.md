---
name: typescript-cli-architect
description: >-
  Designs TypeScript CLIs around the existing parser, process lifecycle and output contracts.
  Includes Node parseArgs and Bun binary examples. Use when building a CLI, fixing
  "exit code", SIGINT handling, argparse, "command-line tool", "parse argv",
  "stderr vs stdout", "broken pipe", "bun build --compile", or distributing a
  single-file binary.
---

# TypeScript CLI Architect

## Project discovery

Read applicable project instructions, manifests, nearby code/tests and CI. Discover paths, runtime, contracts, data restrictions and commands with working directories. Preserve existing stack choices; adapt the examples to those conventions. Use a reversible step when context is incomplete; ask only when behavior or authorization blocks it. Optional neighbors are not prerequisites.

## When to use

- User creates or refactors a Node/Bun TypeScript CLI entrypoint.
- User needs `--help`, `--version`, subcommands, or strict argv validation.
- User reports wrong exit codes, hung processes on Ctrl+C, or broken pipes.
- User pipes output to other tools or runs in CI without a TTY.
- User asks how to structure `main.ts`, error reporting, or logging for terminals.
- User packages the CLI as a Bun single-file binary via `bun build --compile`.

## Core principles

1. Reuse the existing CLI parser. For a new small Node CLI, `node:util` `parseArgs` is an implementation option with explicit options and positional policy.
2. Reserve exit code 0 for success; use 1 for general errors, 2 for misuse (optional convention).
3. Handle `SIGINT` and `SIGTERM`: flush, cancel in-flight work, exit once.
4. Write machine-readable output to stdout; diagnostics and logs to stderr.
5. Implement `--help` and `--version`; fail fast on unknown flags.
6. Detect `process.stdout.isTTY` before colors, spinners, or interactive prompts.
7. Avoid throwing past top-level `main`; map errors to exit codes at the boundary.
8. Support `EPIPE` on stdout when downstream closes early (e.g. `head`).
9. Keep side effects out of module top-level except minimal bootstrap.
10. Separate CLI UX from agent loops; see agentic-loop-engineer for tool orchestration.

## Checklist

- [ ] Define options, defaults and positional policy using the existing parser; use `parseArgs` as an option for a new small Node CLI.
- [ ] Print `--help` and `--version` to stdout (GNU-style); keep diagnostics and logs on stderr; document stream choice in `--help` footer.
- [ ] Implement `--version` from package.json or build metadata without network.
- [ ] Wrap `main()` in try/catch; set `process.exitCode` instead of scattered `exit()` where possible.
- [ ] Register signal handlers that abort controllers and await cleanup with timeout.
- [ ] Route errors: user message on stderr, optional `--json` errors on stdout if documented.
- [ ] Guard TTY-only features; degrade gracefully in CI and pipes.
- [ ] Handle `write` EPIPE without crashing on broken pipe.
- [ ] Document exit codes in README or `--help` footer.
- [ ] Verify Bun/Node shebang and `#!/usr/bin/env` if distributing binary.

## Patterns

**parseArgs with help/version (normal control flow, not errors)**

```typescript
import { parseArgs } from "node:util";

async function main(): Promise<void> {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    options: {
      help: { type: "boolean", short: "h" },
      version: { type: "boolean" },
      verbose: { type: "boolean", short: "v" },
    },
    allowPositionals: true,
  });

  if (values.help) {
    process.stdout.write(HELP_TEXT);
    return;
  }
  if (values.version) {
    process.stdout.write(`${PKG_VERSION}\n`);
    return;
  }
  await run(values, positionals);
}
```

`--help` and `--version` are not errors: write to stdout, return from `main`, and let `process.exitCode` stay at the default `0`. Do not call `process.exit` here — it skips pending stream flushes.

**EPIPE safety on stdout/stderr**

```typescript
for (const stream of [process.stdout, process.stderr] as const) {
  stream.on("error", (err: NodeJS.ErrnoException) => {
    if (err.code === "EPIPE") process.exit(0);
    else { process.exitCode = 1; /* report safely or invoke project error handler */ }
  });
}
```

Install this before any output. Pipelines like `mycli --help | head -n 1` now exit `0` silently instead of crashing with `ERR_STREAM_DESTROYED`/EPIPE.

**Signal-safe shutdown**

```typescript
const ac = new AbortController();
let shuttingDown = false;
for (const sig of ["SIGINT", "SIGTERM"] as const) {
  process.on(sig, () => {
    if (shuttingDown) return;
    shuttingDown = true;
    const exitCode = sig === "SIGINT" ? 130 : 143;
    process.exitCode = exitCode; // Preserve signal status even when cleanup finishes immediately.
    ac.abort();
    setTimeout(() => process.exit(exitCode), 5000).unref();
  });
}
```

**Exit code at boundary**

```typescript
async function main(): Promise<void> { /* ... */ }

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exitCode ??= 1; // Preserve a signal status already selected by shutdown.
});
```

**Non-TTY aware output**

```typescript
const useColor = process.stdout.isTTY && !process.env.NO_COLOR;
```

**Bun single-file binary**

```bash
bun build ./src/main.ts --compile --outfile dist/mycli
```

Shebang for source distribution (npm bin): `#!/usr/bin/env node` or `#!/usr/bin/env bun`. Compiled binaries embed the runtime — no shebang needed; mark the output executable in your release script. Resolve resources via `import.meta.dir` / `import.meta.url`, not `__dirname`, so paths work both when bundled and when compiled.

## Anti-patterns

- **Mixing log lines into stdout JSON** — breaks pipes; logs belong on stderr.
- **Ignoring signals** — zombie processes; register handlers and abort work.
- **Throwing from unhandled promise in CLI** — uncaught rejection; catch at `main`.
- **Hard-coded `process.exit()` deep in libraries** — untestable; set exitCode at top.
- **Interactive prompts when stdin is not TTY** — hangs CI; detect TTY first.
- **Changing parsers during an unrelated fix** — preserve the established option contract; evaluate a new parser only when parsing itself is the requested change.

## Output format

```markdown
# CLI design: <tool name>

## Interface
- Command: `<name> [options] [args...]>`
- Flags: <table>
- Exit codes: 0 = ...; 1 = ...; 2 = ...

## Streams
- stdout: <what>
- stderr: <what>

## Signals and cleanup
- <behavior>

## Implementation notes
- Entry: `<path>`
- Dependencies: <runtime>
```

## Escalation

- Discover runtime and distribution from package/build configuration; ask only for a new target the task requires.
- Preserve documented output behavior; clarify a requested incompatible stream-format change if unresolved.
- Preserve the existing parser; use `parseArgs` as an option for a new small CLI.
- Optional greenfield agent CLI composition example: [reference.md](reference.md).

## Tools and verification

Use existing tools and synthetic fixtures within the task's authorization. If execution is unavailable, provide the check and mark it unexecuted. Report changed artifacts, assumptions, exact commands/cwd, results and remaining gaps; verify the affected success/failure boundary and project conventions. Examples do not authorize downloads or external mutations.

## Handoffs

Required sibling skills: none. Local references are implementation examples, included with this skill.

- Optional: `agentic-loop-engineer` — Implement orchestration only for an agent CLI.
- Optional: `config-and-env-designer` — Load validated settings and explicit overrides.
- Optional: `llm-client-architect` — Wire a model adapter only when needed.
- Optional: `prompt-engineer` — Write prompt messages only when needed.
- Optional: `tool-registry-architect` — Define tool invocation contracts for agent tools.
- Optional: `secure-filesystem-access` — Implement workspace file operations.
- Optional: `observability-designer` — Design diagnostic events and sinks.
- Optional: `typescript-unit-tester` — Test parsing helpers and isolated functions with the established parser and runner.
- Optional: `integration-tester` — Test complete CLI behavior.
- Optional: `typescript-security-auditor` — Review exposed trust boundaries.
- Optional: `typescript-refactoring-architect` — Preserve behavior during structural changes.
