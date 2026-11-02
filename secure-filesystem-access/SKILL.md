---
name: secure-filesystem-access
description: >-
  Designs and reviews safe filesystem access for agents and CLIs: workspace roots,
  input-boundary decoding, control-byte rejection, realpath and
  symlink escape defenses, O_NOFOLLOW, same-descriptor metadata checks with explicit race limitations, bounded
  reads, write-parent checks, threat-aware scoped caches, size and MIME guards,
  temp-directory isolation, and sandbox options (subprocess, container, chroot).
  Use when implementing or fixing read/write/delete/list agent tools, building the
  path pipeline, "path traversal", "symlink escape", "TOCTOU", "O_NOFOLLOW",
  "realpath", "sandbox files", "workspace root", "temp directory", or "safe file
  open". Not for OWASP-wide audits only — use typescript-security-auditor to map
  findings after the pipeline exists.
---

# Secure Filesystem Access

## Project discovery

Read applicable project instructions, manifests, nearby code/tests and CI. Discover paths, runtime, contracts, data restrictions and commands with working directories. Preserve existing stack choices; adapt the examples to those conventions. Use a reversible step when context is incomplete; ask only when behavior or authorization blocks it. Optional neighbors are not prerequisites.

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
- [ ] Define filename encoding and normalization from the filesystem/API contract. NFC is not a homoglyph defense and may change filename identity.
- [ ] Decode URL-encoded input exactly once at its transport boundary, only if the API contract requires it; validate decoded bytes. Literal filesystem paths must not be URL-decoded by default.
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

Node/POSIX-oriented examples for a root whose ancestors are not attacker-mutable. These are not a race-proof sandbox. `realpath` then `open` can race; `O_NOFOLLOW` protects only the final component. `fstat` describes the opened object, not whether it stayed beneath the root. For hostile mutable trees, require OS-enforced containment or verified descriptor-relative traversal; do not claim this path recipe is sufficient.


**Node path validation and bounded read (trusted ancestor directories)**

```typescript
import path from "node:path";
import fs from "node:fs/promises";

function assertInsideRoot(root: string, candidate: string): string {
  const relative = path.relative(root, candidate);
  if (relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative))
    throw new Error("path outside workspace");
  return candidate;
}

async function resolveInside(workspaceRoot: string, raw: string): Promise<string> {
  if (/[\x00-\x1f]/.test(raw) || raw.length > 4096 || path.isAbsolute(raw))
    throw new Error("invalid path");
  // Reject traversal syntax by contract; literal percent characters are unchanged.
  if (raw.split(/[\\/]/).includes("..")) throw new Error("invalid path");
  const root = await fs.realpath(workspaceRoot);
  const candidate = assertInsideRoot(root, path.resolve(root, raw));
  return assertInsideRoot(root, await fs.realpath(candidate));
}

async function readBounded(real: string, maxBytes: number): Promise<Buffer> {
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 0 || maxBytes > 1_048_576)
    throw new Error("invalid byte limit");
  const fd = await fs.open(real, "r");
  try {
    const st = await fd.stat();
    if (!st.isFile() || st.size > maxBytes) throw new Error("invalid file or size");
    // Allocate against the cap, not a possibly stale initial stat size.
    const buf = Buffer.alloc(maxBytes + 1);
    let read = 0;
    while (read < buf.length) {
      const { bytesRead } = await fd.read(buf, read, buf.length - read, read);
      if (bytesRead === 0) break;
      read += bytesRead;
    }
    if (read > maxBytes) throw new Error("file exceeds cap");
    return buf.subarray(0, read);
  } finally {
    await fd.close();
  }
}
```

Resolve the path once using the actual transport contract. This bounded read does not prevent ancestor swaps, hard-link exposure, blocking special-file opens or changes after EOF. Use trusted immutable test directories for this example; strengthen the OS boundary for adversarial writers. Choose Windows-specific policy for drive paths, alternate streams and case/normalization rules rather than claiming POSIX parity.

**Read-only tool default**

```typescript
if (operation === "write" && !ctx.allowWrite) {
  throw new Error("write not permitted");
}
```

## Anti-patterns

- **Checking `includes("..")` only** — bypass via encoding or absolute paths; use resolve + prefix.
- **Treating open-then-stat as containment** — it avoids stale metadata but does not prevent path swaps; enforce the OS threat boundary separately.
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
1. Decode only at the declared input boundary; validate resulting characters
2. resolve + prefix guard (`assertInsideRoot`)
3. realpath + re-assert prefix
4. Open + same-fd metadata checks; state mutable-ancestor limitations and OS containment

## Threat coverage
Use the table template in [reference.md](reference.md). Map `done/gap` to auditor severities per `typescript-security-auditor` § Cross-skill reporting.

## Gaps and follow-ups
- <item>
```

## Escalation

- Discover the workspace root, allowed operations and target OS; ask only when an unresolved trust boundary blocks implementation.
- Proceed with read-only patterns when scope is unclear; flag write paths as high risk.
- Safe write, scoped realpath cache, and export contract: [reference.md](reference.md).

## Tools and verification

Use existing tools and synthetic fixtures within the task's authorization. If execution is unavailable, provide the check and mark it unexecuted. Report changed artifacts, assumptions, exact commands/cwd, results and remaining gaps; verify the affected success/failure boundary and project conventions. Examples do not authorize downloads or external mutations.

## Handoffs

Required sibling skills: none. Local references are implementation examples, included with this skill.

- Optional: `typescript-security-auditor` — Review the wider threat model and severity for TypeScript systems.
- Optional: `program-performance-optimizer` — Measure a bottleneck before considering a scoped path cache.
