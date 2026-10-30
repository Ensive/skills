# Introducing a skill

A new folder is a new skill when it has its own trigger and its own out-of-scope line. Describe the request that opens it and the work that stays with a named neighbor. If those boundaries match an existing skill, extend that skill’s relevant section instead.

Before adding a folder, read [the router](router.md) to find its lane and nearest neighbor, then read that neighbor’s frontmatter and “When to use” section. Check [the boundary table](boundaries.md) for existing ownership.

Complete these items in the same pull request:

- [ ] Create the owned skill folder with `SKILL.md`.
- [ ] Set `name` and `description` in the frontmatter; make the trigger and out-of-scope line explicit.
- [ ] Add a row in the appropriate lane of `docs/router.md`, plus its “Use this when” and “Hand off” section.
- [ ] Add a row in `docs/boundaries.md` for each handoff that names a neighbor, linking the source file; keep that table tied to explicit skill text.
- [ ] Add a row in `README.md` with the folder, skill name, and a sentence grounded in its description.

Keep the skill text and its map consistent in the same change. Folder names in `.gitignore` are local installs and stay untracked.
