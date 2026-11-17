"""Information about a Home Assistant app repository, for the shared workflows.

A repository holds exactly one app: repository.yaml at the root and the app in
the folder <app>/ (Home Assistant requires that layout).

  python ha_app.py check <repo-root> <app> [allowed]   consistency checks (fails on problems)
  python ha_app.py info  <repo-root> <app>   GitHub outputs: name, version, image, builds
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

PLATFORMS = {
    "amd64": "linux/amd64",
    "aarch64": "linux/arm64",
    "armv7": "linux/arm/v7",
    "armhf": "linux/arm/v6",
    "i386": "linux/386",
}
# Where each architecture is built. amd64 and aarch64 run natively on GitHub's
# free x64 and arm64 runners (public repositories); others are emulated (QEMU).
RUNNERS = {
    "amd64": ("ubuntu-latest", False),
    "aarch64": ("ubuntu-24.04-arm", False),
    "armv7": ("ubuntu-24.04-arm", True),
    "armhf": ("ubuntu-24.04-arm", True),
    "i386": ("ubuntu-latest", True),
}
# Every app must ship these (security and bilingual documentation are not optional)
REQUIRED_FILES = (
    "config.yaml",
    "Dockerfile",
    "apparmor.txt",
    "README.md",
    "DOCS.md",
    "CHANGELOG.md",
    "icon.png",
    "logo.png",
    "translations/en.yaml",
)
# Wide access a security-first app should not need. A repository that really
# needs one lists it in the workflow input "allowed-access" – and explains why
# in its SECURITY.md.
SENSITIVE = (
    "homeassistant_api",
    "hassio_api",
    "auth_api",
    "host_network",
    "host_pid",
    "full_access",
    "privileged",
    "docker_api",
    "devices",
    "uart",
    "usb",
    "gpio",
    "kernel_modules",
)
IMAGE = re.compile(r"ghcr\.io/[a-z0-9-]+/\{arch\}-app-[a-z0-9-]+")


def load(root: Path, app: str) -> dict:
    return yaml.safe_load((root / app / "config.yaml").read_text(encoding="utf-8"))


def info(root: Path, app: str) -> dict:
    cfg = load(root, app)
    archs = list(cfg.get("arch", []))
    return {
        "name": cfg["name"],
        "version": str(cfg["version"]),
        "image": str(cfg.get("image", "")),
        "builds": [
            {
                "arch": arch,
                "platform": PLATFORMS[arch],
                "runner": RUNNERS[arch][0],
                # native = no emulation; only native builds can run the smoke test
                "native": not RUNNERS[arch][1],
            }
            for arch in archs
        ],
    }


def check(root: Path, app: str, allowed: frozenset[str] = frozenset()) -> list[str]:
    folder = root / app
    if not (folder / "config.yaml").is_file():
        return [f"{app}/config.yaml not found – is '{app}' the app folder?"]
    problems = []
    if not (root / "repository.yaml").is_file():
        problems.append("repository.yaml is missing at the repository root")
    others = sorted(p.parent.name for p in root.glob("*/config.yaml") if p.parent.name != app)
    if others:
        problems.append(f"one app per repository – found further app folders {others}")
    for name in REQUIRED_FILES:
        if not (folder / name).exists():
            problems.append(f"{app}/{name} is missing")
    cfg = load(root, app)
    if cfg.get("slug") != app:
        problems.append(f"{app}/config.yaml: slug must be the folder name '{app}'")
    if not IMAGE.fullmatch(str(cfg.get("image", ""))):
        problems.append(f"{app}/config.yaml: image must look like ghcr.io/<owner>/{{arch}}-app-<name>")
    if not cfg.get("arch"):
        problems.append(f"{app}/config.yaml: no arch listed")
    for arch in cfg.get("arch", []):
        if arch not in PLATFORMS:
            problems.append(f"{app}/config.yaml: unknown arch {arch}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(cfg.get("version", ""))):
        problems.append(f"{app}/config.yaml: version must look like 1.2.3")
    for key in SENSITIVE:
        if cfg.get(key) and key not in allowed:
            problems.append(f"{app}/config.yaml: '{key}' is enabled – not allowed unless listed in the workflow input allowed-access")
    return problems


def output(values: dict) -> None:
    for key, value in values.items():
        text = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
        print(f"{key}={text}")


def main(argv: list[str]) -> None:
    if len(argv) not in (4, 5) or argv[1] not in ("check", "info"):
        sys.exit(__doc__)
    command, root, app = argv[1], Path(argv[2]).resolve(), argv[3]
    allowed = frozenset(k.strip() for k in (argv[4] if len(argv) == 5 else "").replace(",", " ").split())
    if command == "info":
        output(info(root, app))
        return
    problems = check(root, app, allowed)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        sys.exit(1)
    print(f"{app}: OK")


if __name__ == "__main__":
    main(sys.argv)
