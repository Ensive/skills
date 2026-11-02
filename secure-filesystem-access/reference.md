# Filesystem implementation limits and recipes

## Project contract

Choose the existing filesystem module. `resolveInside(root, raw)` and `readBounded(path, cap)` in [SKILL.md](SKILL.md) are Node implementation examples, not required exports or proof of containment under concurrent attackers. No sibling skill is a required dependency.

## Writes and mutable directories

A parent `realpath` check plus `O_NOFOLLOW` on the leaf does not prevent ancestor replacement. `fstat` on a followed symlink reports its target; it cannot prove that no symlink was followed. Opening with `O_TRUNC` can destroy content before post-open checks run.

For attacker-mutable trees, select an OS containment strategy with verified semantics: descriptor-relative traversal with appropriate no-follow/beneath constraints, a restricted process/container filesystem, or a trusted service owning all mutation. Node's portable path API is not a complete equivalent of Linux `openat2` containment. If the required primitive is unavailable, fail closed for the unsafe operation and report the limitation.

For trusted directories, create a new temporary file with exclusive creation in the verified target directory, bounded content and intended permissions; flush according to durability requirements, then atomically replace only under the application's overwrite policy. Atomic rename is not itself an authorization or containment guarantee. Test failures before/after creation and cleanup. Keep existing file content intact on validation failure.

## Scoped realpath cache (conditional)

Consider a cache only after measuring and proving directory/link stability for its lifetime. Request scope alone does not protect against an external writer changing a link during that request. Key by canonical root and input identity; bound entries, invalidate on controlled mutation/root change, and never share across tenants. If external mutation is possible, omit the cache or use a trusted filesystem snapshot. Optional help: program-performance-optimizer for measurement.

## Threat coverage template

| Threat | Evidence required | Status |
| --- | --- | --- |
| Traversal and absolute paths | Target-OS path cases; transport decoding cases | verified / gap / out of scope |
| Symlink or hard-link exposure | Actual allowed link policy and adversarial fixtures | verified / gap / out of scope |
| Mutable ancestors | OS containment or explicit trusted-tree assumption | verified / gap / out of scope |
| Oversize/growing files | Cap + one-byte detection; cleanup on failure | verified / gap / out of scope |
| Unsafe writes | No truncation before validation; overwrite and cleanup tests | verified / gap / out of scope |
| Filename identity | Literal percent, Unicode, drive/case behavior on target OS | verified / gap / out of scope |

Map reachable gaps to impact/likelihood with optional typescript-security-auditor help for TypeScript systems. Do not infer severity from a checkbox alone.

Source checked 2026-10-30: [Node filesystem documentation](https://nodejs.org/api/fs.html). The snippets are bounded examples, not a certified sandbox or a tested Windows implementation.
