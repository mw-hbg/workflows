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
| [`ha-integration-test.yml`](.github/workflows/ha-integration-test.yml) | Home Assistant integration (Marketplace): repository checks, hassfest, Marketplace validation, lint, unit tests |
| [`ha-integration-release.yml`](.github/workflows/ha-integration-release.yml) | Home Assistant integration: tests, then set the version in `manifest.json`, finish the changelog, tag and create the GitHub release (= Marketplace update) |
| [`translations-check.yml`](.github/workflows/translations-check.yml) | every language has the same texts and placeholders as English |
| [`upstream-check.yml`](.github/workflows/upstream-check.yml) | weekly: opens an issue when a pinned upstream project has new commits |
| [`releases-as-owner.yml`](.github/workflows/releases-as-owner.yml) | once, by hand: recreates releases made by a bot under the owner's name |

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

**Everything under the owner's name:** releases need the secret `RELEASE_TOKEN` – a
fine-grained personal access token of the owner (only the project repository,
permission *Contents: read and write*). Release commit, tag and GitHub release are then
made as the owner, never as a bot. Dependabot pull requests are not merged on GitHub;
their change is committed by the owner instead (otherwise Dependabot becomes a
contributor).

Rules the app checks enforce: one app per repository, `apparmor.txt`,
`README.md`, `DOCS.md`, `CHANGELOG.md`, English option translations, image
`ghcr.io/<owner>/{arch}-app-<name>`, version `x.y.z`, and no wide access
(Home Assistant API, host network, privileged …) unless the repository lists it
in `allowed-access` and explains why in its security policy.

Rules the integration checks enforce: one integration per repository in
`custom_components/<domain>/`, `README.md` with the sections `## English` and
`## Deutsch` (the Marketplace only shows README.md), `CHANGELOG.md`,
`LICENSE`, `SECURITY.md`, `hacs.json`, `strings.json` with English
translation, `brand/icon.png`, domain = folder name, version `x.y.z`.

## Deutsch

Gemeinsame GitHub-Actions-Workflows für alle Repositories von
[mw-hbg](https://github.com/mw-hbg) – ein Projekt pro Repository, alles
Gemeinsame liegt hier. (Standard-Issue-Formulare und Sicherheitsrichtlinie liegen
in [mw-hbg/.github](https://github.com/mw-hbg/.github).)

| Workflow | Was er macht |
|---|---|
| [`ha-app-test.yml`](.github/workflows/ha-app-test.yml) | Home-Assistant-App: Repository-Prüfung, Lint, Unit-Tests, Build für jede Architektur auf nativen Runnern, Smoke-Test |
| [`ha-app-release.yml`](.github/workflows/ha-app-release.yml) | Home-Assistant-App: erst Images bauen und hochladen, dann Version erhöhen, Changelog abschließen, Tag und GitHub-Release |
| [`ha-integration-test.yml`](.github/workflows/ha-integration-test.yml) | Home-Assistant-Integration (Marketplace): Repository-Prüfung, hassfest, Marketplace-Prüfung, Lint, Unit-Tests |
| [`ha-integration-release.yml`](.github/workflows/ha-integration-release.yml) | Home-Assistant-Integration: Tests, dann Version in `manifest.json` setzen, Changelog abschließen, Tag und GitHub-Release (= Marketplace-Update) |
| [`translations-check.yml`](.github/workflows/translations-check.yml) | jede Sprache hat dieselben Texte und Platzhalter wie Englisch |
| [`upstream-check.yml`](.github/workflows/upstream-check.yml) | wöchentlich: legt ein Issue an, wenn ein festgelegtes Fremdprojekt neue Commits hat |
| [`releases-as-owner.yml`](.github/workflows/releases-as-owner.yml) | einmalig von Hand: legt Releases, die ein Bot erstellt hat, unter dem Namen des Besitzers neu an |

Beispiele zur Einbindung stehen oben in jeder Workflow-Datei. Die Skripte dazu
liegen in [`scripts/`](scripts) und werden vom Workflow *Self test* geprüft.

**Alles unter dem Namen des Besitzers:** Releases brauchen das Secret `RELEASE_TOKEN` –
ein feingranularer persönlicher Zugangstoken des Besitzers (nur das Projekt-Repository,
Berechtigung *Contents: read and write*). Release-Commit, Tag und GitHub-Release entstehen
dann unter dem Besitzer, nie unter einem Bot. Dependabot-Pull-Requests werden nicht auf
GitHub zusammengeführt; ihre Änderung committet der Besitzer selbst (sonst wird
Dependabot Contributor).

Was die App-Prüfung erzwingt: eine App pro Repository, `apparmor.txt`,
`README.md`, `DOCS.md`, `CHANGELOG.md`, englische Options-Übersetzung, Image
`ghcr.io/<owner>/{arch}-app-<name>`, Version `x.y.z` und kein weitreichender
Zugriff (Home-Assistant-API, Host-Netzwerk, privilegiert …), außer das
Repository nennt ihn in `allowed-access` und begründet ihn in seiner
Sicherheitsrichtlinie.

Was die Integrations-Prüfung erzwingt: eine Integration pro Repository in
`custom_components/<domain>/`, `README.md` mit den Abschnitten `## English` und
`## Deutsch` (der Marketplace zeigt nur README.md), `CHANGELOG.md`,
`LICENSE`, `SECURITY.md`, `hacs.json`, `strings.json` mit englischer
Übersetzung, `brand/icon.png`, Domain = Ordnername, Version `x.y.z`.

## License / Lizenz

[MIT](LICENSE)
