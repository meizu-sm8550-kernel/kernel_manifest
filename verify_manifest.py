#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise the additive source manifest with the official Repo parser, offline."""

import argparse
import json
import re
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE_PATHS = {
    "device/meizu/m2468": "android_device_meizu_m2468",
    "kernel/meizu/sm8550": "android_kernel_meizu_sm8550",
    "kernel/meizu/sm8550-modules": "android_kernel_meizu_sm8550-modules",
    "kernel/meizu/sm8550-devicetrees": "android_kernel_meizu_sm8550-devicetrees",
}
CLANG_PATH = "prebuilts/clang/host/linux-x86-kernel"
OLD_PREBUILT = "device/meizu/m2468-kernel"
LEGACY = {
    CLANG_PATH: "platform/prebuilts/clang/host/linux-x86",
    OLD_PREBUILT: "legacy/android_device_meizu_m2468-kernel",
}
KEPT = {
    "vendor/meizu/m2468": "private/vendor_meizu_m2468",
    "vendor/lineage": "LineageOS/android_vendor_lineage",
    "kernel/another-device/sm8550": "android_kernel_meizu_sm8550",
    "prebuilts/clang/host/linux-x86": "platform/prebuilts/clang/host/linux-x86",
}


def project_xml(projects):
    root = ET.Element("manifest")
    for path, name in projects.items():
        ET.SubElement(root, "project", name=name, path=path)
    return ET.tostring(root, encoding="unicode")


def check_overlay(path, manifest_xml):
    overlay = ET.parse(path).getroot()
    assert not overlay.findall("remove-project"), "the source manifest must not remove projects"
    assert not overlay.findall("default"), "do not override the platform default"
    assert not overlay.findall("include"), "overlay must work as one downloaded XML file"
    expected = {p.get("path"): p for p in overlay.findall("project")}
    assert set(expected) == set(SOURCE_PATHS)

    remote = overlay.find("remote[@name='meizu-sm8550-kernel']")
    assert remote is not None and remote.get("revision") == "refs/heads/lineage-23.2"
    assert all(not any(a in p.attrib for a in ("revision", "upstream", "dest-branch"))
               for p in expected.values()), "projects must follow the remote branch, not a pinned revision"

    for platform_branch, scenario in (
        (branch, scenario)
        for branch in ("lineage-23.2", "lineage-24.0", "avium-16.2")
        for scenario in ("no_old_projects", "legacy_projects_preserved", "duplicate_main", "duplicate_local")
    ):
        with tempfile.TemporaryDirectory(dir=ROOT / ".verification", prefix="parse-") as temporary:
            repodir = Path(temporary) / ".repo"
            local = repodir / "local_manifests"
            local.mkdir(parents=True)
            (repodir / "manifests").mkdir()
            gitdir = repodir / "manifests.git"
            gitdir.mkdir()
            (gitdir / "config").write_text(
                '[remote "origin"]\nurl = https://example.invalid/manifest\n'
            )
            base = ET.fromstring(project_xml(KEPT))
            base.insert(0, ET.Element("remote", name="lineage", fetch="https://example.invalid/"))
            base.insert(1, ET.Element("default", remote="lineage", revision=platform_branch))
            preserved = dict(KEPT)
            if scenario == "legacy_projects_preserved":
                base.extend(ET.fromstring(project_xml(LEGACY)))
                preserved.update(LEGACY)
            elif scenario == "duplicate_main":
                base.extend(ET.fromstring(project_xml(SOURCE_PATHS)))
            elif scenario == "duplicate_local":
                (local / "old-device.xml").write_text(project_xml(SOURCE_PATHS))
            (local / "zzzz-meizu-m2468.xml").write_text(path.read_text())
            manifest_file = repodir / "manifest.xml"
            manifest_file.write_text(ET.tostring(base, encoding="unicode"))
            parsed = manifest_xml.XmlManifest(str(repodir), str(manifest_file), str(local))
            if scenario.startswith("duplicate_"):
                try:
                    parsed.projects
                except manifest_xml.ManifestParseError as error:
                    assert "duplicate path" in str(error), str(error)
                else:
                    raise AssertionError("duplicate declarations must not be silently replaced")
                print(f"PASS {path.name}: {platform_branch}/{scenario}; duplicate path rejected")
                continue
            projects = {p.relpath: p for p in parsed.projects}
            assert set(projects) == set(preserved) | set(expected)
            for preserved_path, name in preserved.items():
                assert projects[preserved_path].name == name
                assert projects[preserved_path].revisionExpr == platform_branch
            for project_path, node in expected.items():
                actual = projects[project_path]
                assert actual.name == node.get("name")
                assert actual.revisionExpr == "refs/heads/lineage-23.2"
            for source_path, name in SOURCE_PATHS.items():
                assert projects[source_path].remote.url == (
                    "https://github.com/meizu-sm8550-kernel/" + name
                )
            print(f"PASS {path.name}: {platform_branch}/{scenario}; {len(projects)} projects, preserved {len(preserved)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-source", required=True, type=Path,
                        help="official git-repo source checkout, e.g. a ROM tree's .repo/repo")
    args = parser.parse_args()
    if not (args.repo_source / "manifest_xml.py").is_file():
        parser.error("--repo-source must contain the official manifest_xml.py")
    sys.path.insert(0, str(args.repo_source.resolve()))
    import manifest_xml

    (ROOT / ".verification").mkdir(exist_ok=True)
    check_overlay(ROOT / "local_manifest.xml", manifest_xml)
    if (ROOT / "pinned.xml").exists():
        check_overlay(ROOT / "pinned.xml", manifest_xml)
        assert (ROOT / "pinned.xml").read_bytes() == (ROOT / "local_manifest.xml").read_bytes(), \
            "legacy pinned.xml URL must serve the same branch-tracking manifest"
        pinned = ET.parse(ROOT / "pinned.xml").getroot()
        nodes = {p.get("path"): p for p in pinned.findall("project")}
        lock = json.loads((ROOT / "revisions.lock.json").read_text())
        assert len(lock["projects"]) == len(nodes)
        assert {p["path"] for p in lock["projects"]} == set(nodes)
        for record in lock["projects"]:
            node = nodes[record["path"]]
            assert re.fullmatch(r"[0-9a-f]{40}", record["commit"])
            assert record["branch"] == "lineage-23.2"
            assert "revision" not in node.attrib
            assert record["name"] == node.get("name")
        print("PASS branch-tracking aliases match; revisions.lock.json is an audit snapshot only")
    else:
        print("Legacy alias has not been generated; only the branch overlay was checked.")


if __name__ == "__main__":
    main()
