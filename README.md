# DD Tools

Webová aplikace s užitečnými nástroji pro práci s textem.

## Aktuální nástroje

- **Převod kódování** - Převod textových souborů mezi různými kódováními (UTF-8, Windows-1250, CP852, ISO-8859-1/2/15)

## Instalace

### Lokálně

```bash
# Naklonuj repozitář
git clone <repository-url>
cd dd-tools

# Vytvoř virtuální prostředí
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate  # Windows

# Nainstaluj závislosti
pip install -r requirements.txt

# Spusť aplikaci
python app.py
```

Aplikace poběží na `http://localhost:5000`

### Hosting na Rosti.cz

1. Nahraj projekt do Git repozitáře
2. V Rosti.cz vytvoř novou Python aplikaci
3. Nastav:
   - Repository URL
   - Branch: `main`
   - Python verze: 3.11+
   - Start command: `gunicorn app:app`
4. Přidej `gunicorn` do `requirements.txt`

## Struktura projektu

```
dd-tools/
├── app.py              # Flask aplikace
├── libs/               # Knihovny s core logikou
│   └── encoding_converter.py
├── templates/          # HTML šablony
│   ├── base.html
│   ├── index.html
│   └── encoding.html
├── static/             # CSS, JS
│   └── style.css
├── requirements.txt    # Python závislosti
└── README.md
```

## Přidání nového nástroje

1. Vytvoř nový modul v `libs/`
2. Přidej route v `app.py`
3. Vytvoř šablonu v `templates/`
4. Zaregistruj nástroj v `TOOLS` listu v `app.py`

## Barevné schéma

Aplikace používá burgundy barevné schéma:
- Hlavní: `#9B1B30`
- Tmavší: `#800020`
- Světlejší: `#B22746`

## License

Personal project - DD Elektro
