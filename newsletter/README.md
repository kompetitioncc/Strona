# Szablony maili KOMpetition (Brevo)

| Plik | Do czego |
|---|---|
| `01-powitanie.html` | Automatyzacja, mail 1 (od razu po zapisie): powitanie, kod WITAJ10, KOMpedium |
| `02-wiedza-ciekawostka.html` | Automatyzacja, mail 2 (+3 dni); potem wzór pod każdy mail „wiedza” |
| `03-promocja-planu.html` | Automatyzacja, mail 3 (+7 dni); potem wzór pod promocję dowolnego planu |
| `04-newsletter-zbiorczy.html` | Zwykły newsletter co 2–4 tygodnie (teksty w [nawiasach] do podmiany) |

Grafiki są ładowane z `https://kompetition.cc/assets/email/` i `/assets/og/`, więc wyświetlą się dopiero po publikacji nowej strony.
Możesz też wgrać je do biblioteki obrazów w Brevo i podmienić adresy.

## Przed pierwszym wysłaniem
1. Adres w stopce pochodzi z konta Brevo (ul. Hoffmanowej 6b/10, Kraków); zmiana w `generuj-szablony.py`.
2. **Stripe → Produkty → Kupony**: utwórz kupon −10%, a w nim kod promocyjny `WITAJ10`
   (np. limit 1 użycia na klienta, ważność wg uznania). W każdym Payment Linku włącz **„Allow promotion codes”**.
   Jeśli wybierzesz inny kod, zmień `WITAJ10` w szablonach 01–03.
3. Brevo → Contacts → Settings: sprawdź, że atrybut `FIRSTNAME` istnieje (jest domyślnie).

## Wklejanie do Brevo
Campaigns → Templates → **New template** → „Code your own” → wklej całą zawartość pliku → Save.
Temat i preheader ustawiasz w Brevo (preheader jest też w kodzie, pod `<body>`).

Tagi Brevo użyte w szablonach:
- `{{ contact.FIRSTNAME }}` z warunkiem `{% if %}`: „Cześć Marek!” albo samo „Cześć!”, gdy brak imienia
- `{{ unsubscribe }}`: wypisanie (obowiązkowe, jest w stopce)
- `{{ update_profile }}`: zmiana danych
- `{{ mirror }}`: „wyświetl w przeglądarce”

## Automatyzacja powitalna
Automations → Create → „Welcome message”:
1. Wyzwalacz: *Contact added to list* → lista „Newsletter”
2. Send email → szablon **01-powitanie**, temat np. „Witaj w KOMpetition + kod −10%”
3. Wait 3 dni → szablon **02-wiedza-ciekawostka**
4. Wait 4 dni → szablon **03-promocja-planu**, temat np. „Twój kod −10% wygasa za kilka dni”

Formularz zapisu z double opt‑in: Contacts → Forms. Albo podłączymy formularze strony przez API.

## Zmiany wyglądu
Wszystkie 4 pliki powstają ze skryptu `generuj-szablony.py` (kolory, stopka i klocki w jednym miejscu):
```bash
python3 newsletter/generuj-szablony.py
```
Drobne zmiany treści możesz też robić bezpośrednio w Brevo, w edytorze kodu.
