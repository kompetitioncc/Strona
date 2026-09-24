# KOMpetition.cc – strona, sklep z planami i panel

**Szybki start**
- Strona: statyczny HTML/CSS/JS hostowany na **Cloudflare Pages**, który publikuje z repozytorium GitHub `kompetitioncc/strona-internetowa`.
- Panel `/admin` uruchamiasz lokalnie na Macu poleceniem `npm run panel`. Każdy zapis w panelu sam trafia na GitHub, a Cloudflare publikuje go w ok. 1 minutę.
- Płatności obsługują linki Stripe (Payment Links), więc nie potrzeba serwera.
- Formularze wysyła FormSubmit na kontakt@kompetition.cc. Przy pierwszej wiadomości trzeba kliknąć link aktywacyjny.

## 1. GitHub → Cloudflare Pages (jednorazowo)

1. Cloudflare → **Workers & Pages** → Create → **Pages** → Connect to Git → wybierz repozytorium `strona-internetowa`.
2. Ustawienia budowania:
   - **Framework preset:** None
   - **Build command:** `bash tools/cf-build.sh`
   - **Build output directory:** `dist`
3. Deploy. Strona pojawi się pod adresem `strona-internetowa.pages.dev`. Sprawdź ją przed podpięciem domeny.

## 2. Domena kompetition.cc (zarejestrowana w Squarespace)

Najpewniej zadziała przeniesienie DNS domeny do Cloudflare. Rejestracja domeny zostaje w Squarespace, a strona i DNS będą w Cloudflare.

1. Cloudflare → **Add a site** → `kompetition.cc` → plan Free. Cloudflare zaimportuje obecne rekordy DNS.
2. **Sprawdź, czy zaimportowały się rekordy poczty** (MX, TXT/SPF, DKIM, np. Google Workspace). Bez nich przestanie działać e-mail. Porównaj je z listą w Squarespace → Domains → DNS.
3. W Squarespace → Domains → kompetition.cc → **Nameservers** → Use custom nameservers → wpisz dwa serwery podane przez Cloudflare.
4. Po aktywacji (od kilku minut do 24 h): Cloudflare Pages → projekt → **Custom domains** → dodaj `kompetition.cc` i `www.kompetition.cc`. Cloudflare sam ustawi rekordy i certyfikat SSL.
5. Dopiero gdy nowa strona działa pod domeną, anuluj plan strony w Squarespace. **Nie anuluj domeny.**

## 3. Panel `/admin` – lokalnie, z automatyczną publikacją

Wymagania: Node.js 20+ i Git z dostępem do repozytorium.

```bash
npm install
npm run panel
```

- Otwórz `http://localhost:8766/admin/`.
- Po każdym zapisie wpisu, strony albo ustawień panel robi `git commit` i `git push`. Status widać na pulpicie panelu, jest też przycisk „Opublikuj teraz”.
- Panel działa lokalnie, bo Cloudflare Pages nie uruchamia PHP. Na stronie publicznej panelu nie ma (`tools/cf-build.sh` go pomija).
- Hasło panelu i próby logowania są w `admin/data/`. Ten katalog nie trafia do repozytorium.

**Dostęp do GitHuba (jednorazowo).** Push działa bez pytania o hasło, jeśli Git ma zapisane dane logowania. Najprościej:
- zainstalować **GitHub Desktop**, zalogować się i sklonować tym repozytorium albo
- utworzyć token (GitHub → Settings → Developer settings → Fine-grained token, uprawnienie *Contents: Read and write* do repozytorium) i przy pierwszym `git push` w Terminalu wpisać go zamiast hasła. macOS zapamięta go w pęku kluczy.

## 4. Płatności Stripe

1. Załóż konto Stripe, uzupełnij dane firmy i włącz **BLIK** i **Przelewy24** (Settings → Payment methods).
2. Stripe → Developers → API keys → skopiuj **Secret key**. Najpierw testowy (`sk_test_…`).
3. W folderze strony uruchom:
   ```bash
   STRIPE_SECRET_KEY=sk_test_... node tools/stripe-setup.mjs --dry-run
   STRIPE_SECRET_KEY=sk_test_... node tools/stripe-setup.mjs
   ```
   Skrypt tworzy 31 produktów z cenami (10 planów × 4/8/12 tygodni + protokół heat). Do tego linki płatności z:
   - przekierowaniem na `/dziekuje/`,
   - polem „Dostępny czas tygodniowo” i polem na e-mail konta Intervals.icu / TrainingPeaks,
   - fakturą.

   Linki same trafiają do `assets/js/config.js`. Wariant godzinowy wybrany na stronie przychodzi w polu `client_reference_id` (np. `poprawa-ftp-8w-6-8h`).
