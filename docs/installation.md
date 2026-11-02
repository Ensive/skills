# Local installation

The supported route is a selected set of directory links to **one canonical checkout**. It requires Git, Python 3.12+ and filesystem symlinks. The installer does not download dependencies, modify assistant settings, or copy third-party installations. See [compatibility and sources](compatibility.md) for documented versus executed support.

## Choose source and scope

Keep the canonical checkout outside assistant discovery directories when setting up a new installation. Clone `https://github.com/Ensive/skills` to a permanent path, inspect it, and detach at a reviewed **full commit SHA** containing the desired skills and installer.

```bash
git clone https://github.com/Ensive/skills /absolute/path/ensive-skills
git -C /absolute/path/ensive-skills checkout --detach REVIEWED_FULL_COMMIT_SHA
python3 /absolute/path/ensive-skills/scripts/catalog.py
```

Replace the example paths and SHA; the installer requires absolute paths and never guesses a destination.

| Assistant | Project scope destination | User scope destination |
| --- | --- | --- |
| Codex local CLI/IDE | `/project/.agents/skills` | `/user-home/.agents/skills` |
| Claude Code local | `/project/.claude/skills` | `/user-home/.claude/skills` |
| Cursor local | `/project/.cursor/skills` | `/user-home/.cursor/skills` |

Codex 0.163.0 also discovers user skills in `~/.codex/skills`: native `skills/list` verified all 14 owned symlinks as enabled user-scope skills from two unrelated temporary projects. Current OpenAI documentation lists `~/.agents/skills` as the general user route. For an existing `~/.codex/skills` installation, keep that working route rather than installing the same skills again in both locations.

Cursor also documents `.agents/skills`; when sharing with Codex, use that one location and skip a duplicate `.cursor/skills` installation. Inspect existing project/ancestor/user skill locations before installation. The script detects conflicts **at the explicit destination**, not all locations an assistant might discover. It never relies on assistant-specific duplicate precedence. If the source is already inside a discovery directory, do not link it back into itself or install it again in another location discovered by that assistant.

Cursor also reads Claude and Codex skill directories for compatibility. When maintaining links for all three assistants, make every same-name link resolve to the same canonical package; do not keep diverging copies. Cross-directory precedence and duplicate presentation are host-specific and are not established by the installer.

## Activation

Owned skills currently use only `name` and `description` frontmatter, with no manual-only flags or Codex invocation-policy overrides. All are eligible for explicit invocation and automatic selection when their description matches the task. The assistant loads the workflow and relevant references when selected; a skill is not an always-running hook.

| Assistant | Explicit invocation | Automatic selection |
| --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `$integration-tester` or the `/skills` picker | Matches the task to the description; implicit invocation is enabled by default |
| [Claude Code](https://code.claude.com/docs/en/skills) | `/integration-tester` at the start of the message | Chooses relevant skills by default |
| [Cursor](https://cursor.com/docs/skills) | `/integration-tester` in Agent chat | Applies skills it determines are relevant to the context |

Descriptions contain positive triggers and scope exclusions; the skill body supplies detailed decision criteria after loading. These are semantic instructions, not deterministic keyword rules. Project instructions and host permissions still apply. Automatic routing quality is separate from discovery and explicit-invocation evidence; see [compatibility](compatibility.md). A fresh session is a simple discovery check after installing; restart the host if its skill list has not refreshed.

## Preview and install

```bash
python3 /absolute/path/ensive-skills/scripts/install.py \
  --source /absolute/path/ensive-skills \
  --dest /absolute/project/.agents/skills --skill integration-tester
```

Review the printed source, revision, dirty state and links. Repeat with `--apply` to install. Use `--bundle service-foundation` for configuration, observability and integration testing; `--bundle frontend` for frontend contracts and integration testing; or repeat `--skill` for a custom selection. Bundle membership is in [catalog.json](../catalog.json).

Each link exposes the full skill directory including references. Required sibling dependencies, if later introduced, are expanded from the manifest and checked for cycles. Optional neighbors are not installed automatically. A standalone skill uses the project's own contracts and can proceed without its neighbors.

The same command is repeatable: matching links are unchanged. An existing folder, broken/foreign link or different source is a conflict. The installer preflights the whole selection before writing and never replaces conflicting files. Destination symlink ancestors are rejected. This is a local trusted-directory tool, not a defense against another process racing to replace ancestors.

## Verify, update and remove

After installation, confirm the skill appears in the assistant's skill list and explicitly invoke it on a synthetic task. Codex uses `$skill-name`/`/skills`; Claude Code and Cursor expose slash invocation. Reload/restart if discovery does not refresh. Installing a link is not an executed assistant test.

For updates, inspect `git status` in the canonical source and retain local work on a branch or patch. Fetch and review the candidate revision, then switch the source to the reviewed full SHA only when clean. All links intentionally see that revision together. Re-run validation and representative scenarios. Record the revision in the consuming project's instructions or dependency notes; symlinks are machine-local and not portable vendoring for teammates. Roll back by returning the clean source to the previously recorded SHA. The installer prints a dirty flag; a dirty checkout is development content, not a reproducible release pin.

To remove, repeat the selection with `--remove` for a preview, then add `--apply`. Only links pointing to the specified source/name are unlinked. Explicit `--skill` removal works even when a package, reference, catalog or entire source directory has disappeared; supply the original absolute source path and names. Bundle removal still needs the current catalog to expand its members, so use explicit names for recovery. Missing Git provenance is reported as unavailable during removal. Source content and unrelated configuration remain. If a link was replaced with a locally edited directory, removal stops; preserve/reconcile it manually. To use a different source checkout, unlink the matching old selection first and install from the new source. Check other consumers before removing any future shared required dependency.

Do not mix this route with copied or ecosystem-managed versions of the same skill. The [Vercel skills CLI](https://github.com/vercel-labs/skills) provides a broader lifecycle; its installation/update behavior was documentation-reviewed, not executed here. Windows, cloud syncing, plugin marketplaces and copy-based deployment are outside this installer's tested support.
