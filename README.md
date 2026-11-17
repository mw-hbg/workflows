# mw-hbg/workflows

[English](#english) · [Deutsch](#deutsch)

## English

Shared GitHub Actions workflows for all repositories of
[mw-hbg](https://github.com/mw-hbg) – one project per repository, everything
common lives here. (Default issue forms and the security policy are in
[mw-hbg/.github](https://github.com/mw-hbg/.github).)

| Workflow | What it does |
|---|---|
| [`ha-app-test.yml`](.github/workflows/ha-app-test.yml) | Home Assistant app: repository checks, lint, unit tests, build for every architecture on native runners, smoke test |
| [`ha-app-release.yml`](.github/workflows/ha-app-release.yml) | Home Assistant app: build and push images first, then raise the version, finish the changelog, tag and create the GitHub release |
| [`translations-check.yml`](.github/workflows/translations-check.yml) | every language has the same texts and placeholders as English |
| [`upstream-check.yml`](.github/workflows/upstream-check.yml) | weekly: opens an issue when a pinned upstream project has new commits |

Usage examples are at the top of each workflow file, e.g.

```yaml
jobs:
  app:
    uses: mw-hbg/workflows/.github/workflows/ha-app-test.yml@main
    with:
      app: my_app
```

The scripts behind them are in [`scripts/`](scripts) and tested by the
*Self test* workflow.

Rules the app checks enforce: one app per repository, `apparmor.txt`,
`README.md`, `DOCS.md`, `CHANGELOG.md`, English option translations, image
`ghcr.io/<owner>/{arch}-app-<name>`, version `x.y.z`, and no wide access
(Home Assistant API, host network, privileged …) unless the repository lists it
in `allowed-access` and explains why in its security policy.

## Deutsch

Gemeinsame GitHub-Actions-Workflows für alle Repositories von
[mw-hbg](https://github.com/mw-hbg) – ein Projekt pro Repository, alles
Gemeinsame liegt hier. (Standard-Issue-Formulare und Sicherheitsrichtlinie liegen
in [mw-hbg/.github](https://github.com/mw-hbg/.github).)

| Workflow | Was er macht |
|---|---|
| [`ha-app-test.yml`](.github/workflows/ha-app-test.yml) | Home-Assistant-App: Repository-Prüfung, Lint, Unit-Tests, Build für jede Architektur auf nativen Runnern, Smoke-Test |
| [`ha-app-release.yml`](.github/workflows/ha-app-release.yml) | Home-Assistant-App: erst Images bauen und hochladen, dann Version erhöhen, Changelog abschließen, Tag und GitHub-Release |
| [`translations-check.yml`](.github/workflows/translations-check.yml) | jede Sprache hat dieselben Texte und Platzhalter wie Englisch |
| [`upstream-check.yml`](.github/workflows/upstream-check.yml) | wöchentlich: legt ein Issue an, wenn ein festgelegtes Fremdprojekt neue Commits hat |

Beispiele zur Einbindung stehen oben in jeder Workflow-Datei. Die Skripte dazu
liegen in [`scripts/`](scripts) und werden vom Workflow *Self test* geprüft.

Was die App-Prüfung erzwingt: eine App pro Repository, `apparmor.txt`,
`README.md`, `DOCS.md`, `CHANGELOG.md`, englische Options-Übersetzung, Image
`ghcr.io/<owner>/{arch}-app-<name>`, Version `x.y.z` und kein weitreichender
Zugriff (Home-Assistant-API, Host-Netzwerk, privilegiert …), außer das
Repository nennt ihn in `allowed-access` und begründet ihn in seiner
Sicherheitsrichtlinie.

## License / Lizenz

[MIT](LICENSE)