4. Przetestuj zakup kartą testową `4242 4242 4242 4242`, potem powtórz krok 3 z kluczem `sk_live_…`. Użyj opcji `--force`, jeśli chcesz nadpisać linki testowe.
5. Opcja `--tos` wymusza zgodę na regulamin w kasie. Najpierw ustaw adres regulaminu w Stripe → Settings → Public details.
6. Linki możesz też wkleić ręcznie w panelu: Ustawienia → Linki płatności Stripe.

**Realizacja zamówień.** Stripe wysyła Ci e-mail o każdej płatności, z wariantem i danymi z formularza. Plan wgrywasz do kalendarza klienta w Intervals.icu / TrainingPeaks w ciągu 48 h.

## Struktura

| Ścieżka | Co to jest |
|---|---|
| `index.html` | Strona główna |
| `opieka-trenerska/`, `o-mnie/`, `kontakt/`, `regulamin/` | Podstrony |
| `plany-treningowe/` (+ `poprawa-ftp/`, `poprawa-vo2max/`) | Dawny sklep (`/store`) |
| `blog/<wpis>/` | 5 artykułów |
| `cp-kalkulator/` (+ `kalkulator.html`) | Kalkulator CP, W', VO2max w oryginalnej wersji |
| `kalkulator-ge/` | Kalkulator Gross Efficiency |
| `assets/css/style.css` | Źródło stylów — przy budowaniu są wklejane do każdej strony (edytujesz tu, potem wklej do `<style>` lub poproś o przebudowę) |
| `assets/og/` | Grafiki 1200×630 do udostępnień (Facebook, Messenger, LinkedIn) |
| `blog/feed.xml`, `site.webmanifest` | Kanał RSS bloga, manifest aplikacji |
| `assets/js/config.js` | **Jedyny plik do konfiguracji**: adresy formularzy i linki płatności |
| `api/kontakt.php`, `api/newsletter.php` | Obsługa formularzy (wymaga PHP) |
| `.htaccess` | Przekierowania 301 ze starych adresów, HTTPS, cache, kompresja |
| `_redirects` | To samo dla Netlify / Cloudflare Pages |
| `sitemap.xml`, `robots.txt`, `404.html` | SEO |

## Przeprowadzka krok po kroku

1. **Hosting z PHP** (np. cyber_Folks, home.pl, LH.pl, nazwa.pl). Wgraj wszystkie pliki, łącznie z ukrytymi `.htaccess`.
2. **Skrzynka `kontakt@kompetition.cc`**: jeśli poczta działała przez Google Workspace, zostaw rekordy MX bez zmian. Zmieniasz tylko rekordy A/CNAME strony.
3. **SSL**: włącz darmowy certyfikat Let's Encrypt w panelu hostingu, zanim przełączysz DNS.
4. **Formularze**: w plikach `api/*.php` sprawdź stałą `FROM`. Musi to być adres w Twojej domenie. Wyślij testową wiadomość.
5. **Płatności za plany**: w `assets/js/config.js` wklej linki płatności (np. Stripe Payment Links, Przelewy24). Dopóki są puste, przycisk „Kup plan” otwiera formularz kontaktowy z nazwą planu.
6. **DNS**: przełącz rekordy A i `www` na nowy serwer. Dopiero potem anuluj Squarespace.
7. **Google Search Console**: zgłoś `https://kompetition.cc/sitemap.xml` i sprawdź kilka starych adresów (`/store`, `/home`) w narzędziu „Sprawdzanie adresu URL”.

## Hosting bez PHP (Netlify, Cloudflare Pages, GitHub Pages)

W `assets/js/config.js` ustaw `contactEndpoint` i `newsletterEndpoint` na adres z Formspree lub Web3Forms. Przekierowania bierze wtedy plik `_redirects` zamiast `.htaccess`.

## Edycja treści

Każda strona to zwykły plik `index.html` w swoim folderze. Tekst edytujesz w dowolnym edytorze. Przy nowym wpisie na blogu:
- skopiuj folder istniejącego artykułu,
- zmień treść, `<title>`, `description`, `canonical` i JSON-LD,
- dodaj kartę wpisu w `blog/index.html` i adres w `sitemap.xml`.

