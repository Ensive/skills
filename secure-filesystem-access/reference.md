# Secure Filesystem Access — reference

Supplemental patterns moved here to keep `SKILL.md` token-light. Implement exports in `src/fs/workspace.ts` (path configurable).

## `resolveInside` (tool-registry import contract)

```typescript
import path from "node:path";
import fs from "node:fs/promises";
// normalizePathForTrust, assertInsideRoot from SKILL.md Patterns

export async function resolveInside(workspaceRoot: string, raw: string): Promise<string> {
  const resolved = assertInsideRoot(workspaceRoot, raw);
  const real = await fs.realpath(resolved);
  assertInsideRoot(workspaceRoot, real);
  return real;
}

export { readBounded } from "./read-bounded"; // bounded read loop in SKILL.md
```

## Safe write (parent realpath, O_NOFOLLOW)

```typescript
import { constants as C } from "node:fs";

async function openForWrite(workspaceRoot: string, target: string) {
  const resolved = assertInsideRoot(workspaceRoot, target);
  const parent = path.dirname(resolved);
  const realParent = await fs.promises.realpath(parent);
  assertInsideRoot(workspaceRoot, realParent);
  const final = path.join(realParent, path.basename(resolved));
  const flags = C.O_WRONLY | C.O_CREAT | C.O_TRUNC |
    (C.O_NOFOLLOW ?? 0) | (C.O_CLOEXEC ?? 0);
  return fs.promises.open(final, flags, 0o600);
}
```

`O_NOFOLLOW` is honored on the final path component on POSIX; missing on Windows (constant absent → `?? 0`). After open, re-`fstat` the fd and reject symlinks (`!st.isFile()`).

## Scoped realpath cache (perf-safe)

For hot read paths, cache `realpath` results keyed by the *normalized* input path and scoped to one request/turn. Drop the cache when the workspace root changes or when any write occurs. Never persist across requests; never share across users.

```typescript
function makeRealpathCache(workspaceRoot: string) {
  const cache = new Map<string, string>();
  return {
    async resolveInside(raw: string): Promise<string> {
      const key = normalizePathForTrust(raw);
      const cached = cache.get(key);
      if (cached) return cached;
      const resolved = assertInsideRoot(workspaceRoot, key);
      const real = await fs.promises.realpath(resolved);
      assertInsideRoot(workspaceRoot, real);
      cache.set(key, real);
      return real;
    },
    invalidate(): void { cache.clear(); },
  };
}
```

See `program-performance-optimizer` for when to add this cache; never skip prefix guards or fd-stat.

## Threat coverage template

| Threat | Mitigation | Status |
|--------|------------|--------|
| Traversal | NFC + decode + resolve + prefix + realpath | done/gap |
| Symlink escape | realpath + re-assert prefix | done/gap |
| TOCTOU read | open + fstat + bounded read loop | done/gap |
| TOCTOU write | parent realpath + O_NOFOLLOW + fd-stat | done/gap |
| Unicode homoglyphs | NFC before compare | done/gap |
| Double percent-encoding | decode twice check | done/gap |

Map `done/gap` with exploit path to auditor severities: `typescript-security-auditor` § Cross-skill reporting.
