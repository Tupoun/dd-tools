# Instrukce pro Claude — DD Tools

## Projekt
Flask webová aplikace s utility nástroji pro testování a development (textové konverze, generátory, parsery). Python backend, vanilla frontend, deploy na Rosti.cz.

## Při úpravě existujícího nástroje
- Logiku piš do `libs/<modul>.py`, ne do route v `app.py`
- Route je jen thin wrapper: vezme form data → zavolá lib → předá do template
- Zachovej `(result, error)` return pattern
- Zachovej `form_data` dict pro re-populate formuláře po POST

## Při přidávání nového nástroje
Potřebuješ 4 soubory/změny:
1. `libs/<nazev>.py` — pure Python logika
2. `templates/<nazev>.html` — extends base.html, stejná struktura jako ostatní
3. Route v `app.py` — GET/POST, render_template s `tools=TOOLS`
4. Záznam v `TOOLS` listu v `app.py`

## Coding styl
- DRY (Don't Repeat Yourself) — sdílenou logiku extrahuj do pomocné funkce nebo modulu
- KISS (Keep It Simple, Stupid) — nejjednodušší řešení které funguje, nepřekombinovat
- YAGNI (You Aren't Gonna Need It) — implementuj jen co je teď potřeba, ne co by se mohlo hodit
- Python: žádné externí závislosti pokud není nutné (stdlib preferována)
- Pojmenování: snake_case pro funkce a proměnné, PascalCase pro třídy
- Exceptions: catch a vrať jako `(None, "popis chyby")`, nepoužívej raise do route
- Templates: Jinja2, formulář vždy `method="POST"`, bez JS frameworků
- CSS: přidávej styly do `static/style.css`, používej existující CSS variables

## Testování
- Testy patří do složky `tests/`, ne vedle lib souborů
- Používej pytest
- Při přidání nové logiky do `libs/` navrhni odpovídající test
- Testy se na Rosti.cz nenasazují (jsou excludovány z rsync)

## Git konvence
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Branch naming: `feat/nazev`, `fix/nazev`, `chore/nazev`
- Vždy pracuj na větvi, ne přímo na `master`

## Co neměnit bez explicitního zadání
- `base.html` — layout a sidebar
- `static/style.css` barevné schéma (CSS variables v `:root`)
- Deploy workflow `.github/workflows/main.yml`
- `SECRET_KEY` handling v `app.py`
