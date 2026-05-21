---
name: secure-filesystem-access
description: >-
  Designs and reviews safe filesystem access for agents and CLIs: workspace roots,
  path normalization (NFC, percent-decode, control-byte rejection), realpath and
  symlink escape defenses, O_NOFOLLOW, TOCTOU-safe open-then-fstat patterns, bounded
  reads, safe-write parent realpath, scoped realpath caches, size and MIME guards,
  temp-directory isolation, and sandbox options (subprocess, container, chroot).
  Use when implementing or fixing read/write/delete/list agent tools, building the
  path pipeline, "path traversal", "symlink escape", "TOCTOU", "O_NOFOLLOW",
  "realpath", "sandbox files", "workspace root", "temp directory", or "safe file
  open". Not for OWASP-wide audits only — use typescript-security-auditor to map
  findings after the pipeline exists.
---

# Secure Filesystem Access

## When to use

- User implements or fixes agent tools that read, write, list, or delete files (primary owner for path-guard code).
- User asks to prevent path traversal, symlink escapes, or writes outside a project root in tool handlers.
- User needs TOCTOU-safe open patterns or race-resistant file operations.
- User compares subprocess chroots, containers, seccomp, or AppArmor for isolation.
- User sets max file size, extension allowlists, or binary-vs-text policies for tools.

## Core principles

1. Define one explicit workspace root; reject operations outside it after normalization.
2. Normalize with `path.resolve` then verify prefix with trailing separator discipline.
3. Resolve symlinks with `realpath` before trust decisions; treat unexpected links as errors.
4. Open then stat on the same file descriptor; do not trust path-only checks alone.
5. Enforce max bytes, line counts, and MIME sniffing where content type matters.
6. Default read-only; require explicit flag or role for writes and deletes.
7. Never follow user-controlled symlinks into sensitive paths without policy.
8. Prefer subprocess or container sandboxes when OS-level isolation is required.
9. Log paths as relative to workspace in user-facing output when possible.
10. Defer OWASP-wide review to typescript-security-auditor; focus on FS mechanics here.

## Checklist

- [ ] Document workspace root source (cwd, config, env) and whether it can change mid-run.
- [ ] Normalize path string to NFC before any comparison or resolve (Unicode homoglyph bypass).
- [ ] Percent-decode path once (reject double-encoding); re-run prefix guard after decode.
- [ ] Reject NUL and control bytes `0x00`–`0x1F` in path strings; reject overlong path segments.
- [ ] Reject absolute paths and `..` segments before resolve.
- [ ] After `resolve`, assert `resolved === workspaceRoot || resolved.startsWith(workspaceRoot + sep)`.
- [ ] Call `realpath` (or `fs.realpath`) and re-assert prefix after link resolution.
- [ ] Use `open` + `fstat` on fd for TOCTOU-sensitive reads; avoid stat-then-open races.
- [ ] Apply max size before reading full content; for untrusted size, stream into a fixed buffer that aborts past `MAX_BYTES` instead of trusting the stat.
- [ ] For writes, `realpath` the *parent* directory (leaf does not exist yet) and re-assert prefix; open with `O_NOFOLLOW` on platforms that support it.
- [ ] Validate extension allowlist and magic bytes for uploads if applicable.
- [ ] Separate read, write, delete capabilities in tool schemas and executor checks.
- [ ] Document behavior for missing files, directories, and permission errors (no leaks).
- [ ] If sandboxing: specify subprocess cwd, uid, seccomp profile, or container boundary.

## Patterns

**Normalize path for trust (checklist step 1 — before resolve)**

```typescript
const MAX_PATH_LEN = 4096;

function normalizePathForTrust(raw: string): string {
  if (raw.includes("\0") || /[\x00-\x1f]/.test(raw)) {
    throw new Error("invalid path characters");
  }
  if (raw.length > MAX_PATH_LEN) throw new Error("path too long");
  let p = raw.normalize("NFC");
  try {
    p = decodeURIComponent(p);
  } catch {
    throw new Error("invalid percent-encoding");
  }
  // Reject only when a second decode changes the string (true double-encoding).
  try {
    const twice = decodeURIComponent(p);
    if (twice !== p) throw new Error("double-encoded path");
  } catch (e) {
    if (e instanceof Error && e.message === "double-encoded path") throw e;
  }
  return p;
}
```

