"""Read an upstream.yaml: which upstream project is pinned to which commit.

  python upstream.py <path/to/upstream.yaml>

Prints shell assignments (NAME, REPO, BRANCH, PIN_FILE, PINNED) for eval.

upstream.yaml format (paths are relative to the folder of upstream.yaml):

  name: Garmin MCP server         # shown in the issue
  repo: Taxuspt/garmin_mcp        # GitHub owner/repo
  branch: main                    # optional, default main
  file: Dockerfile                # file holding the pinned commit
  pattern: '^ARG UPSTREAM_REF=(\\S+)'   # regex, group 1 = pinned commit
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

import yaml


def read(path: Path) -> dict[str, str]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    pin_file = path.parent / cfg["file"]
    match = re.search(cfg["pattern"], pin_file.read_text(encoding="utf-8"), re.M)
    if not match:
        raise SystemExit(f"::error::{pin_file}: pattern {cfg['pattern']!r} not found")
    repo = str(cfg["repo"])
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise SystemExit(f"::error::{path}: repo must look like owner/name")
    return {
        "NAME": str(cfg["name"]),
        "REPO": repo,
        "BRANCH": str(cfg.get("branch", "main")),
        "PIN_FILE": str(pin_file),
        "PINNED": match.group(1),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for key, value in read(Path(sys.argv[1])).items():
        print(f"{key}={shlex.quote(value)}")
