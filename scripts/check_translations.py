"""Check that every language of a set of translation files is complete.

Each argument is one group of files that must have the same texts, given as
glob patterns separated by spaces, e.g.

  python check_translations.py "app/i18n/*.json" \\
      "custom_components/x/strings.json custom_components/x/translations/*.json"

Within a group the English file (en.json / en.yaml, otherwise the first file
found) is the reference. Every other file must have exactly the same keys
(nested keys included) and, per text, the same {placeholders}. Files may be
JSON or YAML.
"""

from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import yaml

PLACEHOLDER = re.compile(r"(?<!\{)\{(\w*)\}(?!\})")


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def flatten(data, prefix: str = "") -> dict[str, object]:
    """{"a": {"b": "x"}} → {"a.b": "x"}; lists count as one value."""
    if isinstance(data, dict):
        flat: dict[str, object] = {}
        for key, value in data.items():
            flat.update(flatten(value, f"{prefix}{key}."))
        return flat
    return {prefix.rstrip("."): data}


def placeholders(value) -> set[str]:
    return set(PLACEHOLDER.findall(value)) if isinstance(value, str) else set()


def check_group(patterns: str) -> tuple[list[Path], list[str]]:
    files = sorted({Path(p) for pattern in patterns.split() for p in glob.glob(pattern, recursive=True)})
    if not files:
        return [], [f"no files match '{patterns}'"]
    english = [f for f in files if f.stem == "en"]
    reference = english[0] if english else files[0]
    base = flatten(load(reference))
    problems = []
    for path in files:
        if path == reference:
            continue
        other = flatten(load(path))
        missing = sorted(set(base) - set(other))
        extra = sorted(set(other) - set(base))
        if missing:
            problems.append(f"{path}: missing {missing} (compared with {reference})")
        if extra:
            problems.append(f"{path}: unknown keys {extra} (not in {reference})")
        for key in sorted(set(base) & set(other)):
            if placeholders(base[key]) != placeholders(other[key]):
                problems.append(
                    f"{path}: '{key}' has placeholders {sorted(placeholders(other[key]))},"
                    f" {reference} has {sorted(placeholders(base[key]))}"
                )
    return files, problems


def main(groups: list[str]) -> None:
    if not groups:
        sys.exit(__doc__)
    failed = False
    for patterns in groups:
        files, problems = check_group(patterns)
        for problem in problems:
            print(f"::error::{problem}")
        failed |= bool(problems)
        if not problems:
            print(f"OK ({len(files)} files): {', '.join(map(str, files))}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main([g for g in sys.argv[1:] if g.strip()])
