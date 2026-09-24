Kontynuujemy pracę nad nową stroną kompetition.cc (trener kolarstwa Jakub Obitko). Pracuj w folderze `kompetition-site` (rozpakowany z kompetition-site.zip; to repozytorium git z remote https://github.com/kompetitioncc/strona-internetowa.git, gałąź main).

Najpierw przeczytaj PODSUMOWANIE-SESJI.md i README.md w tym folderze – jest tam pełny opis strony, sklepu z planami, panelu /admin i listy rzeczy do zrobienia.

Kontekst techniczny:
- Strona to statyczny HTML/CSS/JS, docelowo na Cloudflare Pages (build: `bash tools/cf-build.sh`, output: `dist`), domena zarejestrowana w Squarespace.
- Panel /admin (PHP) uruchamiany lokalnie przez `npm install && npm run panel` → http://localhost:8766/admin/, po zapisie robi automatyczny git commit + push.
- Sklep: 10 planów × 4/8/12 tygodni (250 zł za każde 4 tygodnie) + protokół heat 5 tyg. / 350 zł, dane w content/shop.json, płatności przez Stripe Payment Links w assets/js/config.js (paymentLinks["<plan>-<tygodnie>"]).
- tools/stripe-setup.mjs tworzy produkty, ceny i linki płatności w Stripe.

Zadania na teraz, po kolei:
1. Sprawdź stan repozytorium (`git status`, `git log`) i pomóż mi wypchnąć je na GitHub (sam wkleję token w Terminalu – nie proś mnie o wklejanie tokenów ani kluczy w czacie).
2. Utwórz warianty produktów w Stripe: jeśli masz podłączony konektor Stripe – zrób to przez niego (31 produktów/cen/linków płatności w PLN, przekierowanie na https://kompetition.cc/dziekuje/?plan=<slug>&w=<tygodnie>, pole wyboru godzin tygodniowo, faktura), a linki zapisz w content/settings.json i assets/js/config.js; jeśli nie – uruchom w Terminalu tools/stripe-setup.mjs tak, żebym to ja wkleił klucz.
3. Pomóż podłączyć Cloudflare Pages i przenieść DNS domeny ze Squarespace bez utraty poczty (rekordy MX).

Pisz do mnie po polsku.
