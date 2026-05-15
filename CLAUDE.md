# DD Tools — CLAUDE.md

> Pravidla pro psaní kódu a Git konvence jsou v `INSTRUCTIONS.md`.

## Stack
- **Backend:** Python 3.13 + Flask, Jinja2 šablony, gunicorn
- **Frontend:** vanilla HTML/CSS/JS, žádný framework
- **Deploy:** Rosti.cz přes GitHub Actions (branch `master`)

## Struktura projektu
```
app.py                  # Flask routes + TOOLS registrace
libs/                   # Business logika (jeden modul = jeden nástroj)
templates/              # Jinja2 šablony (base.html + per-tool)
static/style.css        # Fialové téma (CSS variables)
requirements.txt
.github/workflows/main.yml
```

## Jak přidat nový nástroj
1. Vytvoř `libs/<nazev>.py` — vrací `(result, error)` tuply
2. Přidej route v `app.py` (`GET/POST` pattern jako ostatní)
3. Vytvoř `templates/<nazev>.html` — extends `base.html`
4. Zaregistruj do `TOOLS` listu v `app.py` (id, name, description, route)

## Konvence
- Lib funkce vždy vracejí `(result, error)` — `error` je `None` při úspěchu
- Template proměnné: `result`, `form_data` (zachování stavu formuláře po POST)
- Výsledky v `<pre class="result-pre">` — copy button přidává JS automaticky
- Chyby přes `result.error` v template, ne flash (flash jen pro redirect flow)
- Max délka ve formulářích ošetřena v lib, ne v route

## Styling
- CSS variables v `:root` — fialová paleta (`--purple-*`)
- Karty: `.card`, tlačítka: `.btn.btn-primary`, vstupy: `.form-control`
- Barvy nekóduj inline — vždy `var(--purple-main)` apod.

## Environment
- `SECRET_KEY` — povinná env proměnná (Flask session)
- Na Rosti.cz injektována přes supervisor `environment=`

## Deploy
Push na `master` → GitHub Actions → rsync na Rosti.cz → pip install → supervisorctl restart
Health check: `https://drazan.cz`
