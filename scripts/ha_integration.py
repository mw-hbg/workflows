"""Information about a Home Assistant custom integration repository (Marketplace), for the shared workflows.

A repository holds exactly one integration in custom_components/<domain>/ (the
Marketplace allows only one per repository).

  python ha_integration.py check       <repo-root> <domain>   consistency checks (fails on problems)
  python ha_integration.py info        <repo-root> <domain>   GitHub outputs: name, version
  python ha_integration.py set-version <repo-root> <domain> <version>   writes the version into manifest.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Files every integration repository must have (relative to the repository root).
# README.md holds English and German together: the Marketplace only shows README.md.
REQUIRED_ROOT_FILES = ("README.md", "CHANGELOG.md", "LICENSE", "SECURITY.md", "hacs.json")
# Files inside custom_components/<domain>/
REQUIRED_FILES = ("__init__.py", "manifest.json", "strings.json", "translations/en.json", "brand/icon.png")
VERSION = re.compile(r"\d+\.\d+\.\d+")


def manifest_path(root: Path, domain: str) -> Path:
    return root / "custom_components" / domain / "manifest.json"


def load(root: Path, domain: str) -> dict:
    return json.loads(manifest_path(root, domain).read_text(encoding="utf-8"))


def info(root: Path, domain: str) -> dict:
    manifest = load(root, domain)
    return {"name": manifest["name"], "version": str(manifest.get("version", ""))}


def check(root: Path, domain: str) -> list[str]:
    folder = root / "custom_components" / domain
    if not manifest_path(root, domain).is_file():
        return [f"custom_components/{domain}/manifest.json not found – is '{domain}' the domain?"]
    problems = []
    others = sorted(p.parent.name for p in (root / "custom_components").glob("*/manifest.json"))
    others = [name for name in others if name != domain]
    if others:
        problems.append(f"one integration per repository – found further integrations {others}")
    for name in REQUIRED_ROOT_FILES:
        if not (root / name).is_file():
            problems.append(f"{name} is missing")
    for name in REQUIRED_FILES:
        if not (folder / name).is_file():
            problems.append(f"custom_components/{domain}/{name} is missing")
    manifest = load(root, domain)
    if manifest.get("domain") != domain:
        problems.append(f"manifest.json: domain must be the folder name '{domain}'")
    if not VERSION.fullmatch(str(manifest.get("version", ""))):
        problems.append("manifest.json: version must look like 1.2.3")
    for key in ("documentation", "issue_tracker", "codeowners"):
        if not manifest.get(key):
            problems.append(f"manifest.json: '{key}' is missing")
    if (root / "hacs.json").is_file():
        hacs = json.loads((root / "hacs.json").read_text(encoding="utf-8"))
        if not hacs.get("name"):
            problems.append("hacs.json: 'name' is missing")
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for heading in ("## English", "## Deutsch"):
            if not re.search(rf"^{heading}\s*$", text, re.M):
                problems.append(f"README.md: section '{heading}' is missing (one README with both languages)")
    if (root / "CHANGELOG.md").is_file() and not re.search(
        r"^## ", (root / "CHANGELOG.md").read_text(encoding="utf-8"), re.M
    ):
        problems.append("CHANGELOG.md has no version or '## Unreleased' section")
    return problems


def set_version(root: Path, domain: str, version: str) -> None:
    if not VERSION.fullmatch(version):
        raise ValueError("version must look like 1.2.3")
    path = manifest_path(root, domain)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["version"] = version
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def output(values: dict) -> None:
    for key, value in values.items():
        print(f"{key}={value}")


def main(argv: list[str]) -> None:
    if len(argv) < 4 or argv[1] not in ("check", "info", "set-version"):
        sys.exit(__doc__)
    command, root, domain = argv[1], Path(argv[2]).resolve(), argv[3]
    if command == "info":
        output(info(root, domain))
        return
    if command == "set-version":
        if len(argv) != 5:
            sys.exit(__doc__)
        set_version(root, domain, argv[4])
        return
    problems = check(root, domain)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        sys.exit(1)
    print(f"{domain}: OK")


if __name__ == "__main__":
    main(sys.argv)
