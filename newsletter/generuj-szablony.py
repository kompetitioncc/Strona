#!/usr/bin/env python3
"""Generuje szablony maili KOMpetition (Brevo) do kompetition-site/newsletter/."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
SITE = "https://kompetition.cc"
IMG = SITE + "/assets"
UTM = "utm_source=newsletter&utm_medium=email&utm_campaign="

INK, SAND, LINE, MUTED, SUN, SUN_DEEP = "#0b0b0c", "#f4f2ec", "#e4e1d8", "#5b5b60", "#ffd500", "#c9a800"
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
  <!-- tło jako gradient + logo z wbudowanym czarnym tłem: Gmail w trybie ciemnym nie odwraca ani jednego, ani drugiego -->
  <tr><td align="center" bgcolor="{INK}" style="background-color:{INK};background-image:linear-gradient({INK},{INK});padding:18px 24px 14px;border-radius:18px 18px 0 0;">
    <a href="{u('/', campaign)}" target="_blank"><img src="{IMG}/email/logo-header.png" width="170" alt="KOMpetition.cc" style="width:170px;max-width:170px;background:{INK};color:#ffffff;font:800 22px {DISPLAY};"></a>
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
          <strong>Jakub Obitko</strong><br>
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
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{INK}" style="background-color:{INK};background-image:linear-gradient({INK},{INK});border-radius:14px;">
        <tr><td style="padding:26px 26px 8px;font:800 26px/27px {DISPLAY};text-transform:uppercase;color:#ffffff;">{title}</td></tr>
        <tr><td style="padding:0 26px;font:15px/23px {TEXT};color:#d9d9dc;">{text}</td></tr>
        <tr><td style="padding:18px 26px 26px;">
          <a href="{href}" target="_blank" style="display:inline-block;padding:13px 26px;border-radius:999px;background:{SUN};color:{INK};font:700 15px/18px {TEXT};text-decoration:none;">{btn_text} &rarr;</a>
        </td></tr>
      </table>
    </td></tr>'''


def raw(t):
    """Znacznik szablonu Brevo między wierszami tabeli (Brevo usuwa go przy renderowaniu)."""
    return "    " + t


def plan_card(label="Twój plan z ankiety doboru"):
    """Karta polecanego planu – wypełniana parametrami params.PLAN_* z Workera."""
    return f'''    <tr><td class="px" style="padding:26px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="box" style="background:{SAND};border:1px solid {LINE};border-radius:14px;">
        <tr><td style="padding:0;">
          <a href="{{{{ params.PLAN_URL }}}}" target="_blank"><img src="{{{{ params.PLAN_IMG }}}}" width="520" alt="{{{{ params.PLAN_NAME }}}}" style="width:100%;max-width:520px;border-radius:14px 14px 0 0;"></a>
        </td></tr>
        <tr><td style="padding:22px 24px 0;">
          <div class="t-muted" style="font:600 13px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{MUTED};">{label}</div>
          <div class="t-ink" style="padding-top:6px;font:800 32px/32px {DISPLAY};text-transform:uppercase;color:{INK};">{{{{ params.PLAN_NAME }}}}</div>
          <div class="t-ink" style="padding-top:8px;font:700 15px/22px {TEXT};color:{INK};">{{{{ params.PLAN_VARIANT }}}}</div>
          <div class="t-ink" style="padding-top:10px;font:15px/23px {TEXT};color:{INK};">{{{{ params.PLAN_TAGLINE }}}}</div>
        </td></tr>
        <tr><td style="padding:18px 24px 0;font:15px/22px {TEXT};" class="t-ink">
          <span class="t-muted" style="color:{MUTED};text-decoration:line-through;">{{{{ params.PLAN_PRICE }}}} zł</span>
          &nbsp;<strong style="font:800 30px/30px {DISPLAY};color:{INK};">{{{{ params.PLAN_PRICE_CODE }}}} zł</strong>
          &nbsp;<span class="t-muted" style="color:{MUTED};">z kodem WITAJ10</span>
        </td></tr>
        <tr><td style="padding:18px 24px 24px;">
          <a href="{{{{ params.PLAN_BUY }}}}" target="_blank" style="display:inline-block;padding:14px 26px;border-radius:999px;background:{SUN};color:{INK};font:700 15px/18px {TEXT};text-decoration:none;">Kupuję z rabatem &rarr;</a>
          &nbsp; <a href="{{{{ params.PLAN_URL }}}}" target="_blank" class="t-ink" style="font:700 14px/18px {TEXT};color:{INK};text-decoration:none;border-bottom:2px solid {SUN};">Szczegóły planu</a>
        </td></tr>
      </table>
    </td></tr>'''


# ---------- 1. POWITANIE ----------
c = "powitanie"
body = "\n".join([
    eyebrow("Witaj w KOMpetition"),
    h1("Dobrze, że jesteś"),
    p(f"<strong>{GREETING}</strong>", 20),
    p("Dzięki za zapis. Jestem Jakub i prowadzę KOMpetition: trenuję kolarzy szosowych, gravelowych i MTB, a na blogu rozkładam na czynniki pierwsze to, co naprawdę działa w treningu."),
    raw("{% if params.PLAN_NAME %}"),
    p("Obiecany plan z ankiety doboru jest poniżej. Wybrałem go na podstawie Twojego celu, doświadczenia i czasu, który masz na trening."),
    plan_card(),
    raw("{% endif %}"),
    p("Co będziesz ode mnie dostawać, maksymalnie kilka razy w miesiącu:"),
    ul([
        "<strong>Wiedzę bez lania wody</strong>: badania, protokoły i liczby, które przekładasz na trening.",
        "<strong>Nowości z KOMpetition</strong>: nowe plany, artykuły i narzędzia (jak kalkulator CP).",
        "<strong>Rabaty tylko dla subskrybentów</strong>: pierwszy masz już poniżej.",
    ]),
    code_box("WITAJ10", "Twój kod: −10% na pierwszy plan", "Wpisz go przy płatności · ważny 14 dni"),
    raw("{% if params.PLAN_NAME %}{% else %}"),
    button("Wybierz plan treningowy", u("/plany-treningowe/", c)),
    raw("{% endif %}"),
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


# ---------- 5. NOWY WPIS: ROZTRENOWANIE ----------
c = "roztrenowanie"
body = "\n".join([
    eyebrow("Nowy wpis · Niepopularna opinia"),
    h1("W roztrenowaniu zamiast trenażera – sauna"),
    image(f"{IMG}/email/wpis-roztrenowanie.jpg", "Roztrenowanie w kolarstwie – nowy wpis na blogu KOMpetition", u("/blog/roztrenowanie-kolarstwo/", c)),
    p(f"<strong>{GREETING}</strong>", 24),
    p("Sezon się kończy, a w głowie pojawia się pytanie: ile odpocząć, żeby nie stracić wszystkiego, co wypracowałem? Napisałem o tym duży artykuł – z liczbami z badań i tym, jak roztrenowanie rozpisuję swoim podopiecznym."),
    h2("Niepopularna opinia", 26),
    p("W przerwie od treningu forma ucieka najpierw <strong>przez krew</strong>: po 2–4 tygodniach objętość osocza spada o ok. 12%. Co ciekawe, gdy badani mieli przywróconą objętość krwi, ich VO2max wracało niemal do poziomu sprzed przerwy."),
    p("Dlatego zamiast zmuszać się do trenażera w październiku, polecam <strong>ciepło jako osobną jednostkę</strong>: 2–3 razy w tygodniu 20–30 minut sauny albo gorąca kąpiel – bez dokładania treningu, bo w roztrenowaniu przecież nie trenujesz. W badaniu, w którym biegacze przez 3 tygodnie chodzili do sauny, objętość osocza wzrosła o 7,1%. Zero obciążenia dla nóg i głowy, a „silnik” nie gaśnie."),
    h2("Co jeszcze znajdziesz w artykule", 26),
    ul([
        "<strong>Oś czasu detreningu</strong> – co i kiedy tracisz, gdy odpuszczasz.",
        "<strong>Minimalna dawka treningu</strong> – dlaczego jedna mocna sesja w tygodniu wystarczy.",
        "<strong>Przykładowy plan na 3 tygodnie</strong>, siłownia, badania po sezonie i najczęstsze błędy.",
    ]),
    button("Czytaj artykuł", u("/blog/roztrenowanie-kolarstwo/", c)),
    dark_band("A po roztrenowaniu?",
              "Wróć mądrze od bazy. Plan <strong style=\"color:#ffd500;\">Baza tlenowa</strong> albo <strong style=\"color:#ffd500;\">Powrót do formy</strong> – 8 lub 12 tygodni rozpisanych jednostek w intervals.icu.",
              "Zobacz plany", u("/plany-treningowe/", c)),
    p("Masz pytanie o swoje roztrenowanie? Odpisz na tego maila – czytam wszystkie odpowiedzi.", 24),
    signature(),
    end(),
])
(OUT / "05-wpis-roztrenowanie.html").write_text(page("Roztrenowanie – niepopularna opinia", "Forma ucieka najpierw przez krew. Jak to zatrzymać bez trenażera?", body, c))

print("OK:", sorted(x.name for x in OUT.glob("*.html")))


# ---------- 6. RAPORT Z KALKULATORA CP (wysyłany przez Workera, params.* liczone w cp-model.js) ----------
c = "kalkulator-cp"
DARK, DARK_LINE, DARK_MUTED = "#141416", "#2a2a2d", "#a9a9ae"


def stat_cell(label, value, unit):
    return f"""<td class="stack stack-pad" width="25%" valign="top" style="padding:0 6px 0 0;">
            <div style="font:600 12px/14px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{DARK_MUTED};">{label}</div>
            <div style="padding-top:4px;font:800 34px/34px {DISPLAY};color:#ffffff;">{value}<span style="font-size:15px;color:{DARK_MUTED};"> {unit}</span></div>
          </td>"""


def report_hero():
    return f"""    <tr><td class="px" style="padding:26px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{DARK}" style="background-color:{DARK};background-image:linear-gradient({DARK},{DARK});border-radius:16px;">
        <tr><td style="padding:24px 24px 0;font:600 13px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{DARK_MUTED};">Twój fenotyp</td></tr>
        <tr><td style="padding:6px 24px 0;font:800 50px/48px {DISPLAY};text-transform:uppercase;color:{SUN};">{{{{ params.TYPE }}}}</td></tr>
        <tr><td style="padding:10px 24px 0;font:15px/23px {TEXT};color:#d6d4cd;">{{{{ params.TYPE_DESC }}}}</td></tr>
        <tr><td style="padding:20px 24px 24px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {DARK_LINE};"><tr><td style="padding-top:16px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          {stat_cell("CP", "{{ params.CP }}", "W")}
          {stat_cell("W'", "{{ params.WK }}", "kJ")}
          {stat_cell("VO2max", "{{ params.VO2 }}", "ml/kg")}
          {stat_cell("VLaMax", "{{ params.VLA }}", "mmol")}
            </tr></table>
          </td></tr></table>
        </td></tr>
      </table>
    </td></tr>"""


def kv_table(rows):
    trs = "".join(
        f"""
        <tr><td class="t-ink line" style="padding:11px 0;border-bottom:1px solid {LINE};font:15px/21px {TEXT};color:{INK};">{k}</td>
            <td class="t-ink line" align="right" style="padding:11px 0;border-bottom:1px solid {LINE};font:800 20px/22px {DISPLAY};color:{INK};white-space:nowrap;">{v}</td></tr>"""
        for k, v in rows)
    return f"""    <tr><td class="px" style="padding:10px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{trs}
      </table>
    </td></tr>"""


def loop_table(head, loop, cells):
    AR = 'align="right"'
    ths = "".join(f'<td class="t-muted line" {AR if i else ""} style="padding:0 0 8px;border-bottom:1px solid {LINE};font:600 12px/14px {DISPLAY};letter-spacing:1.5px;text-transform:uppercase;color:{MUTED};">{h}</td>' for i, h in enumerate(head))
    last = len(cells) - 1
    tds = "".join(f'<td class="t-ink line" {AR if i else ""} style="padding:10px 0;border-bottom:1px solid {LINE};font:{("800 18px/20px " + DISPLAY) if i == last else ("15px/20px " + TEXT)};color:{INK};">{c}</td>' for i, c in enumerate(cells))
    return f"""    <tr><td class="px" style="padding:12px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>{ths}</tr>
        {{% for {loop} %}}<tr>{tds}</tr>{{% endfor %}}
      </table>
    </td></tr>"""


def bullet_loop(var, color):
    return f"""    <tr><td class="px" style="padding:10px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        {{% for x in params.{var} %}}<tr><td valign="top" width="20" style="padding:6px 0;"><div style="width:10px;height:10px;border-radius:3px;background:{color};margin-top:6px;font-size:0;line-height:0;">&nbsp;</div></td><td class="t-ink" style="padding:6px 0;font:15px/23px {TEXT};color:{INK};">{{{{ x }}}}</td></tr>{{% endfor %}}
      </table>
    </td></tr>"""


def training_band():
    return f"""    <tr><td class="px" style="padding:30px 40px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{DARK}" style="background-color:{DARK};background-image:linear-gradient({DARK},{DARK});border-radius:16px;">
        <tr><td style="padding:24px 24px 0;font:600 13px/16px {DISPLAY};letter-spacing:2px;text-transform:uppercase;color:{DARK_MUTED};">Priorytet na najbliższe 8 tygodni</td></tr>
        <tr><td style="padding:8px 24px 0;font:800 24px/26px {DISPLAY};text-transform:uppercase;color:#ffffff;">{{{{ params.FOCUS }}}}</td></tr>
        <tr><td style="padding:14px 24px 22px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            {{% for s in params.SESSIONS %}}<tr><td style="padding:10px 0;border-top:1px solid {DARK_LINE};">
              <div style="font:800 18px/20px {DISPLAY};text-transform:uppercase;color:{SUN};">{{{{ s.n }}}}</div>
              <div style="padding-top:3px;font:14px/21px {TEXT};color:#d6d4cd;">{{{{ s.d }}}}</div>
            </td></tr>{{% endfor %}}
          </table>
        </td></tr>
      </table>
    </td></tr>"""


body = "\n".join([
    eyebrow("Kalkulator CP · raport"),
    h1("Twój profil mocy"),
    p(f"<strong>{GREETING}</strong>", 20),
    p("Oto pełny raport z kalkulatora na kompetition.cc: z Twoich wyników z 3 i 12 minut{% if params.SPRINT %} i sprintu 12 s{% endif %}. Zachowaj go – przyda się przy ustawianiu treningów i do porównania po kolejnym teście."),
    report_hero(),
    h2("Silnik", 32),
    kv_table([
        ("Moc krytyczna (CP) · {{ params.CP_RANK }}", "{{ params.CP_KG }} W/kg"),
        ("W' – bak beztlenowy · {{ params.W_LABEL }}", "{{ params.W_KG }} J/kg"),
        ("60 min (szac. FTP)", "{{ params.FTP }} W"),
        ("Wykorzystanie VO2max na progu", "{{ params.UTIL }}%"),
        ("Masa beztłuszczowa", "{{ params.FFM }} kg"),
    ]),
    p('<span class="t-muted" style="color:#5b5b60;font-size:14px;">{{ params.UTIL_TXT }}</span>', 12),
    h2("Metabolizm", 32),
    kv_table([
        ("VLaMax · {{ params.VLA_LABEL }}", "{{ params.VLA }} mmol/l/s"),
        ("FatMax (do ok. {{ params.MFO_GH }} g tłuszczu/h)", "{{ params.FATMAX }} W"),
        ("Włókna typu I (szacunek ± {{ params.T1_RANGE }} pp)", "{{ params.TYPE1 }}%"),
    ]),
    h2("Krzywa mocy", 32),
    loop_table(["Czas", "Moc", "W/kg"], "c in params.CURVE", ["{{ c.t }}", "{{ c.w }} W", "{{ c.wkg }}"]),
    h2("Paliwo", 32),
    loop_table(["Intensywność", "Moc", "Tłuszcz g/h", "Węgl. g/h"], "f in params.FUEL", ["{{ f.n }}", "{{ f.w }} W", "{{ f.fat }}", "{{ f.cho }}"]),
    p('<span style="display:block;background:#fff6c2;border-radius:12px;padding:14px 16px;font-size:14px;line-height:22px;color:#0b0b0c;">{{ params.FUEL_NOTE }}</span>', 14),
    h2("Mocne strony", 32),
    bullet_loop("STRENGTHS", "#1f9d55"),
    h2("Ograniczniki", 26),
    bullet_loop("LIMITERS", "#d9362b"),
    raw("{% if params.BODY %}"),
    p('<strong>Skład ciała.</strong> {{ params.BODY }}', 16),
    raw("{% endif %}"),
    training_band(),
    raw("{% if params.PLAN_NAME %}"),
    plan_card("Polecam na bazie Twojego profilu"),
    raw("{% endif %}"),
    code_box("WITAJ10", "Twój kod: −10% na pierwszy plan", "Wpisz go przy płatności · ważny 14 dni"),
    dark_band("Chcesz, żebym prowadził to za Ciebie?", "W opiece trenerskiej regularnie aktualizuję CP, W' i profil – i przekładam je na plan tydzień po tygodniu.", "Opieka trenerska", u("/opieka-trenerska/", c)),
    p('<span class="t-muted" style="color:#5b5b60;font-size:13px;line-height:20px;">Wyniki poza CP i W\' to szacunki z modelu i zależności opisanych w badaniach (m.in. Sitko i in. 2021 i 2023, Vanhatalo i in. 2016), nie pomiar laboratoryjny. Masz pytanie do raportu? Po prostu odpisz na tego maila.</span>', 24),
    signature(),
    end(),
])
(OUT / "06-raport-cp.html").write_text(page("Twój profil mocy", "CP, W', VO2max, VLaMax, FatMax, paliwo i plan – Twój raport z kalkulatora.", body, c))
