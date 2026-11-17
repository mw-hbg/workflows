"""Tests for the shared scripts (run by .github/workflows/self-test.yml)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_translations  # noqa: E402
import ha_app  # noqa: E402
import upstream  # noqa: E402

CONFIG = """\
name: Demo
version: "1.2.3"
slug: demo
image: ghcr.io/mw-hbg/{arch}-app-demo
arch: [amd64, aarch64]
"""


def make_app(root: Path, config: str = CONFIG) -> Path:
    (root / "repository.yaml").write_text("name: x\n")
    app = root / "demo"
    (app / "translations").mkdir(parents=True)
    for name in ha_app.REQUIRED_FILES:
        (app / name).write_text("x")
    for name in ("README.md", "DOCS.md"):
        (app / name).write_text("# Demo\n\n## English\n\nHi\n\n## Deutsch\n\nHallo\n")
    (app / "config.yaml").write_text(config)
    return app


def test_valid_app(tmp_path):
    make_app(tmp_path)
    assert ha_app.check(tmp_path, "demo") == []
    info = ha_app.info(tmp_path, "demo")
    assert info["version"] == "1.2.3"
    assert [b["runner"] for b in info["builds"]] == ["ubuntu-latest", "ubuntu-24.04-arm"]
    assert all(b["native"] for b in info["builds"])


def test_missing_files_and_second_app(tmp_path):
    app = make_app(tmp_path)
    (app / "apparmor.txt").unlink()
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "config.yaml").write_text("slug: other\n")
    problems = "\n".join(ha_app.check(tmp_path, "demo"))
    assert "apparmor.txt is missing" in problems
    assert "one app per repository" in problems


def test_readme_and_docs_hold_both_languages(tmp_path):
    app = make_app(tmp_path)
    (app / "DOCS.md").write_text("# Demo\n\n## English\n\nHi\n")
    (app / "README.de.md").write_text("# Demo\n")
    problems = "\n".join(ha_app.check(tmp_path, "demo"))
    assert "DOCS.md: section '## Deutsch' is missing" in problems
    assert "README.de.md: Home Assistant never shows it" in problems


def test_sensitive_access_needs_allowance(tmp_path):
    make_app(tmp_path, CONFIG + "homeassistant_api: true\n")
    assert any("homeassistant_api" in p for p in ha_app.check(tmp_path, "demo"))
    assert ha_app.check(tmp_path, "demo", frozenset({"homeassistant_api"})) == []


def test_bad_image_slug_and_version(tmp_path):
    make_app(tmp_path, CONFIG.replace("slug: demo", "slug: x").replace("ghcr.io", "docker.io").replace('"1.2.3"', "dev"))
    problems = "\n".join(ha_app.check(tmp_path, "demo"))
    assert "slug" in problems and "image" in problems and "version" in problems


def write(path: Path, data) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return str(path)


def test_translations_complete(tmp_path):
    write(tmp_path / "i18n/en.json", {"a": "Hi {name}", "b": {"c": "x"}})
    write(tmp_path / "i18n/de.json", {"a": "Hallo {name}", "b": {"c": "y"}})
    files, problems = check_translations.check_group(f"{tmp_path}/i18n/*.json")
    assert len(files) == 2 and problems == []


def test_translations_missing_extra_and_placeholders(tmp_path):
    write(tmp_path / "i18n/en.json", {"a": "Hi {name}", "b": {"c": "x"}})
    write(tmp_path / "i18n/de.json", {"a": "Hallo", "d": "?"})
    _, problems = check_translations.check_group(f"{tmp_path}/i18n/*.json")
    text = "\n".join(problems)
    assert "missing ['b.c']" in text and "unknown keys ['d']" in text and "placeholders" in text


def test_translations_yaml_and_several_patterns(tmp_path):
    (tmp_path / "strings.json").write_text('{"x": "1"}')
    (tmp_path / "t").mkdir()
    (tmp_path / "t/en.yaml").write_text("x: one\n")
    (tmp_path / "t/de.yaml").write_text("x: eins\ny: zwei\n")
    files, problems = check_translations.check_group(f"{tmp_path}/strings.json {tmp_path}/t/*.yaml")
    assert len(files) == 3
    assert len(problems) == 1 and "unknown keys ['y']" in problems[0]


def test_translations_no_files(tmp_path):
    assert check_translations.check_group(f"{tmp_path}/nothing/*.json")[1]


def test_upstream(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM x\nARG UPSTREAM_REF=abc123\n")
    (tmp_path / "upstream.yaml").write_text(
        "name: Demo\nrepo: owner/demo\nfile: Dockerfile\npattern: '^ARG UPSTREAM_REF=(\\S+)'\n"
    )
    values = upstream.read(tmp_path / "upstream.yaml")
    assert values["PINNED"] == "abc123" and values["BRANCH"] == "main" and values["REPO"] == "owner/demo"


def test_upstream_rejects_odd_repo(tmp_path):
    (tmp_path / "Dockerfile").write_text("ARG UPSTREAM_REF=abc\n")
    (tmp_path / "upstream.yaml").write_text(
        "name: D\nrepo: 'x; rm -rf /'\nfile: Dockerfile\npattern: '^ARG UPSTREAM_REF=(\\S+)'\n"
    )
    with pytest.raises(SystemExit):
        upstream.read(tmp_path / "upstream.yaml")


# --- ha_integration.py ------------------------------------------------------
import ha_integration  # noqa: E402

MANIFEST = {
    "domain": "demo",
    "name": "Demo",
    "codeowners": ["@mw-hbg"],
    "documentation": "https://example.org",
    "issue_tracker": "https://example.org/issues",
    "version": "0.1.0",
}


def make_integration(root: Path, manifest: dict = MANIFEST) -> Path:
    for name in ha_integration.REQUIRED_ROOT_FILES:
        text = {"CHANGELOG.md": "## Unreleased\n", "README.md": "# Demo\n\n## English\n\nx\n\n## Deutsch\n\nx\n"}
        (root / name).write_text(text.get(name, "x"))
    (root / "hacs.json").write_text('{"name": "Demo"}')
    folder = root / "custom_components" / "demo"
    for name in ha_integration.REQUIRED_FILES:
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text("x")
    (folder / "manifest.json").write_text(json.dumps(manifest))
    return folder


def test_valid_integration(tmp_path):
    make_integration(tmp_path)
    assert ha_integration.check(tmp_path, "demo") == []
    assert ha_integration.info(tmp_path, "demo") == {"name": "Demo", "version": "0.1.0"}


def test_integration_problems(tmp_path):
    folder = make_integration(tmp_path, {**MANIFEST, "domain": "other", "version": "1.0"})
    (folder / "brand" / "icon.png").unlink()
    (tmp_path / "SECURITY.md").unlink()
    (tmp_path / "README.md").write_text("# Demo\n\n## English\n")
    second = tmp_path / "custom_components" / "second"
    second.mkdir()
    (second / "manifest.json").write_text("{}")
    problems = "\n".join(ha_integration.check(tmp_path, "demo"))
    for expected in ("one integration per repository", "brand/icon.png", "SECURITY.md", "domain must", "1.2.3", "## Deutsch"):
        assert expected in problems


def test_integration_missing(tmp_path):
    assert "not found" in ha_integration.check(tmp_path, "demo")[0]


def test_set_version_keeps_order(tmp_path):
    folder = make_integration(tmp_path)
    ha_integration.set_version(tmp_path, "demo", "0.2.0")
    data = json.loads((folder / "manifest.json").read_text())
    assert data["version"] == "0.2.0"
    assert list(data)[:2] == ["domain", "name"]
    with pytest.raises(ValueError):
        ha_integration.set_version(tmp_path, "demo", "v1")
