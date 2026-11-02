#!/usr/bin/env python3
"""Validate owned content and derive human routing docs. Python 3.12+, stdlib only."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HANDOFF = re.compile(r"^- (Optional|Example): `([a-z0-9-]+)` — (.+)$", re.M)
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
REFERENCE_LINK = re.compile(r"^ {0,3}\[[^\]\n]+\]:|\[[^\]\n]+\]\[[^\]\n]*\]", re.M)


def metadata(text: str) -> dict[str, str]:
    """Narrow YAML profile: name/description; plain, JSON-quoted or folded strings."""
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("missing YAML frontmatter")
    block = text.split("---\n", 2)[1]
    result: dict[str, str] = {}
    key = None
    folded = False
    for line in block.splitlines():
        if "\t" in line:
            raise ValueError("tabs are not supported in frontmatter")
        if line.startswith("  ") and not line.startswith("   ") and folded:
            result[key] = (result[key] + " " + line.strip()).strip()
            continue
        match = re.fullmatch(r"(name|description): (.+)", line)
        if not match or match[1] in result:
            raise ValueError(f"unsupported or duplicate frontmatter line: {line}")
        key, value = match.groups()
        value = value.rstrip()
        folded = key == "description" and value in (">-", ">")
        if folded:
            result[key] = ""
            continue
        if value.startswith('"'):
            value = json.loads(value)
        elif (not re.match(r"[A-Za-z]", value) or ": " in value or value.endswith(":")
              or " #" in value or value.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
            raise ValueError("use a JSON-quoted string for YAML punctuation or non-prose values")
        result[key] = value
    if set(result) != {"name", "description"}:
        raise ValueError("name and description are required")
    if any(not isinstance(value, str) or not value.strip() for value in result.values()):
        raise ValueError("name and description must be non-empty strings")
    return result


def section(text: str, title: str) -> str:
    match = re.search(r"^## " + re.escape(title) + r"\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise ValueError(f"missing section: {title}")
    return match[1].strip()


def read_catalog(root: Path = ROOT) -> dict:
    catalog = json.loads((root / "catalog.json").read_text())
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported catalog version")
    names = [item["name"] for item in catalog["skills"]]
    if len(names) != len(set(names)):
        raise ValueError("duplicate catalog skill")
    for name in names:
        if not NAME.fullmatch(name) or len(name) > 64:
            raise ValueError(f"invalid skill name: {name}")
    graph = {item["name"]: item["requires"] for item in catalog["skills"]}
    visiting, visited = set(), set()

    def visit(name):
        if name not in graph:
            raise ValueError(f"unknown required skill: {name}")
        if name in visiting:
            raise ValueError(f"required dependency cycle: {name}")
        if name in visited:
            return
        visiting.add(name)
        for neighbor in graph[name]:
            visit(neighbor)
        visiting.remove(name)
        visited.add(name)

    for name in names:
        visit(name)
    for bundle, members in catalog["bundles"].items():
        if not NAME.fullmatch(bundle) or not members or any(n not in graph for n in members):
            raise ValueError(f"invalid bundle: {bundle}")
    return catalog


def prose(text: str) -> str:
    return re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    seen: dict[str, int] = {}
    result = set()
    for title in re.findall(r"^#{1,6} (.+)$", prose(text), re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.add(slug if not count else f"{slug}-{count}")
    return result


def check_links(path: Path, boundary: Path, public_paths: set[Path] | None = None) -> list[str]:
    errors = []
    text = prose(path.read_text())
    if REFERENCE_LINK.search(text):
        errors.append(f"{path}: reference-style links unsupported; use inline [label](path) links")
    for target in LINK.findall(text):
        if target.startswith(("https://", "http://", "mailto:")):
            continue
        target = target.removeprefix("<").removesuffix(">")
        file, _, fragment = target.partition("#")
        dest = (path.parent / file).resolve() if file else path.resolve()
        if not dest.is_relative_to(boundary.resolve()):
            errors.append(f"{path}: link escapes package: {target}")
        elif not dest.exists():
            errors.append(f"{path}: missing link: {target}")
        elif public_paths is not None and dest not in public_paths:
            errors.append(f"{path}: link target excluded from public distribution: {target}")
        elif fragment and dest.is_file() and fragment not in anchors(dest.read_text()):
            errors.append(f"{path}: missing anchor: {target}")
    return errors


def public_document_errors(root: Path) -> list[str]:
    """Ignore local evidence, but reject published links to it and tracked ignores."""
    def git_paths(*args):
        result = subprocess.run(["git", "ls-files", "-z", *args], cwd=root,
                                capture_output=True, text=True, check=True)
        return {root / name for name in result.stdout.split("\0") if name}

    ignored = git_paths("--cached", "--ignored", "--exclude-standard")
    files = git_paths("--cached", "--others", "--exclude-standard") - ignored
    public = {path.resolve() for path in files}
    for path in files:
        public.update(parent.resolve() for parent in path.parents if parent.is_relative_to(root))
    errors = [f"{path}: ignored file is tracked; remove it from the index" for path in sorted(ignored)]
    for path in sorted(files):
        relative = path.relative_to(root)
        if path.suffix == ".md" and (len(relative.parts) == 1 or relative.parts[0] in {"docs", "tests"}):
            if not path.is_file():
                errors.append(f"{path}: tracked documentation is missing")
            else:
                errors.extend(check_links(path, root, public))
    return errors


def resource_errors(directory: Path) -> list[str]:
    """Validate package links and actual Markdown reachability from SKILL.md."""
    errors = []
    documents = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            errors.append(f"{path}: symlink inside owned package")
        elif path.is_file() and path.suffix == ".md":
            documents[path.resolve()] = path
            errors.extend(check_links(path, directory))
    pending, visited = [(directory / "SKILL.md").resolve()], set()
    while pending:
        path = pending.pop()
        if path in visited or path not in documents:
            continue
        visited.add(path)
        for target in LINK.findall(prose(path.read_text())):
            if target.startswith(("https://", "http://", "mailto:")):
                continue
            file = target.removeprefix("<").removesuffix(">").partition("#")[0]
            pending.append((path.parent / file).resolve() if file else path)
    errors.extend(f"{documents[path]}: unreachable reference" for path in sorted(documents.keys() - visited))
    return errors


def generated(root: Path, catalog: dict) -> dict[str, str]:
    table = ["| Skill | Purpose and trigger |", "| --- | --- |"]
    router = ["# Skill router", "", "Generated by `python3 scripts/catalog.py --write` from owned SKILL.md files. Select the task boundary; do not load the whole catalog. Required resources live inside each skill. Optional neighbors are resolved by name through the host assistant and loaded only when relevant and available.", ""]
    boundaries = ["# Cross-skill boundaries", "", "Generated from each skill's Handoffs section and catalog required edges. Optional help and implementation examples are not installation dependencies. Return to the original task after a focused handoff; do not recursively load neighbors.", "", "| Skill to leave | Relationship | Skill to open | Situation |", "| --- | --- | --- | --- |"]
    lane = None
    for item in catalog["skills"]:
        name = item["name"]
        text = (root / name / "SKILL.md").read_text()
        meta = metadata(text)
        summary = meta['description'].split(". ", 1)[0].rstrip(".") + "."
        table.append(f"| [{name}]({name}/SKILL.md) | {summary} |")
        if item["lane"] != lane:
            lane = item["lane"]
            router += [f"## {lane}", ""]
        router += [f"### {name}", "", f"[{name}](../{name}/SKILL.md): {meta['description']}", "", "**Use this when:**", "", section(text, "When to use"), "", "**Hand off (optional):**", ""]
        for kind, target, why in HANDOFF.findall(section(text, "Handoffs")):
            router.append(f"- {kind}: [{target}](../{target}/SKILL.md) — {why}")
            boundaries.append(f"| [{name}](../{name}/SKILL.md#handoffs) | {kind} | [{target}](../{target}/SKILL.md) | {why} |")
        for target in item["requires"]:
            boundaries.append(f"| [{name}](../{name}/SKILL.md#handoffs) | Required | [{target}](../{target}/SKILL.md) | Required by the skill contract. |")
        router.append("")
    readme = (root / "README.md").read_text()
    start, end = "<!-- catalog:start -->", "<!-- catalog:end -->"
    if readme.count(start) != 1 or readme.count(end) != 1:
        raise ValueError("README catalog markers missing or duplicated")
    readme = readme.split(start)[0] + start + "\n" + "\n".join(table) + "\n" + end + readme.split(end)[1]
    return {"README.md": readme, "docs/router.md": "\n".join(router), "docs/boundaries.md": "\n".join(boundaries) + "\n"}


def validate(root: Path = ROOT, check_generated: bool = True) -> list[str]:
    catalog = read_catalog(root)
    names = {item["name"] for item in catalog["skills"]}
    errors = []
    for item in catalog["skills"]:
        name = item["name"]
        directory = root / name
        try:
            text = (directory / "SKILL.md").read_text()
            meta = metadata(text)
            if meta["name"] != name or not 1 <= len(meta["description"]) <= 1024:
                errors.append(f"{name}: name mismatch or invalid description length")
            expected = "Required sibling skills: " + (", ".join(item["requires"]) if item["requires"] else "none") + "."
            handoffs = section(text, "Handoffs")
            if expected not in handoffs:
                errors.append(f"{name}: required dependency contract differs from catalog")
            targets = {target for _, target, _ in HANDOFF.findall(handoffs)}
            if targets - names or name in targets:
                errors.append(f"{name}: unknown/self handoff")
            body = "\n".join(p.read_text() for p in directory.rglob("*.md"))
            mentioned = {n for n in names - {name} if re.search(r"(?<![a-z-])" + re.escape(n) + r"(?![a-z-])", body)}
            if mentioned - targets - set(item["requires"]):
                errors.append(f"{name}: unclassified neighbors {sorted(mentioned - targets - set(item['requires']))}")
            errors.extend(resource_errors(directory))
            if item["migration"] == "contract":
                for title in ("Discover and decide", "Workflow", "Tools and acceptance"):
                    section(text, title)
        except (ValueError, OSError) as exc:
            errors.append(f"{name}: {exc}")
    # The ownership manifest must not accidentally absorb ignored local installs.
    for path in root.glob("*/SKILL.md"):
        ignored = subprocess.run(["git", "check-ignore", "--no-index", "-q", str(path.parent)], cwd=root).returncode == 0
        if ignored and path.parent.name in names:
            errors.append(f"{path}: owned skill is ignored")
        if not ignored and path.parent.name not in names:
            errors.append(f"{path}: unlisted owned skill")
    errors.extend(public_document_errors(root))
    if check_generated:
        for relative, content in generated(root, catalog).items():
            if (root / relative).read_text() != content:
                errors.append(f"{relative}: stale; run python3 scripts/catalog.py --write")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh generated routing documents")
    args = parser.parse_args()
    try:
        if args.write:
            for path, content in generated(ROOT, read_catalog()).items():
                (ROOT / path).write_text(content)
        errors = validate()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(read_catalog()['skills'])} owned skills; metadata, resources, links, dependencies and generated routing")


if __name__ == "__main__":
    main()
