# TODO — DD Tools

## Bezpečnost
- [ ] **Autentizace / login** — projekt běží veřejně na webu, přidat jednoduchý login
- [ ] **Sanitizace vstupů** — důsledně validovat vstupy ve všech nástrojích v `libs/`

## Testování
- [ ] **CI — pytest před deployem** — přidat GitHub Actions krok který spustí testy před rsync na Rosti.cz; deploy se nespustí pokud testy selžou
- [ ] **Testy** — složka `tests/` zatím prázdná, postupně přidávat testy k existující i nové logice
