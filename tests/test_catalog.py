import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import catalog
import install


class CatalogTests(unittest.TestCase):
    def test_current_owned_packages_and_routing_are_consistent(self):
        self.assertEqual(catalog.validate(), [])

    def test_metadata_rejects_duplicates_unknown_fields_and_bad_yaml(self):
        for body in ["name: a\nname: b\ndescription: test", "name: a\ndescription: x\nrequires: b", "name: a\ndescription: foo: bar"]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                catalog.metadata(f"---\n{body}\n---\n")

    def test_missing_files_anchors_and_escape_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "SKILL.md"
            path.write_text("# Present\n[missing](missing.md)\n[wrong](#absent)\n[escape](../outside.md)\n")
            self.assertEqual(len(catalog.check_links(path, root)), 3)

    def test_metadata_rejects_yaml_non_strings_and_empty_values(self):
        for value in ['# TODO', '*missing_alias', '&anchor value', '[]', '{}',
                      'null', '~', 'true', 'yes', '123', '"   "', '>-']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                catalog.metadata(f'---\nname: example\ndescription: {value}\n---\n')
        with self.assertRaises(ValueError):
            catalog.metadata('---\nname: example\ndescription: "first"\n  second\n---\n')

    def test_metadata_supported_strings(self):
        for value, expected in [('Plain prose.', 'Plain prose.'),
                                ('"Use: JSON punctuation # safely"', 'Use: JSON punctuation # safely'),
                                ('>-\n  First line\n  second line.', 'First line second line.')]:
            self.assertEqual(catalog.metadata(f'---\nname: example\ndescription: {value}\n---\n')['description'], expected)

    def test_reference_style_links_are_rejected_explicitly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'SKILL.md'
            for text in ['[Recipe][r]\n[r]: missing.md\n', '[Recipe][]', '[r]: ../escape.md\n',
                         '[Recipe][undefined]']:
                path.write_text(text)
                with self.subTest(text=text):
                    self.assertTrue(catalog.check_links(path, root))

    def test_resource_reachability_starts_at_entrypoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'SKILL.md').write_text('# Skill\n')
            (root / 'a.md').write_text('[b](b.md)\n')
            (root / 'b.md').write_text('[a](a.md)\n')
            self.assertEqual(len(catalog.resource_errors(root)), 2)
            (root / 'SKILL.md').write_text('[a](a.md)\n')
            self.assertEqual(catalog.resource_errors(root), [])

    def test_local_evidence_is_excluded_but_public_links_to_it_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".gitignore").write_text("/docs/reviews/\n/.artifacts/\n")
            reviews = root / "docs/reviews"
            reviews.mkdir(parents=True)
            (reviews / "local.md").write_text("[private missing file](absent.md)\n")
            readme = root / "README.md"
            readme.write_text("# Public guide\n")
            self.assertEqual(catalog.public_document_errors(root), [])
            readme.write_text("[local report](docs/reviews/local.md)\n")
            errors = catalog.public_document_errors(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("excluded from public distribution", errors[0])
            # Force-staging ignored evidence must not silently make it publishable.
            readme.write_text("# Public guide\n")
            subprocess.run(["git", "add", "-f", "docs/reviews/local.md"], cwd=root, check=True)
            errors = catalog.public_document_errors(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("ignored file is tracked", errors[0])
            # New public docs are checked before staging as well.
            (root / "docs/guide.md").write_text("[missing](absent.md)\n")
            self.assertTrue(any("missing link" in error for error in catalog.public_document_errors(root)))

    def test_required_cycles_and_unknown_dependencies_are_rejected(self):
        for graph in [
            [{"name": "a", "requires": ["b"]}, {"name": "b", "requires": ["a"]}],
            [{"name": "a", "requires": ["missing"]}],
            [{"name": "../escape", "requires": []}],
        ]:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / "catalog.json").write_text(json.dumps({"schema_version": 1, "skills": graph, "bundles": {}}))
                with self.assertRaises(ValueError):
                    catalog.read_catalog(root)

    def test_generated_docs_change_when_trigger_or_handoff_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copy(ROOT / "README.md", root / "README.md")
            for item in catalog.read_catalog()["skills"]:
                shutil.copytree(ROOT / item["name"], root / item["name"])
            before = catalog.generated(root, catalog.read_catalog())
            skill = root / "integration-tester" / "SKILL.md"
            skill.write_text(skill.read_text().replace("Test an isolated TypeScript helper.", "Test a changed helper contract.").replace("Test behavior crossing modules", "Test changed behavior crossing modules"))
            after = catalog.generated(root, catalog.read_catalog())
            self.assertNotEqual(before["docs/router.md"], after["docs/router.md"])
            self.assertNotEqual(before["docs/boundaries.md"], after["docs/boundaries.md"])

    def test_every_full_migration_has_three_behavior_case_classes(self):
        cases = json.loads((ROOT / "tests" / "scenarios.json").read_text())
        for skill in catalog.read_catalog()["skills"]:
            if skill["migration"] == "contract":
                kinds = {case["kind"] for case in cases if case["skill"] == skill["name"]}
                self.assertEqual(kinds, {"positive", "adjacent", "missing-context"})
        for case in cases:
            self.assertTrue(case["request"] and case["expected"])


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)

    def test_all_assistant_layouts_are_repeatable_and_include_references(self):
        # These are filesystem lifecycle tests, not assistant-runtime tests.
        for host in (".agents", ".claude", ".cursor"):
            destination = self.base / host / "skills"
            operations = install.plan(ROOT, destination, ["integration-tester"])
            self.assertFalse(destination.exists())
            install.apply(operations)
            package = destination / "integration-tester"
            self.assertTrue((package / "references/python.md").is_file())
            self.assertEqual(catalog.check_links(package / "SKILL.md", ROOT / "integration-tester"), [])
            self.assertEqual(install.plan(ROOT, destination, ["integration-tester"])[0][0], "unchanged")
            install.apply(install.plan(ROOT, destination, ["integration-tester"], remove=True))
            self.assertFalse(package.exists())
            self.assertTrue((ROOT / "integration-tester/SKILL.md").is_file())

    def test_every_skill_installs_alone_with_all_local_resources(self):
        for item in catalog.read_catalog()["skills"]:
            destination = self.base / item["name"] / "skills"
            install.apply(install.plan(ROOT, destination, [item["name"]]))
            source = ROOT / item["name"]
            for resource in source.rglob("*.md"):
                installed = destination / item["name"] / resource.relative_to(source)
                self.assertEqual(installed.read_bytes(), resource.read_bytes())
                self.assertEqual(catalog.check_links(installed, source), [])

    def test_bundle_conflict_preflights_without_partial_write(self):
        destination = self.base / "skills"
        destination.mkdir()
        unrelated = destination / "observability-designer"
        unrelated.mkdir()
        (unrelated / "local.txt").write_text("preserve me")
        names = install.selection(catalog.read_catalog(), [], ["service-foundation"])
        with self.assertRaises(ValueError):
            install.plan(ROOT, destination, names)
        self.assertEqual(sorted(p.name for p in destination.iterdir()), ["observability-designer"])
        self.assertEqual((unrelated / "local.txt").read_text(), "preserve me")

    def test_reject_foreign_broken_links_relative_dest_and_symlink_ancestors(self):
        destination = self.base / "skills"
        destination.mkdir()
        (destination / "integration-tester").symlink_to(self.base / "missing")
        with self.assertRaises(ValueError):
            install.plan(ROOT, destination, ["integration-tester"], remove=True)
        with self.assertRaises(ValueError):
            install.plan(ROOT, Path("relative"), ["integration-tester"])
        alias = self.base / "alias"
        alias.symlink_to(destination)
        with self.assertRaises(ValueError):
            install.plan(ROOT, alias / "nested", ["config-and-env-designer"])

    def test_refuses_self_install_unknown_skill_and_changed_removal_link(self):
        with self.assertRaises(ValueError):
            install.plan(ROOT, ROOT / "nested", ["integration-tester"])
        with self.assertRaises(ValueError):
            install.selection(catalog.read_catalog(), ["third-party"], [])
        destination = self.base / "skills"
        install.apply(install.plan(ROOT, destination, ["integration-tester"]))
        removal = install.plan(ROOT, destination, ["integration-tester"], remove=True)
        link = destination / "integration-tester"
        link.unlink()
        link.symlink_to(self.base / "foreign")
        with self.assertRaises(ValueError):
            install.apply(removal)
        self.assertTrue(link.is_symlink())

    def test_cli_preview_does_not_create_destination(self):
        destination = self.base / "preview" / "skills"
        output = subprocess.run([sys.executable, str(ROOT / "scripts/install.py"), "--source", str(ROOT), "--dest", str(destination), "--skill", "integration-tester"], capture_output=True, text=True, check=True)
        self.assertIn("Preview only", output.stdout)
        self.assertIn("revision=", output.stdout)
        self.assertFalse(destination.exists())

    def test_missing_resource_prevents_installation(self):
        source = self.base / "source"
        source.mkdir()
        shutil.copytree(ROOT / "integration-tester", source / "integration-tester")
        (source / "integration-tester/references/python.md").unlink()
        destination = self.base / "target"
        with self.assertRaises(ValueError):
            install.plan(source, destination, ["integration-tester"])
        self.assertFalse(destination.exists())

    def test_bundle_installs_without_optional_neighbors(self):
        names = install.selection(catalog.read_catalog(), [], ["service-foundation"])
        self.assertEqual(names, ["config-and-env-designer", "integration-tester", "observability-designer"])
        destination = self.base / "bundle" / "skills"
        install.apply(install.plan(ROOT, destination, names))
        self.assertEqual(sorted(p.name for p in destination.iterdir()), names)

    def test_links_share_source_edits_and_removal_preserves_them(self):
        source = self.base / "source"
        source.mkdir()
        shutil.copytree(ROOT / "integration-tester", source / "integration-tester")
        destination = self.base / "target"
        install.apply(install.plan(source, destination, ["integration-tester"]))
        resource = source / "integration-tester/references/python.md"
        resource.write_text(resource.read_text() + "\nLocal development edit.\n")
        self.assertEqual((destination / "integration-tester/references/python.md").read_text(), resource.read_text())
        install.apply(install.plan(source, destination, ["integration-tester"], remove=True))
        self.assertIn("Local development edit.", resource.read_text())

    def test_cli_removes_matching_links_with_broken_or_absent_source(self):
        source = self.base / 'source'
        source.mkdir()
        package = source / 'integration-tester'
        shutil.copytree(ROOT / 'integration-tester', package)
        destination = self.base / 'target with spaces'
        install.apply(install.plan(source, destination, ['integration-tester']))
        (package / 'references/python.md').unlink()
        command = [sys.executable, str(ROOT / 'scripts/install.py'), '--source', str(source),
                   '--dest', str(destination), '--skill', 'integration-tester', '--remove', '--apply']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        link = destination / 'integration-tester'
        self.assertFalse(link.is_symlink())
        # Explicit names also recover after the entire source/catalog has disappeared.
        link.symlink_to(package)
        shutil.rmtree(source)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(link.is_symlink())

    def test_removal_rejects_escaping_names_and_preserves_real_directories(self):
        destination = self.base / 'target'
        destination.mkdir()
        (destination / 'integration-tester').mkdir()
        for name in ['../integration-tester', '/absolute', 'integration-tester']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                install.plan(self.base / 'missing', destination, [name], remove=True)
        self.assertTrue((destination / 'integration-tester').is_dir())


if __name__ == "__main__":
    unittest.main()
