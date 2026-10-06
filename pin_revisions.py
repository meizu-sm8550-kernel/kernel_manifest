#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Record release SHAs for audit; keep both XML entry points tracking the branch."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
BRANCH = "lineage-23.2"


def git(directory, *args):
    return subprocess.check_output(
        ["git", "-C", str(directory), *args], text=True
    ).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--repos-dir", type=Path,
                        help="directory containing the four named source repos")
    inputs.add_argument("--revisions", type=Path,
                        help="JSON object mapping each source repo name to its 40-character commit")
    args = parser.parse_args()
    tree = ET.parse(ROOT / "local_manifest.xml")
    if tree.getroot().findall("remove-project"):
        parser.error("remove-project entries are disabled; keep the source manifest additive")
    projects = tree.getroot().findall("project")
    source_projects = [p for p in projects if p.get("remote") == "meizu-sm8550-kernel"]
    expected_names = {p.get("name") for p in source_projects}

    if args.revisions:
        revisions = json.loads(args.revisions.read_text())
        if not isinstance(revisions, dict) or set(revisions) != expected_names:
            parser.error("revision map must contain exactly the four source repo names")
    else:
        revisions = {}
        for project in source_projects:
            name = project.get("name")
            directory = args.repos_dir / name
            if Path(git(directory, "rev-parse", "--show-toplevel")).resolve() != directory.resolve():
                parser.error(f"not a repository root: {directory}")
            if git(directory, "branch", "--show-current") != BRANCH:
                parser.error(f"{name} must be on branch {BRANCH}")
            if git(directory, "status", "--porcelain"):
                parser.error(f"{name} has uncommitted files; commit source changes before pinning")
            revisions[name] = git(directory, "rev-parse", "HEAD^{commit}")

    for name, revision in revisions.items():
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            parser.error(f"{name}: expected a full lowercase Git commit, got {revision!r}")

    remotes = {r.get("name"): r.get("fetch") for r in tree.getroot().findall("remote")}
    records = []
    for project in projects:
        name = project.get("name")
        if any(attr in project.attrib for attr in ("revision", "upstream", "dest-branch")):
            parser.error(f"{name}: project revision pins are disabled; use the remote branch")
        records.append({
            "name": name,
            "path": project.get("path"),
            "url": remotes[project.get("remote")] + name,
            "commit": revisions[name],
            **({"branch": BRANCH} if name in revisions else {}),
        })

    # Keep the legacy URL usable for clients that already download pinned.xml.
    # Release recording must never turn either entry point back into SHA pins.
    (ROOT / "pinned.xml").write_bytes((ROOT / "local_manifest.xml").read_bytes())
    lock = {
        "schema_version": 2,
        "lineageos_branch": BRANCH,
        "scope": "Audit snapshot of four published commits; XML manifests follow the source branch and do not use these SHAs for checkout.",
        "projects": records,
    }
    (ROOT / "revisions.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    print("Recorded revisions.lock.json for audit; both XML aliases still follow the source branch.")


if __name__ == "__main__":
    main()
