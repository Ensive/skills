---
name: typescript-cli-architect
description: >-
  Architects robust TypeScript CLIs using node:util parseArgs, exit codes, signal
  handling, stdout/stderr discipline, EPIPE safety, help/version flags, non-TTY
  behavior, and Bun-compiled single-file binaries. Use when building a CLI, fixing
  "exit code", SIGINT handling, argparse, "command-line tool", "parse argv",
  "stderr vs stdout", "broken pipe", "bun build --compile", or distributing a
  single-file binary.
---

# TypeScript CLI Architect

## When to use

- User creates or refactors a Node/Bun TypeScript CLI entrypoint.
- User needs `--help`, `--version`, subcommands, or strict argv validation.
- User reports wrong exit codes, hung processes on Ctrl+C, or broken pipes.
- User pipes output to other tools or runs in CI without a TTY.
- User asks how to structure `main.ts`, error reporting, or logging for terminals.
- User packages the CLI as a Bun single-file binary via `bun build --compile`.

## Core principles

1. Use `node:util` `parseArgs` with explicit `options` and `allowPositionals` policy.
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

- [ ] Define `parseArgs` schema: booleans, strings, defaults, and positional rules.
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
  });
}
```

Install this before any output. Pipelines like `mycli --help | head -n 1` now exit `0` silently instead of crashing with `ERR_STREAM_DESTROYED`/EPIPE.

**Signal-safe shutdown**

```typescript
const ac = new AbortController();
for (const sig of ["SIGINT", "SIGTERM"] as const) {
  process.on(sig, () => {
    ac.abort();
    setTimeout(() => process.exit(130), 5000).unref();
  });
}
```

**Exit code at boundary**

```typescript
async function main(): Promise<void> { /* ... */ }

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exitCode = 1;
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
- **Parsing argv with manual `slice` loops** — inconsistent; use `parseArgs`.

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

- Ask target runtime (Node vs Bun) and distribution shape (npm bin, compiled binary).
- Ask whether output must be JSON-only for scripting.
- Proceed with `parseArgs` defaults when subcommand tree is unspecified; propose subcommand pattern in output.
- Greenfield agent/CLI boot order and MV stubs: `reference.md` (composition chain).
