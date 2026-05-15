# TODO — DD Tools

## Bezpečnost
- [x] **Rate limiting** — 60 requestů za minutu na IP (Flask-Limiter)
- [x] **robots.txt** — zakázána indexace (`Disallow: /`)
- [x] **Sanitizace vstupů — délkové limity** — ve všech libs, XXE ochrana v XML (defusedxml)
- [ ] **Sanitizace vstupů — hloubka JSON/YAML** — limit rekurze při parsování, délkový limit nestačí
- [ ] **Sanitizace vstupů — validace file uploadu** — encoding converter by měl odmítat binární soubory, omezit na text/*
- [ ] **Sanitizace vstupů — audit šablon** — zkontrolovat že žádná šablona nepoužívá `| safe` na uživatelský vstup (XSS riziko)

## Testování
- [ ] **CI — pytest před deployem** — přidat GitHub Actions krok který spustí testy před rsync na Rosti.cz; deploy se nespustí pokud testy selžou
- [ ] **Testy** — složka `tests/` zatím prázdná, postupně přidávat testy k existující i nové logice
