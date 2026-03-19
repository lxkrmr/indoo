# PLAN

## Ziel

Kleines lokales Tool fuer Odoo-Entwicklung bauen, das Boilerplate fuer Record-Inspektion abnimmt.

Schwerpunkt:
- konkrete Records anschauen
- computed fields pruefen
- `@api.depends`-Verhalten nachvollziehen
- Werte schreiben und direkt danach erneut lesen
- Ergebnisse leicht als JSON mit Codex teilen

## Entscheidungen

- Python-Projekt mit `uv`
- CLI mit `typer`
- Odoo-Zugriff vorerst ueber `odoorpc`
- Output ist MCP-inspiriert: strukturiertes JSON
- Verbindung nur ueber projektlokale Profile
- keine globalen Env Vars
- kein Fallback-System

## Verbindungsmodell

Es gibt genau einen Weg:

Projektdatei `.odoo-lab.toml`

Beispiel:

```toml
[profiles.local]
url = "http://localhost:8069"
db = "odoo"
user = "admin"
password = "admin"
```

Verwendung:

```bash
uv run odoo-lab show res.partner 1 name --profile local
```

## Bereits umgesetzt

- `uv`-Projekt initialisiert
- lokale virtuelle Umgebung ueber `uv sync`
- CLI-Binary `odoo-lab`
- Command `show`
- Command `write-and-show`
- Parsing fuer `--value key=value`
- Parsing fuer `--context key=value`
- JSON-Ausgabe fuer Records und Before/After-Vergleiche
- Beispiel-Datei `.odoo-lab.example.toml`
- README mit aktueller Nutzung

## Relevante Dateien

- `pyproject.toml`
- `src/odoo_lab/client.py`
- `src/odoo_lab/cli.py`
- `README.md`
- `.odoo-lab.example.toml`

## Aktueller CLI-Stand

Show:

```bash
uv run odoo-lab show your.model 42 field_x computed_y --profile local
```

Write and show:

```bash
uv run odoo-lab write-and-show your.model 42 field_x computed_y --profile local --value field_x=10
```

## Was noch offen ist

1. Echte `.odoo-lab.toml` im Projekt anlegen
2. Gegen lokales Odoo verbinden
3. Mit echten Records testen
4. Pruefen, ob `write-and-show` fuer euren `@api.depends`-Workflow schon reicht
5. Danach entscheiden, was als Naechstes am meisten hilft

Moegliche naechste Features:
- `ping` oder `whoami`
- `ref <xmlid>`
- `search`
- lesbarere Ausgabe fuer Relations
- Diff-Ausgabe noch kompakter machen
- kleine gespeicherte Debug-Cases

## Commits bisher

- `5263900` `chore(project): initialize uv workspace`
- `d62441d` `feat(cli): add Odoo record inspection commands`
- `a48b2e5` `docs(readme): add local usage examples`
- `0f7bd88` `feat(config): load Odoo connections from local profiles`

## Wichtig fuer morgen

- Nutzer moechte kleine sinnvolle Commits
- Commit-Format: Conventional Commits mit Scope
- Committen ist erlaubt
- Push macht der Nutzer selbst
- ein klarer Weg ist wichtiger als mehrere Optionen