## Statystyki odwiedzin (Google Analytics 4)

1. Załóż usługę GA4 na analytics.google.com i skopiuj identyfikator `G-…`.
2. Wklej go w `assets/js/config.js` jako `ga4Id`.
3. Strona sama pokaże baner zgody. Analityka ładuje się dopiero po kliknięciu „Akceptuję”.
4. Dopisz do klauzuli RODO w `regulamin/index.html` zdanie o Google Analytics i plikach cookie.

## Panel administracyjny `/admin`

Ukryty panel do dodawania wpisów i szybkiej edycji treści. Nie ma do niego linków na stronie, a wyszukiwarki dostają nagłówek `noindex`.

**Pierwsze logowanie:** wejdź na `https://kompetition.cc/admin/` i zaloguj się hasłem startowym (dostałeś je w rozmowie). Panel od razu poprosi o ustawienie własnego hasła (min. 10 znaków).

**Wymagania:**
- PHP 8.0 lub nowsze, z biblioteką GD (z obsługą WebP) i rozszerzeniem DOM – standard u polskich hostingów. FreeType nie jest potrzebny – tytuły na grafikach OG składane są z gotowego atlasu liter.
- Serwer Apache (albo LiteSpeed), bo pliki `.htaccess` blokują dostęp do `admin/data`, `admin/templates` i `content/`. Na nginx trzeba te katalogi zablokować w konfiguracji serwera.
- Stan serwera widać na pulpicie panelu. Czerwone pozycje zgłoś hostingowi.

**Co potrafi panel:**
- **Blog:**
  - nowe wpisy w edytorze wizualnym, z nagłówkami, listami, tabelami, zdjęciami, filmami, przyciskiem CTA i sekcją „Źródła”,
  - szkice z podglądem,
  - seria „KOMpedium wiedzy”.
- **Obrazy:** zdjęcia i okładki są automatycznie zmniejszane do WebP w kilku rozmiarach. Do każdego wpisu powstaje grafika OG 1200×630 z tytułem.
- **Automatyczne odświeżanie:** po zapisaniu wpisu przebudowują się lista bloga, sekcja „najnowsze” na stronie głównej, powiązane artykuły, RSS i `sitemap.xml`.
- **Strony:** edycja tekstów bezpośrednio na podglądzie strony, podmiana zdjęć kliknięciem, zmiana linków dwuklikiem. Tytuł i opis w Google edytujesz z licznikiem znaków. Jest też tryb HTML dla zaawansowanych.
- **Ustawienia:**
  - hasło,
  - e-mail do formularzy,
  - zapasowa wysyłka przez FormSubmit,
  - Google Analytics 4,
  - linki płatności za plany (generują `assets/js/config.js`),
  - pobieranie listy newslettera (CSV).
- **Kopie zapasowe:** przed każdą zmianą zapisuje się poprzednia wersja pliku (20 ostatnich), a przywracasz ją jednym kliknięciem.
- **Bezpieczeństwo:** hasło hashowane bcryptem, blokada po 5 błędnych próbach na 15 minut, tokeny CSRF, bezpieczne ciasteczko sesji. Z treści usuwane są skrypty.

**Wskazówki:**
- Nazwę katalogu `admin` możesz zmienić (np. na `panel-kuby`), żeby był trudniejszy do znalezienia. Wszystkie linki w panelu są względne.
- Zmiana ceny w tekście strony nie zmienia jej w danych strukturalnych (JSON-LD). Przy zmianie cennika poproś o aktualizację.

## Formularze – jak trafiają wiadomości na kontakt@kompetition.cc

1. **Główna droga:** `api/kontakt.php` wysyła e-mail funkcją PHP `mail()` bezpośrednio na kontakt@kompetition.cc. Stała `FROM` w pliku musi być adresem w Twojej domenie.
2. **Droga zapasowa:** gdy PHP nie odpowie (hosting bez PHP, awaria), formularz wysyła wiadomość przez [FormSubmit](https://formsubmit.co) na ten sam adres.
   - Przy pierwszej takiej wiadomości FormSubmit przyśle maila z prośbą o aktywację. Kliknij link.
   - FormSubmit przetwarza wtedy dane z formularza, więc warto dopisać go w klauzuli RODO.
   - Wyłączysz go w panelu: Ustawienia → „Zapasowa wysyłka”.
3. **Ostatnia deska ratunku:** jeśli obie drogi zawiodą, otworzy się program pocztowy z gotową wiadomością do kontakt@kompetition.cc.
