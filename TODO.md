# TODO — DD Tools

## Bezpečnost
- [x] **Rate limiting** — 60 requestů za minutu na IP (Flask-Limiter)
- [x] **robots.txt** — zakázána indexace (`Disallow: /`)
- [x] **Sanitizace vstupů — délkové limity** — ve všech libs, XXE ochrana v XML (defusedxml)
- [ ] **Rate limiting na login** — `@limiter.limit("5 per minute; 20 per hour")` na `/login` route
- [ ] **Custom 429 stránka pro login** — vtipná hláška pro útočníky, vyber variantu:
  - 🇨🇿 *"Tohle zvládne jen Tupoun, a to ty nebudeš. Pokud se pletu, máš přesto smůlu, musíš být totiž Tupý Tupoun, a ne jen obyčejný Tupoun. A to ty určitě nejsi, že?"*
  - 🇬🇧 *"Only a true Dunce gets in here — and you're clearly not one. If I'm wrong, you're still out of luck, because you'd need to be a Supreme Dunce, not just a regular one. And we both know that's not you, right?"*
  - 🇮🇳 *"यहाँ केवल एक सच्चा मूर्ख ही घुस सकता है — और तुम स्पष्ट रूप से वो नहीं हो। अगर मैं गलत हूँ, तो भी तुम्हारी किस्मत खराब है, क्योंकि तुम्हें सिर्फ मूर्ख नहीं, बल्कि महामूर्ख होना पड़ेगा। और वो तुम निश्चित रूप से नहीं हो, है ना?"*
- [ ] **Sanitizace vstupů — hloubka JSON/YAML** — limit rekurze při parsování, délkový limit nestačí
- [ ] **Sanitizace vstupů — validace file uploadu** — encoding converter by měl odmítat binární soubory, omezit na text/*
- [ ] **Sanitizace vstupů — audit šablon** — zkontrolovat že žádná šablona nepoužívá `| safe` na uživatelský vstup (XSS riziko)

## Testování
- [ ] **CI — pytest před deployem** — přidat GitHub Actions krok který spustí testy před rsync na Rosti.cz; deploy se nespustí pokud testy selžou
- [ ] **Testy** — složka `tests/` zatím prázdná, postupně přidávat testy k existující i nové logice