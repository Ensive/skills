#!/usr/bin/env python3
"""Link selected owned skills from one explicit checkout; preview unless --apply."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from catalog import NAME, metadata, read_catalog, resource_errors


def selection(catalog: dict, skills: list[str], bundles: list[str]) -> list[str]:
    graph = {s["name"]: s["requires"] for s in catalog["skills"]}
    selected = set()

    def add(name):
        if name not in graph:
            raise ValueError(f"unknown owned skill: {name}")
        if name not in selected:
            selected.add(name)
            for required in graph[name]:
                add(required)

    for name in skills:
        add(name)
    for name in bundles:
        if name not in catalog["bundles"]:
            raise ValueError(f"unknown bundle: {name}")
        for skill in catalog["bundles"][name]:
            add(skill)
    if not selected:
        raise ValueError("select at least one --skill or --bundle")
    return sorted(selected)


def plan(source: Path, destination: Path, names: list[str], remove: bool = False):
    if not source.is_absolute() or not destination.is_absolute():
        raise ValueError("--source and --dest must be absolute paths")
    # Reject symlink ancestors: an explicit destination must not redirect writes.
    for path in [destination, *destination.parents]:
        if path.is_symlink():
            raise ValueError(f"destination has a symlink ancestor: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"destination ancestor is not a directory: {path}")
    source = source.resolve(strict=not remove)
    destination = destination.resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError("destination must be outside the source checkout")
    operations = []
    for name in names:
        if not NAME.fullmatch(name) or len(name) > 64:
            raise ValueError(f"invalid skill name: {name}")
        target = source / name
        link = destination / name
        if not remove:
            if not (target / "SKILL.md").is_file() or target.is_symlink():
                raise ValueError(f"missing or indirect owned source: {target}")
            if metadata((target / "SKILL.md").read_text())["name"] != name:
                raise ValueError(f"source metadata does not match: {name}")
            problems = resource_errors(target)
            if problems:
                raise ValueError("; ".join(problems))
        ours = link.is_symlink() and Path(os.path.abspath(link.parent / os.readlink(link))) == target
        if (link.exists() or link.is_symlink()) and not ours:
            raise ValueError(f"conflict: {link}; preserve it and reconcile manually")
        action = ("unlink" if ours else "absent") if remove else ("unchanged" if ours else "link")
        operations.append((action, link, target))
    return operations


def apply(operations):
    # Recheck before each mutation; no overwrites, settings changes or recursive deletion.
    created = []
    try:
        for action, link, target in operations:
            if action == "link":
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(target, target_is_directory=True)
                created.append(link)
            elif action == "unlink":
                if not link.is_symlink() or Path(os.path.abspath(link.parent / os.readlink(link))) != target:
                    raise ValueError(f"link changed since preview: {link}")
                link.unlink()
    except (OSError, ValueError):
        for link in created:
            if link.is_symlink() and link.resolve() == dict((l, t) for _, l, t in operations)[link]:
                link.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="canonical local repository checkout")
    parser.add_argument("--dest", type=Path, required=True, help="explicit assistant skills directory")
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--bundle", action="append", default=[])
    parser.add_argument("--remove", action="store_true", help="unlink only matching links; preserve source")
    parser.add_argument("--apply", action="store_true", help="perform the displayed operations")
    args = parser.parse_args()
    try:
        # Explicit removal works even when the old package/catalog has disappeared.
        if args.remove and not args.bundle:
            if not args.skill:
                raise ValueError("select at least one --skill or --bundle")
            names = sorted(set(args.skill))
        else:
            names = selection(read_catalog(args.source), args.skill, args.bundle)
        operations = plan(args.source, args.dest, names, args.remove)
        try:
            sha = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True, stderr=subprocess.PIPE).strip()
            dirty = str(bool(subprocess.check_output(["git", "-C", str(args.source), "status", "--porcelain"], text=True, stderr=subprocess.PIPE).strip())).lower()
        except (OSError, subprocess.CalledProcessError):
            if not args.remove:
                raise
            sha, dirty = "unavailable", "unknown"
        print(f"source={args.source.resolve()} revision={sha} dirty={dirty}")
        for action, link, target in operations:
            print(f"{action}: {link} -> {target}")
        if args.apply:
            apply(operations)
            print("Applied. Assistant discovery/invocation must be verified separately.")
        else:
            print("Preview only. Repeat with --apply to perform these operations.")
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    main()
