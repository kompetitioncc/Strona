#!/usr/bin/env python3
"""Generuje szablony maili KOMpetition (Brevo) do kompetition-site/newsletter/."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
SITE = "https://kompetition.cc"
IMG = SITE + "/assets"
UTM = "utm_source=newsletter&utm_medium=email&utm_campaign="

INK, SAND, LINE, MUTED, SUN = "#0b0b0c", "#f4f2ec", "#e4e1d8", "#5b5b60", "#ffd500"
DISPLAY = "'Barlow Condensed','Arial Narrow',Arial,sans-serif"
TEXT = "Roboto,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

GREETING = '{% if contact.FIRSTNAME %}Cześć {{ contact.FIRSTNAME }}!{% else %}Cześć!{% endif %}'


def u(path, campaign):
    sep = "&" if "?" in path else "?"
    return f"{SITE}{path}{sep}{UTM}{campaign}"


def page(title, preheader, body, campaign):
    return f"""<!DOCTYPE html>
<html lang="pl" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>{title}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<!--[if !mso]><!-->
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<!--<![endif]-->
<style>
  body{{margin:0;padding:0;width:100%!important;background:{SAND};-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}}
  table{{border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0}}
  img{{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;display:block;height:auto}}
  a{{color:{INK}}}
  a[x-apple-data-detectors]{{color:inherit!important;text-decoration:none!important}}
  .btn a:hover{{background:{INK}!important;color:#ffffff!important}}
  @media (max-width:620px){{
    .container{{width:100%!important}}
    .px{{padding-left:22px!important;padding-right:22px!important}}
    .h1{{font-size:38px!important;line-height:38px!important}}
    .stack{{display:block!important;width:100%!important;padding-left:0!important;padding-right:0!important}}
    .stack-pad{{padding:0 0 16px 0!important}}
    .img-full{{max-width:100%!important}}
  }}
  @media (prefers-color-scheme:dark){{
    body,.bg-sand{{background:#141416!important}}
    .card{{background:#1d1d20!important}}
    .t-ink,.t-ink a,h1,h2,h3{{color:#f3f3f3!important}}
    .t-muted{{color:#a9a9ae!important}}
    .box{{background:#26262a!important;border-color:#3a3a3f!important}}
    .line{{border-color:#2a2a2d!important}}
  }}
  [data-ogsc] .card{{background:#1d1d20!important}}
  [data-ogsc] .t-ink,[data-ogsc] h1,[data-ogsc] h2{{color:#f3f3f3!important}}
</style>
</head>
<body class="bg-sand" style="margin:0;padding:0;background:{SAND};">
<!-- PREHEADER: tekst widoczny w skrzynce obok tematu -->
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:{SAND};">{preheader}&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="bg-sand" style="background:{SAND};">
<tr><td align="center" style="padding:24px 12px;">

<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">

  <!-- link „wyświetl w przeglądarce” -->
  <tr><td align="right" style="padding:0 4px 10px;font:12px/16px {TEXT};color:{MUTED};" class="t-muted">
    <a href="{{{{ mirror }}}}" style="color:{MUTED};">Wyświetl w przeglądarce</a>
  </td></tr>

  <!-- NAGŁÓWEK -->
  <tr><td align="center" bgcolor="{INK}" style="background:{INK};padding:28px 24px 24px;border-radius:18px 18px 0 0;">
    <a href="{u('/', campaign)}" target="_blank"><img src="{IMG}/email/logo-white.png" width="150" alt="KOMpetition.cc" style="width:150px;max-width:150px;color:#ffffff;font:800 22px {DISPLAY};"></a>
  </td></tr>
  <tr><td height="4" bgcolor="{SUN}" style="background:{SUN};font-size:0;line-height:0;">&nbsp;</td></tr>

  <!-- TREŚĆ -->
  <tr><td class="card" bgcolor="#ffffff" style="background:#ffffff;border-radius:0 0 18px 18px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{body}
    </table>
  </td></tr>

  <!-- STOPKA -->
  <tr><td class="px t-muted" align="center" style="padding:28px 40px 8px;font:13px/20px {TEXT};color:{MUTED};">
    <a href="https://www.instagram.com/kompetition.cc/" style="color:{INK};font-weight:700;text-decoration:none;" class="t-ink">Instagram</a>
    &nbsp;·&nbsp;
    <a href="{u('/blog/', campaign)}" style="color:{INK};font-weight:700;text-decoration:none;" class="t-ink">Blog</a>
    &nbsp;·&nbsp;
    <a href="{u('/plany-treningowe/', campaign)}" style="color:{INK};font-weight:700;text-decoration:none;" class="t-ink">Plany treningowe</a>
  </td></tr>
  <tr><td class="px t-muted" align="center" style="padding:8px 40px 32px;font:12px/18px {TEXT};color:{MUTED};">
    Dostajesz ten mail, bo zapisałeś/aś się na newsletter KOMpetition.cc.<br>
    <a href="{{{{ unsubscribe }}}}" style="color:{MUTED};">Wypisz się</a>
    &nbsp;·&nbsp;
    <a href="{{{{ update_profile }}}}" style="color:{MUTED};">Zmień dane</a>
    &nbsp;·&nbsp;
    <a href="{u('/polityka-prywatnosci/', campaign)}" style="color:{MUTED};">Polityka prywatności</a><br>
    KOMpetition.cc · Jakub Obitko · ul. Hoffmanowej 6b/10, 30-419 Kraków · <a href="mailto:kontakt@kompetition.cc" style="color:{MUTED};">kontakt@kompetition.cc</a>
  </td></tr>

</table>
<!--[if mso]></td></tr></table><![endif]-->

</td></tr>
</table>
</body>
</html>
"""


# ---------- klocki ----------
def eyebrow(t):
    return f'''    <tr><td class="px" style="padding:36px 40px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="28" valign="middle" style="width:28px;"><div style="width:28px;height:3px;background:{SUN};font-size:0;line-height:0;">&nbsp;</div></td>
        <td class="t-muted" style="padding-left:10px;font:600 14px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{MUTED};">{t}</td>
      </tr></table>
    </td></tr>'''


def h1(t):
    return f'''    <tr><td class="px" style="padding:14px 40px 0;">
      <h1 class="h1 t-ink" style="margin:0;font:800 46px/44px {DISPLAY};text-transform:uppercase;color:{INK};mso-line-height-rule:exactly;">{t}</h1>
    </td></tr>'''


def h2(t, top=28):
    return f'''    <tr><td class="px" style="padding:{top}px 40px 0;">
      <h2 class="t-ink" style="margin:0;font:800 28px/28px {DISPLAY};text-transform:uppercase;color:{INK};mso-line-height-rule:exactly;">{t}</h2>
    </td></tr>'''


def p(html, top=16):
    return f'''    <tr><td class="px t-ink" style="padding:{top}px 40px 0;font:16px/26px {TEXT};color:{INK};">
      {html}
    </td></tr>'''


def ul(items):
    lis = "".join(
        f'''
        <tr><td valign="top" width="22" style="padding:6px 0;font:800 18px/24px {DISPLAY};color:{SUN};">■</td>
            <td class="t-ink" style="padding:6px 0;font:16px/24px {TEXT};color:{INK};">{i}</td></tr>'''
        for i in items)
    return f'''    <tr><td class="px" style="padding:14px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{lis}
      </table>
    </td></tr>'''


def button(text, href, top=26, ghost=False):
    bg, fg, bd = (("#ffffff", INK, INK) if ghost else (SUN, INK, SUN))
    return f'''    <tr><td class="px" style="padding:{top}px 40px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td class="btn" align="center" bgcolor="{bg}" style="border-radius:999px;background:{bg};">
          <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" style="height:50px;v-text-anchor:middle;width:280px;" arcsize="50%" stroke="t" strokecolor="{bd}" fillcolor="{bg}"><w:anchorlock/><center style="color:{fg};font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{text}</center></v:roundrect><![endif]-->
          <!--[if !mso]><!--><a href="{href}" target="_blank" style="display:inline-block;padding:15px 30px;border:2px solid {bd};border-radius:999px;background:{bg};color:{fg};font:700 16px/18px {TEXT};text-decoration:none;">{text} &rarr;</a><!--<![endif]-->
        </td>
      </tr></table>
    </td></tr>'''


def image(src, alt, href=None, top=28, radius=12):
    img = f'<img src="{src}" width="520" alt="{alt}" style="width:100%;max-width:520px;border-radius:{radius}px;">'
    if href:
        img = f'<a href="{href}" target="_blank">{img}</a>'
    return f'''    <tr><td class="px" style="padding:{top}px 40px 0;">
      {img}
    </td></tr>'''


def code_box(code, text, until):
    return f'''    <tr><td class="px" style="padding:26px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="box" style="background:{SAND};border:2px dashed {INK};border-radius:14px;">
        <tr><td align="center" style="padding:22px 20px;">
          <div class="t-muted" style="font:600 13px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{MUTED};">{text}</div>
          <div class="t-ink" style="padding:8px 0 6px;font:800 40px/40px {DISPLAY};letter-spacing:3px;color:{INK};">{code}</div>
          <div class="t-muted" style="font:13px/18px {TEXT};color:{MUTED};">{until}</div>
        </td></tr>
      </table>
    </td></tr>'''


def signature():
    return f'''    <tr><td class="px" style="padding:30px 40px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="56" valign="middle"><img src="{IMG}/email/jakub-avatar.jpg" width="56" height="56" alt="Jakub Obitko" style="width:56px;height:56px;border-radius:50%;"></td>
        <td valign="middle" class="t-ink" style="padding-left:14px;font:15px/21px {TEXT};color:{INK};">
          <strong>Kuba Obitko</strong><br>
          <span class="t-muted" style="color:{MUTED};">trener kolarstwa · KOMpetition.cc</span>
        </td>
      </tr></table>
    </td></tr>'''


def divider(top=32):
    return f'''    <tr><td class="px" style="padding:{top}px 40px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td class="line" style="border-top:1px solid {LINE};font-size:0;line-height:0;">&nbsp;</td></tr></table></td></tr>'''


def end(bottom=40):
    return f'    <tr><td style="padding-bottom:{bottom}px;font-size:0;line-height:0;">&nbsp;</td></tr>'


def article_row(img, title, desc, href):
    """Artykuł: obrazek po lewej, tekst po prawej (na telefonie jeden pod drugim)."""
    return f'''    <tr><td class="px" style="padding:22px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td class="stack stack-pad" width="200" valign="top" style="width:200px;padding-right:20px;">
          <a href="{href}" target="_blank"><img src="{img}" width="200" alt="{title}" class="img-full" style="width:100%;max-width:200px;border-radius:10px;"></a>
        </td>
        <td class="stack" valign="top">
          <a href="{href}" target="_blank" class="t-ink" style="font:800 22px/23px {DISPLAY};text-transform:uppercase;color:{INK};text-decoration:none;">{title}</a>
          <div class="t-ink" style="padding-top:6px;font:15px/23px {TEXT};color:{INK};">{desc}</div>
          <div style="padding-top:8px;"><a href="{href}" target="_blank" class="t-ink" style="font:700 14px/18px {TEXT};color:{INK};text-decoration:none;border-bottom:2px solid {SUN};">Czytaj &rarr;</a></div>
        </td>
      </tr></table>
    </td></tr>'''


def dark_band(title, text, btn_text, href):
    return f'''    <tr><td class="px" style="padding:32px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{INK}" style="background:{INK};border-radius:14px;">
        <tr><td style="padding:26px 26px 8px;font:800 26px/27px {DISPLAY};text-transform:uppercase;color:#ffffff;">{title}</td></tr>
        <tr><td style="padding:0 26px;font:15px/23px {TEXT};color:#d9d9dc;">{text}</td></tr>
        <tr><td style="padding:18px 26px 26px;">
          <a href="{href}" target="_blank" style="display:inline-block;padding:13px 26px;border-radius:999px;background:{SUN};color:{INK};font:700 15px/18px {TEXT};text-decoration:none;">{btn_text} &rarr;</a>
        </td></tr>
      </table>
    </td></tr>'''


# ---------- 1. POWITANIE ----------
c = "powitanie"
body = "\n".join([
    eyebrow("Witaj w KOMpetition"),
    h1("Dobrze, że jesteś"),
    p(f"<strong>{GREETING}</strong>", 20),
    p("Dzięki za zapis. Jestem Kuba i prowadzę KOMpetition: trenuję kolarzy szosowych, gravelowych i MTB, a na blogu rozkładam na czynniki pierwsze to, co naprawdę działa w treningu."),
    p("Co będziesz ode mnie dostawać, maksymalnie kilka razy w miesiącu:"),
    ul([
        "<strong>Wiedzę bez lania wody</strong>: badania, protokoły i liczby, które przekładasz na trening.",
        "<strong>Nowości z KOMpetition</strong>: nowe plany, artykuły i narzędzia (jak kalkulator CP).",
        "<strong>Rabaty tylko dla subskrybentów</strong>: pierwszy masz już poniżej.",
    ]),
    code_box("WITAJ10", "Twój kod: −10% na pierwszy plan", "Wpisz go przy płatności · ważny 14 dni"),
    button("Wybierz plan treningowy", u("/plany-treningowe/", c)),
    divider(),
    h2("Od czego zacząć?"),
    p(f'Najlepiej od <a href="{u("/blog/kompedium-slownik-treningowy/", c)}" style="color:{INK};font-weight:700;">KOMpedium</a>, czyli słownika treningowego: FTP, CP, W\', strefy, makrocykle. Wszystko w jednym miejscu.'),
    p("Masz pytanie albo chcesz opowiedzieć o swoim celu na sezon? <strong>Po prostu odpisz na tego maila</strong>. Czytam wszystkie odpowiedzi."),
    signature(),
    end(),
])
(OUT / "01-powitanie.html").write_text(page("Witaj w KOMpetition", "Dzięki za zapis! W środku kod −10% na pierwszy plan treningowy.", body, c))

# ---------- 2. WIEDZA / CIEKAWOSTKA ----------
c = "wiedza"
body = "\n".join([
    eyebrow("KOMpedium · Ciekawostka"),
    h1("Heat training: 5 dni, które robią różnicę"),
    image(f"{IMG}/og/blog-heat-training-kompedium.jpg", "Heat training w kolarstwie", u("/blog/heat-training-kompedium/", c)),
    p(f"<strong>{GREETING}</strong>", 24),
    p("Trening w cieple to jedna z niewielu legalnych metod, która w kilka tygodni podnosi objętość osocza, obniża tętno przy tej samej mocy i poprawia tolerancję wysiłku, i to nie tylko w upale."),
    h2("3 rzeczy, które warto wiedzieć", 26),
    ul([
        "<strong>Adaptacja zaczyna się szybko</strong>: pierwsze zmiany widać już po 5–7 sesjach.",
        "<strong>Liczy się temperatura głęboka</strong>, a nie to, jak bardzo się pocisz. Czujnik CORE pokazuje, czy bodziec był wystarczający.",
        "<strong>Efekt trzeba podtrzymać</strong>: bez sesji przypominających adaptacje stopniowo zanikają w ciągu kilku tygodni.",
    ]),
    p("W artykule znajdziesz, co mówią badania, jak mierzyć obciążenie cieplne i 5 gotowych protokołów: od 5-dniowego blitzu po 5-tygodniowy blok."),
    button("Czytaj cały artykuł", u("/blog/heat-training-kompedium/", c)),
    dark_band("Chcesz to zrobić z planem?",
              "Protokół Heat to 5 tygodni rozpisanych jednostek z kontrolą temperatury głębokiej. Z kodem <strong style=\"color:#ffd500;\">WITAJ10</strong> taniej o 10%.",
              "Zobacz Protokół Heat", u("/plany-treningowe/protokol-heat/", c)),
    signature(),
    end(),
])
(OUT / "02-wiedza-ciekawostka.html").write_text(page("Heat training: 5 dni, które robią różnicę", "Jedna z niewielu legalnych metod, która działa w kilka tygodni.", body, c))

# ---------- 3. PROMOCJA PLANU ----------
c = "promocja"
body = "\n".join([
    eyebrow("Plan treningowy · Oferta"),
    h1("Rusz swoje FTP z miejsca"),
    image(f"{IMG}/email/plan-poprawa-ftp.jpg", "Plan treningowy: Poprawa FTP", u("/plany-treningowe/poprawa-ftp/", c)),
    p(f"<strong>{GREETING}</strong>", 24),
    p("Jeśli od miesięcy widzisz tę samą wartość FTP, problem zwykle nie leży w braku chęci, tylko w strukturze treningu. Plan <strong>Poprawa FTP</strong> jest dla kolarzy, którzy chcą to zmienić."),
    ul([
        "<strong>8 lub 12 tygodni</strong> rozpisanych jednostek, od 4 do 12 h tygodniowo",
        "<strong>Treningi w intervals.icu</strong>: synchronizują się z Garminem, Wahoo i Zwiftem",
        "<strong>Waty, kadencja i węglowodany</strong> opisane przy każdej jednostce",
        "<strong>Test na starcie i na końcu</strong>: progres widać w liczbach",
    ]),
    # cennik
    f'''    <tr><td class="px" style="padding:26px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td class="stack stack-pad" width="50%" valign="top" style="padding-right:8px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="box" style="background:{SAND};border:1px solid {LINE};border-radius:14px;">
            <tr><td align="center" style="padding:20px 14px;">
              <div class="t-muted" style="font:600 14px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{MUTED};">8 tygodni</div>
              <div class="t-ink" style="padding:6px 0 12px;font:800 38px/38px {DISPLAY};color:{INK};">250 zł</div>
              <a href="https://buy.stripe.com/9B6fZi5CmekKash5cW4sE0S" target="_blank" style="display:inline-block;padding:11px 22px;border-radius:999px;background:{SUN};color:{INK};font:700 14px/16px {TEXT};text-decoration:none;">Kupuję 8 tyg. &rarr;</a>
            </td></tr>
          </table>
        </td>
        <td class="stack" width="50%" valign="top" style="padding-left:8px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="box" style="background:{SAND};border:1px solid {LINE};border-radius:14px;">
            <tr><td align="center" style="padding:20px 14px;">
              <div class="t-muted" style="font:600 14px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{MUTED};">12 tygodni</div>
              <div class="t-ink" style="padding:6px 0 12px;font:800 38px/38px {DISPLAY};color:{INK};">400 zł</div>
              <a href="https://buy.stripe.com/28E14o3ue1xYcAp5cW4sE0T" target="_blank" style="display:inline-block;padding:11px 22px;border-radius:999px;background:{SUN};color:{INK};font:700 14px/16px {TEXT};text-decoration:none;">Kupuję 12 tyg. &rarr;</a>
            </td></tr>
          </table>
        </td>
      </tr></table>
    </td></tr>''',
    code_box("WITAJ10", "Kod dla subskrybentów: −10%", "Wpisz go w polu „Dodaj kod promocyjny” przy płatności"),
    button("Zobacz szczegóły planu", u("/plany-treningowe/poprawa-ftp/", c), ghost=True),
    p("Nie wiesz, który plan wybrać? Odpisz na tego maila: napisz, ile masz czasu w tygodniu i jaki masz cel, a podpowiem.", 24),
    signature(),
    end(),
])
(OUT / "03-promocja-planu.html").write_text(page("Rusz swoje FTP z miejsca", "8 lub 12 tygodni, od 250 zł. Z kodem dla subskrybentów taniej o 10%.", body, c))

# ---------- 4. NEWSLETTER ZBIORCZY ----------
c = "newsletter"
body = "\n".join([
    eyebrow("Newsletter · [MIESIĄC ROK]"),
    h1("Co słychać w KOMpetition"),
    p(f"<strong>{GREETING}</strong>", 20),
    p("[Krótkie intro: 2–3 zdania. Co się działo w tym miesiącu: starty, obozy, wyniki podopiecznych, nad czym pracujesz.]"),
    divider(28),
    h2("Nowe na blogu"),
    article_row(f"{IMG}/og/blog-lactate-testing.jpg", "Test laktatowy: LT1, LT2 i strefy",
                "Wyjdź poza test FTP. Jak test laktatowy pomaga wyznaczyć strefy i zaplanować trening.",
                u("/blog/lactate-testing/", c)),
    article_row(f"{IMG}/og/blog-czym-jest-gross-efficiency.jpg", "Gross Efficiency: ukryta rezerwa mocy",
                "Czym jest GE, jak ją obliczyć i jak ją poprawić, żeby z tej samej energii wyciskać więcej watów.",
                u("/blog/czym-jest-gross-efficiency/", c)),
    divider(32),
    h2("Liczba miesiąca"),
    f'''    <tr><td class="px" style="padding:16px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="150" valign="middle" class="stack stack-pad t-ink" style="font:800 64px/60px {DISPLAY};color:{INK};">+23 W</td>
        <td valign="middle" class="stack t-ink" style="font:15px/23px {TEXT};color:{INK};">[Wynik podopiecznego albo ciekawa liczba z badań, np. „tyle zyskał na FTP Marek po 12 tygodniach bazy”. Pamiętaj o zgodzie podopiecznego.]</td>
      </tr></table>
    </td></tr>''',
    divider(32),
    h2("Szybka porada"),
    p("[Jedna praktyczna wskazówka na 3–4 zdania, np. o jedzeniu na długim treningu, rozgrzewce przed startem albo ustawieniu stref.]"),
    dark_band("Chcesz, żebym prowadził Twój trening?",
              "Opieka trenerska: indywidualny plan co tydzień, analiza każdej jednostki i stały kontakt. 499 zł / miesiąc.",
              "Sprawdź opiekę trenerską", u("/opieka-trenerska/", c)),
    signature(),
    end(),
])
(OUT / "04-newsletter-zbiorczy.html").write_text(page("Co słychać w KOMpetition", "[Preheader: jedno zdanie zachęty, widoczne w skrzynce obok tematu]", body, c))

print("OK:", sorted(x.name for x in OUT.glob("*.html")))