Call `normalizePathForTrust` on user input, then `assertInsideRoot` + `realpath` below.

**Prefix guard after resolve**

```typescript
function assertInsideRoot(workspaceRoot: string, targetPath: string): string {
  const safe = normalizePathForTrust(targetPath);
  const root = path.resolve(workspaceRoot);
  const resolved = path.resolve(root, safe);
  const prefix = root.endsWith(path.sep) ? root : root + path.sep;
  if (resolved !== root && !resolved.startsWith(prefix)) {
    throw new Error("path outside workspace");
  }
  return resolved;
}
```

**Resolve inside workspace (export for tool-registry)**

```typescript
async function resolveInside(workspaceRoot: string, raw: string): Promise<string> {
  const resolved = assertInsideRoot(workspaceRoot, raw);
  const real = await fs.promises.realpath(resolved);
  assertInsideRoot(workspaceRoot, real);
  return real;
}
```

Export `resolveInside` and `readBounded` from your FS module; full export contract in `reference.md`.

**Bounded read with TOCTOU-safe fstat**

`fd.readFile()` after a stat trusts the file size between two syscalls; for untrusted input, cap during the read itself.

```typescript
async function readBounded(real: string, maxBytes: number): Promise<Buffer> {
  const fd = await fs.promises.open(real, "r");
  try {
    const st = await fd.stat();
    if (st.size > maxBytes) throw new Error("file too large");
    const buf = Buffer.allocUnsafe(Math.min(st.size, maxBytes) + 1);
    let read = 0;
    while (read < buf.length) {
      const { bytesRead } = await fd.read(buf, read, buf.length - read, read);
      if (bytesRead === 0) break;
      read += bytesRead;
      if (read > maxBytes) throw new Error("file grew past cap during read");
    }
    return buf.subarray(0, Math.min(read, maxBytes));
  } finally {
    await fd.close();
  }
}
```

**Read-only tool default**

```typescript
if (operation === "write" && !ctx.allowWrite) {
  throw new Error("write not permitted");
}
```

## Anti-patterns

- **Checking `includes("..")` only** — bypass via encoding or absolute paths; use resolve + prefix.
- **Stat path then open path separately** — TOCTOU swap; open-then-stat on same fd.
- **Trusting user-supplied `workspaceRoot` without validation** — attacker-chosen root; fix config source.
- **Following symlinks blindly** — escape via link; realpath and deny link chains outside root.
- **Reading unbounded files into memory** — DoS; stream with size cap.
- **`fd.readFile()` on untrusted size after a stat-only check** — TOCTOU growth window; use the bounded read loop above.
- **`realpath` on the full target before a write** — fails with `ENOENT` for new files; realpath the parent and re-assert.
- **Persisting a realpath cache across requests or users** — stale links and cross-tenant leaks; scope to one request.
- **Mixing FS policy into generic security audit prose** — keep FS rules here; cross-ref auditor skill.

## Output format

```markdown
# Filesystem access design: <feature>

## Workspace policy
- Root: <how determined>
- Allowed ops: read | write | delete
- Max size: <bytes> | Max lines: <n>

## Path pipeline
1. NFC + percent-decode + control-byte rejection (`normalizePathForTrust`)
2. resolve + prefix guard (`assertInsideRoot`)
3. realpath + re-assert prefix
4. open + fstat on same fd (reads) or parent realpath + O_NOFOLLOW (writes)

## Threat coverage
Use the table template in `reference.md`. Map `done/gap` to auditor severities per `typescript-security-auditor` § Cross-skill reporting.

## Gaps and follow-ups
- <item>
```

## Escalation

- Ask for workspace root source and whether writes or deletes are required.
- Ask target OS if recommending seccomp, AppArmor, or containers.
- Proceed with read-only patterns when scope is unclear; flag write paths as high risk.
- Safe write, scoped realpath cache, and export contract: `reference.md`.
