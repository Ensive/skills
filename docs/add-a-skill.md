# Introducing a skill

A new folder is a new skill when it has its own trigger and its own out-of-scope line. Describe the request that opens it and the work that stays with a named neighbor. If those boundaries match an existing skill, extend that skill’s relevant section instead.

Before adding a folder, read [the router](router.md) to find its lane and nearest neighbor, then read that neighbor’s frontmatter and “When to use” section. Check [the boundary table](boundaries.md) for existing ownership.

Complete these items in the same pull request:

- [ ] Create the owned skill folder with `SKILL.md`.
- [ ] Set `name` and `description` in the frontmatter; make the trigger and out-of-scope line explicit.
- [ ] Add an ownership/lane entry to `catalog.json`; required sibling edges must be justified, explicit in the skill and acyclic. Prefer independent workflows.
- [ ] Write discovery/inputs, workflow/outputs, permissions/fallback, acceptance/failure cases and local reference pointers. Keep language/provider examples conditional.
- [ ] Add a `Handoffs` section declaring required sibling skills (normally none), and classify each neighbor as optional help or an implementation example. Follow the existing bullet format.
- [ ] Run `python3 scripts/catalog.py --write` to derive the README catalog, router and boundary rows from skill text. Review the routing diff.
- [ ] Add positive, adjacent-negative and missing-context cases to `tests/scenarios.json`; test standalone resources and relevant behavior.
- [ ] Run `python3 scripts/catalog.py` and `python3 -m unittest discover -s tests -v`; report model evaluations separately.
- [ ] Check [compatibility](compatibility.md) before changing metadata/discovery and [provenance](provenance.md) before including external material.

Keep the skill text and its map consistent in the same change. Folder names in `.gitignore` are local installs and stay untracked.
