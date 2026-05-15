# TODO — DD Tools

## Bezpečnost
- [x] **Rate limiting** — 60 requestů za minutu na IP (Flask-Limiter)
- [x] **robots.txt** — zakázána indexace (`Disallow: /`)
- [ ] **Sanitizace vstupů** — důsledně validovat vstupy ve všech nástrojích v `libs/`

## Testování
- [ ] **CI — pytest před deployem** — přidat GitHub Actions krok který spustí testy před rsync na Rosti.cz; deploy se nespustí pokud testy selžou
- [ ] **Testy** — složka `tests/` zatím prázdná, postupně přidávat testy k existující i nové logice
