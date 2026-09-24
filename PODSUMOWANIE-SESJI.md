# KOMpetition.cc – podsumowanie sesji (24.09.2026)

## Co powstało

Nowa strona kompetition.cc, zbudowana od zera jako następca strony na Squarespace. Znajduje się w folderze `kompetition-site/`, który jest też repozytorium git (remote: `https://github.com/kompetitioncc/strona-internetowa.git`, gałąź `main`).

### Strona (statyczny HTML/CSS/JS)
- **Wygląd:** nowoczesny design w barwach marki (czerń, biel, żółty `#ffd500`), fonty Barlow Condensed i Roboto hostowane lokalnie. Strona jest w pełni responsywna, ma wideo w nagłówku strony głównej i przyklejony pasek CTA na telefonach.
- **SEO:**
  - unikalne tytuły i opisy,
  - dane strukturalne JSON-LD: LocalBusiness, Person, FAQ, Product, BlogPosting, Service,
  - grafiki OG 1200×630 dla każdej strony,
  - sitemapa z obrazami, RSS,
  - obrazy WebP z srcset,
  - CSS wbudowany w strony,
  - przekierowania 301 ze starych adresów Squarespace (`_redirects`, `.htaccess`).
- **Strony:** główna, opieka trenerska (450 zł/mies.), o mnie, kontakt (formularz + kalendarz Google ładowany po kliknięciu), regulamin (dodany §12 o sprzedaży planów), polityka prywatności (nowa), kalkulator CP (oryginalny, z Tailwindem skompilowanym do statycznego CSS) i kalkulator GE.
- **Blog / KOMpedium wiedzy:** 7 artykułów, w tym dwa nowe:
  - „Heat training w kolarstwie – KOMpedium” (15 źródeł z PubMed, grafiki CORE, 5 protokołów),
  - „Słownik treningowy kolarza” (ponad 30 pojęć, 6 infografik).
- **Newsletter:** popup z obowiązkową zgodą RODO (po 35 s, po przewinięciu 55% artykułu lub gdy ktoś chce opuścić stronę; zamknięty wraca po 21 dniach).
- **Formularze:** najpierw PHP (`api/`), zapasowo FormSubmit na kontakt@kompetition.cc, na końcu mailto.

### Sklep z planami (`/plany-treningowe/`)
- **Katalog:**
  - 10 planów: baza tlenowa, poprawa FTP, poprawa VO2max, podjazdy i góry, maraton MTB, wyścig szosowy / Gran Fondo, gravel i ultra, jazda na czas i triathlon, trenażer – zima, powrót do formy,
  - długości 4, 8 i 12 tygodni po 250 zł za każde 4 tygodnie (250 / 500 / 750 zł),
  - warianty godzinowe 4–6, 6–8, 8–10, 10–12 h,
  - protokół heat: 5 tygodni, 350 zł.
- **Ankieta dopasowania:** widoczna od razu po wejściu. Drzewko decyzyjne pyta o cel, rodzaj startu, upał, czas do startu, godziny tygodniowo i doświadczenie. Pod przyciskiem „Dopasuj plan dla mnie” jest link do katalogu z filtrami.
- **Okładki:** minimalistyczne, generowane skryptem.
- **Dane sklepu:** `content/shop.json`. Logika ankiety i płatności: `assets/js/shop.js`.
- **Płatności:** linki Stripe Payment Links w `assets/js/config.js` → `paymentLinks["<plan>-<tygodnie>"]`. Wybrany wariant godzinowy jest przekazywany w `client_reference_id`. Dopóki linków nie ma, przycisk „Kup” prowadzi do formularza kontaktowego.
- **Strona po zakupie:** `/dziekuje/`.

### Panel `/admin` (PHP, uruchamiany lokalnie)
- `npm install && npm run panel` → http://localhost:8766/admin/ (PHP 8.3 przez WebAssembly, bez instalowania PHP).
- **Funkcje:**
  - wpisy na blogu z edytorem TinyMCE, szkicami, okładkami i automatycznymi grafikami OG,
  - wizualna edycja stron (klikasz tekst na podglądzie),
  - ustawienia: e-mail, Google Analytics 4, linki Stripe dla każdego wariantu,
  - kopie zapasowe z przywracaniem.
- **Automatyczna publikacja:** po każdym zapisie panel robi `git commit` i `git push`, a Cloudflare Pages wdraża stronę.
- **Hasło panelu:** ustawione przez Jakuba, zapisane w `admin/data/auth.json`. Ten plik nie trafia do repozytorium.

### Narzędzia
- `tools/cf-build.sh` – build dla Cloudflare Pages (output: `dist/`, bez `admin/`, `api/` i `content/`).
- `tools/stripe-setup.mjs` – tworzy w Stripe 31 produktów z cenami i linkami płatności, a linki zapisuje na stronie. Przyjmuje klucze `sk_…` i ograniczone `rk_…`.

## Status – do zrobienia

1. **GitHub:** zmiany z tego folderu **nie zostały jeszcze wypchnięte** (commit `f940cf1` i nowsze). Push wymaga tokenu GitHub z uprawnieniem Contents: Read and write do `strona-internetowa`:
   ```bash
   cd ŚCIEŻKA/kompetition-site && printf "protocol=https\nhost=github.com\nusername=kompetitioncc\npassword=WKLEJ_TOKEN\n" | git credential-osxkeychain store && git push -u origin main
   ```
2. **Stripe:** produkty jeszcze **nie istnieją**. Dwie drogi:
   - konektor Stripe w Claude (Connect → logowanie), wtedy Claude tworzy produkty sam,
   - skrypt uruchomiony w Terminalu (klucz wklejasz dopiero, gdy skrypt o niego poprosi):
     ```bash
     read -s "STRIPE_SECRET_KEY?Klucz Stripe: " && export STRIPE_SECRET_KEY && node tools/stripe-setup.mjs; unset STRIPE_SECRET_KEY
     ```
   W Stripe włącz BLIK i Przelewy24 (Settings → Payment methods).
3. **Bezpieczeństwo:** token GitHub i klucz Stripe `rk_live_…` wklejone w czacie traktuj jako ujawnione. **Unieważnij je** i utwórz nowe.
4. **Cloudflare Pages:** podłącz repozytorium (build command: `bash tools/cf-build.sh`, output: `dist`), potem przenieś DNS domeny (rejestracja zostaje w Squarespace) i **sprawdź rekordy MX poczty**. Kroki są w README.
5. **FormSubmit:** po pierwszej wiadomości z formularza kliknij link aktywacyjny w mailu.
6. **Prawnik:** przegląd §12 regulaminu i polityki prywatności. Trzeba dopisać dane firmy (NIP, adres) i ustalić, który e-mail ma być w RODO (w klauzuli jest obitko.cc@gmail.com).

## Sugestie na później
- Webhook Stripe w Cloudflare Worker, żeby klient po zakupie automatycznie dostawał maila z formularzem startowym.
- MailerLite lub Brevo zamiast FormSubmit dla newslettera, lead magnet PDF w popupie.
- Opinie klientów na stronach planów, pakiety (plan + heat), kody rabatowe dla klubów.
- Google Search Console po przepięciu domeny.
