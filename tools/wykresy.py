#!/usr/bin/env python3
"""Wykresy i diagramy do wpisów na blogu (SVG z osadzonym, przyciętym fontem strony).

    python3 tools/wykresy.py      → assets/img/wykresy/*.svg

Wymaga: pip install fonttools brotli
"""
import base64, io, pathlib, re
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/img/wykresy"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = ROOT / "assets/fonts"

INK, INK2, SAND, LINE, MUTED, SUN, SUN_DEEP, WHITE = "#0b0b0c", "#2c2c30", "#f4f2ec", "#e4e1d8", "#5b5b60", "#ffd500", "#a88c00", "#ffffff"
SUN_SOFT = "#fff3b0"


# ---------------------------------------------------------------- fonty
def font_face(family, files, weight, text):
    """Przycina font do użytych znaków. Podstawowe znaki bierze wyłącznie z pierwszego pliku (latin),
    z drugiego (latin-ext) tylko te, których brakuje – z rozłącznym unicode-range, żeby się nie nakładały."""
    # napisy w stylu .h/.k mają text-transform:uppercase – font musi mieć też wielkie odpowiedniki liter
    chars = set(text) | set(text.upper()) | set(" 0123456789")
    out, taken = [], set()
    for f in files:
        opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga"]; opts.name_IDs = []; opts.notdef_outline = True
        font = TTFont(FONTS / f)
        cmap = font.getBestCmap()
        uni = sorted(ord(c) for c in chars if ord(c) in cmap and ord(c) not in taken)
        if not uni:
            continue
        taken.update(uni)
        s = subset.Subsetter(opts); s.populate(unicodes=uni); s.subset(font)
        buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
        rng = ",".join(f"U+{u:04X}" for u in uni)
        out.append(f"@font-face{{font-family:'{family}';font-weight:{weight};unicode-range:{rng};src:url(data:font/woff2;base64,{base64.b64encode(buf.getvalue()).decode()}) format('woff2')}}")
    return "".join(out)


def svg(name, w, h, body, title, desc):
    text = re.sub(r"<[^>]+>", " ", body) + title + desc
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    style = (font_face("KB", ["barlow-condensed-800-latin.woff2", "barlow-condensed-800-latin-ext.woff2"], 800, text) +
             font_face("KS", ["barlow-condensed-600-latin.woff2", "barlow-condensed-600-latin-ext.woff2"], 600, text) +
             font_face("KR", ["roboto-latin.woff2", "roboto-latin-ext.woff2"], "400 700", text) +
             ".h{font-family:KB,'Arial Narrow',Arial,sans-serif;font-weight:800;text-transform:uppercase}"
             ".k{font-family:KS,'Arial Narrow',Arial,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:.12em}"
             ".t{font-family:KR,Arial,sans-serif}.b{font-weight:700}")
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">'
           f'<title id="t">{title}</title><desc id="d">{desc}</desc><style>{style}</style>'
           f'<rect width="{w}" height="{h}" rx="24" fill="{WHITE}"/>{body}</svg>')
    (OUT / f"{name}.svg").write_text(doc, encoding="utf-8")
    print(f"{name}.svg  {len(doc)//1024} KB")


def t(x, y, s, size=22, cls="t", fill=INK, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


def header(kicker, title, w, y=64):
    return (f'<rect x="56" y="{y-28}" width="40" height="5" fill="{SUN}"/>' + t(108, y - 20, kicker, 18, "k", MUTED) +
            t(56, y + 26, title, 40, "h"))


def footer(src, w, h):
    return t(56, h - 30, src, 16, "t", MUTED) + t(w - 56, h - 30, "KOMpetition.cc", 18, "h", INK, "end")


# ================================================================ ROZTRENOWANIE
def detrening():
    W, H = 1200, 700
    x0, x1, y0, y1 = 130, 1120, 560, 170          # oś: tygodnie 0–12, % 80–100
    X = lambda wk: x0 + (x1 - x0) * wk / 12
    Y = lambda p: y0 - (y0 - y1) * (p - 80) / 20
    b = header("Co się dzieje z formą w przerwie", "Utrata formy po całkowitym odstawieniu treningu", W)
    b += f'<rect x="{X(0)}" y="{y1}" width="{X(3)-X(0)}" height="{y0-y1}" fill="{SUN_SOFT}"/>'
    b += t(X(1.5), y0 - 18, "Roztrenowanie 2–3 tyg.", 18, "h", SUN_DEEP, "middle")
    for p in (80, 85, 90, 95, 100):
        b += f'<line x1="{x0}" x2="{x1}" y1="{Y(p)}" y2="{Y(p)}" stroke="{LINE}" stroke-width="1.5"/>' + t(x0 - 14, Y(p) + 7, f"{p}%", 18, "t", MUTED, "end")
    for wk in range(0, 13, 2):
        b += t(X(wk), y0 + 34, str(wk), 18, "t", MUTED, "middle")
    b += t((x0 + x1) / 2, y0 + 66, "tygodnie bez treningu", 18, "t", MUTED, "middle")
    pts = [(0, 100), (3, 93), (8, 84), (12, 84)]
    b += f'<polyline points="{" ".join(f"{X(a)},{Y(c)}" for a, c in pts)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    for a, c in pts:
        b += f'<circle cx="{X(a)}" cy="{Y(c)}" r="8" fill="{INK}"/>'
    b += t(X(3) + 18, Y(93) - 16, "−7% VO2max po 3 tyg.", 20, "t b")
    b += t(X(10), Y(84) - 18, "−16% VO2max i stabilizacja", 20, "t b", INK, "middle")
    # objętość krwi: znacznik + ramka pod linią
    bx, by, bw_, bh = X(0.25), Y(85.9), X(6.4) - X(0.25), 78
    b += f'<circle cx="{X(3)}" cy="{Y(91)}" r="9" fill="{SUN}" stroke="{INK}" stroke-width="3"/>'
    b += f'<line x1="{X(3)}" y1="{Y(91)+10}" x2="{X(3)}" y2="{by}" stroke="{SUN_DEEP}" stroke-width="2" stroke-dasharray="4 4"/>'
    b += f'<rect x="{bx}" y="{by}" width="{bw_}" height="{bh}" rx="12" fill="{WHITE}" stroke="{SUN_DEEP}" stroke-width="2"/>'
    b += t(bx + 18, by + 32, "Objętość krwi −9%, osocza −12% już po 2–4 tyg.", 18, "t b", INK)
    b += t(bx + 18, by + 58, "→ sauna lub gorąca kąpiel 2–3 × w tyg. pomaga ją podtrzymać", 17, "t b", SUN_DEEP)
    b += (f'<rect x="{X(8.3)}" y="{Y(84)+22}" width="{X(12)-X(8.3)+10}" height="58" rx="10" fill="{SAND}"/>' +
          t(X(8.3) + 14, Y(84) + 46, "Po 12 tyg. VO2max wciąż wyżej", 17, "t", INK2) + t(X(8.3) + 14, Y(84) + 68, "niż u osób nietrenujących", 17, "t", INK2))
    b += footer("Dane: Coyle i wsp. 1984, 1986 – wytrenowani zawodnicy wytrzymałościowi.", W, H)
    svg("roztrenowanie-utrata-formy", W, H, b, "Utrata formy po odstawieniu treningu",
        "VO2max spada o ok. 7% po 3 tygodniach i stabilizuje się ok. 16% poniżej poziomu z treningu po 8–12 tygodniach; objętość krwi spada o ok. 9% po 2–4 tygodniach.")


def minimalna_dawka():
    W, H = 1200, 780
    b = header("Minimalna dawka treningu", "Co chroni formę, a co nie", W)
    rows = [
        ("2 intensywne sesje w tygodniu", "Hickson i Rosenkoetter 1981, 15 tyg.", [("VO2max", 0)]),
        ("1 × 35 min intensywnie w tygodniu", "Madsen i wsp. 1993, 4 tyg.", [("VO2max", 0), ("wytrzymałość", -21)]),
        ("Ta sama częstość, intensywność −1/3", "Hickson i wsp. 1985, 15 tyg.", [("długa wytrzymałość", -21)]),
        ("Całkowita przerwa", "Coyle i wsp. 1984, 3 tyg.", [("VO2max", -7)]),
    ]
    zx, sc = 760, 14                                  # 0% i skala: px na 1%
    b += f'<line x1="{zx}" x2="{zx}" y1="150" y2="{150 + len(rows)*125}" stroke="{INK}" stroke-width="2"/>'
    b += t(zx, 140, "0%", 18, "t b", INK, "middle")
    for p in (-10, -20):
        b += f'<line x1="{zx+p*sc}" x2="{zx+p*sc}" y1="150" y2="{150+len(rows)*125}" stroke="{LINE}" stroke-dasharray="4 6"/>' + t(zx + p * sc, 140, f"−{-p}%", 18, "t", MUTED, "middle")
    y = 175
    for label, src, bars in rows:
        b += t(56, y + 18, label, 22, "t b") + t(56, y + 46, src, 17, "t", MUTED)
        for i, (name, v) in enumerate(bars):
            by = y + i * 42
            col = INK if name == "VO2max" else SUN
            if v == 0:
                b += f'<rect x="{zx-4}" y="{by}" width="8" height="30" rx="3" fill="{col}"/>' + t(zx + 18, by + 22, f"{name}: bez spadku ✓", 19, "t b", "#1f7a3a")
            else:
                b += f'<rect x="{zx+v*sc}" y="{by}" width="{-v*sc}" height="30" rx="4" fill="{col}"/>' + t(zx + 16, by + 22, f"{name}: −{-v}%", 19, "t b")
        y += 125
    b += (f'<rect x="56" y="{H-122}" width="{W-112}" height="56" rx="12" fill="{SUN_SOFT}"/>' +
          t(80, H - 86, "Wniosek: utrzymaj intensywność – objętość i częstość możesz mocno obniżyć (Spiering i wsp. 2021).", 20, "t b", INK))
    b += footer("Zmiany względem poziomu z okresu treningu.", W, H)
    svg("roztrenowanie-minimalna-dawka", W, H, b, "Minimalna dawka treningu – co chroni formę",
        "Dwie intensywne sesje tygodniowo utrzymują VO2max; jedna krótka intensywna sesja utrzymuje VO2max, ale wytrzymałość spada o 21%; obniżenie intensywności o jedną trzecią obniża długą wytrzymałość o 21%; całkowita przerwa to −7% VO2max po 3 tygodniach.")


def sezon():
    W, H = 1200, 600
    b = header("Periodyzacja roku", "Gdzie w sezonie jest roztrenowanie", W)
    months = ["paź", "lis", "gru", "sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz"]
    x0, x1, yb = 70, 1130, 480
    mw = (x1 - x0) / 12
    X = lambda m: x0 + mw * m
    for i, m in enumerate(months):
        b += t(X(i) + mw / 2, yb + 34, m, 18, "t", MUTED, "middle")
        b += f'<line x1="{X(i)}" x2="{X(i)}" y1="{yb}" y2="{yb+10}" stroke="{MUTED}"/>'
    b += f'<line x1="{x0}" x2="{x1}" y1="{yb}" y2="{yb}" stroke="{INK}" stroke-width="2"/>'
    blocks = [(0.75, 4.5, "Okres przygotowawczy", "baza tlenowa · siła · trenażer", INK, WHITE),
              (4.5, 6.0, "Budowa", "próg · VO2max", INK2, WHITE), (6.0, 12, "Okres startowy", "starty · utrzymanie · taper", SAND, INK)]
    b += f'<rect x="{X(0)+2}" y="{yb-78}" width="{X(0.75)-X(0)-4}" height="66" rx="10" fill="{SUN}"/>'
    for a, c, name, sub, fill, fc in blocks:
        b += f'<rect x="{X(a)+2}" y="{yb-78}" width="{X(c)-X(a)-4}" height="66" rx="10" fill="{fill}"/>'
        b += t((X(a) + X(c)) / 2, yb - 49, name, 21, "h", fc, "middle") + t((X(a) + X(c)) / 2, yb - 25, sub, 15, "t", fc, "middle")
    # krzywa obciążenia
    pts = [(0, 18), (0.75, 16), (1.2, 42), (3, 60), (4.5, 68), (5.5, 86), (6, 78), (7, 90), (8, 84), (9, 92), (10, 86), (11, 80), (11.8, 55), (12, 30)]
    Y = lambda v: yb - 100 - (v / 100) * 200
    b += f'<polyline points="{" ".join(f"{X(a)},{Y(v)}" for a, v in pts)}" fill="none" stroke="{SUN_DEEP}" stroke-width="4" stroke-linejoin="round"/>'
    b += t(X(7.4), Y(94) - 14, "obciążenie treningowe", 18, "t b", SUN_DEEP, "middle")
    # opis roztrenowania
    bx, by = X(0) + 4, 136
    b += f'<rect x="{bx}" y="{by}" width="300" height="92" rx="12" fill="{SUN_SOFT}" stroke="{SUN_DEEP}" stroke-width="2"/>'
    b += t(bx + 16, by + 30, "Roztrenowanie 2–3 tyg.", 20, "h", INK) + t(bx + 16, by + 56, "głowa odpoczywa, zdrowie,", 17, "t", INK2) + t(bx + 16, by + 78, "siłownia, ciepło, luźny ruch", 17, "t", INK2)
    b += f'<line x1="{X(0.375)}" y1="{by+92}" x2="{X(0.375)}" y2="{yb-80}" stroke="{SUN_DEEP}" stroke-width="2" stroke-dasharray="4 4"/>'
    b += footer("Przykład dla sezonu szosowego w Polsce – terminy przesuń pod swój kalendarz startów.", W, H)
    svg("roztrenowanie-periodyzacja-sezonu", W, H, b, "Roztrenowanie w periodyzacji rocznej",
        "Po sezonie startowym 2–3 tygodnie roztrenowania z niskim obciążeniem, potem okres przygotowawczy od listopada do lutego, budowa formy i okres startowy od kwietnia do września.")


# ================================================================ ŻYWIENIE
def wegle_na_godzine():
    W, H = 1200, 700
    b = header("Węglowodany podczas jazdy", "Ile węglowodanów na godzinę?", W)
    x0, y0, y1 = 150, 560, 170                       # 0–120 g/h
    Y = lambda g: y0 - (y0 - y1) * g / 120
    for g in (0, 30, 60, 90, 120):
        b += f'<line x1="{x0}" x2="1130" y1="{Y(g)}" y2="{Y(g)}" stroke="{LINE}" stroke-width="1.5"/>' + t(x0 - 14, Y(g) + 7, f"{g}", 18, "t", MUTED, "end")
    b += t(x0 - 14, y1 - 22, "g/h", 18, "t b", MUTED, "end")
    bars = [("do 45 min", 0, "niepotrzebne", LINE), ("45–75 min", 8, "płukanie ust", LINE), ("1–2 h", 30, "do 30 g/h", SUN),
            ("2–3 h", 60, "do 60 g/h", SUN), ("> 2,5 h", 90, "do 90 g/h", INK), ("długie wyścigi*", 120, "90–120 g/h", INK)]
    bw, gap = 118, 45
    for i, (lab, g, val, col) in enumerate(bars):
        x = x0 + 30 + i * (bw + gap)
        h = max(y0 - Y(g), 4)
        b += f'<rect x="{x}" y="{y0-h}" width="{bw}" height="{h}" rx="8" fill="{col}"/>'
        b += t(x + bw / 2, y0 - h - 14, val, 19, "t b", INK, "middle")
        b += t(x + bw / 2, y0 + 34, lab, 19, "t", INK2, "middle")
    for k in (4, 5):
        cx = x0 + 30 + k * (bw + gap) + bw / 2
        b += t(cx, Y(90) + 40, "glukoza", 16, "t b", SUN, "middle") + t(cx, Y(90) + 60, "+ fruktoza", 16, "t b", SUN, "middle")
    b += t(56, H - 64, "* przy wytrenowanym przewodzie pokarmowym, glukoza : fruktoza ok. 1 : 0,8", 17, "t", MUTED)
    b += footer("Dane: Jeukendrup 2014; Burke i wsp. 2011; Hearris i wsp. 2022; Podlogar i wsp. 2022.", W, H)
    svg("zywienie-weglowodany-na-godzine", W, H, b, "Ile węglowodanów na godzinę jazdy",
        "Do 45 minut węglowodany niepotrzebne, 45–75 minut płukanie ust, 1–2 h do 30 g/h, 2–3 h do 60 g/h, powyżej 2,5 h do 90 g/h, a w długich wyścigach przy wytrenowanym żołądku 90–120 g/h mieszanki glukozy i fruktozy.")


def wegle_dziennie():
    W, H = 1200, 640
    b = header("Periodyzacja węglowodanów", "Węglowodany dziennie a obciążenie", W)
    x0, x1 = 400, 1000
    X = lambda g: x0 + (x1 - x0) * g / 12
    for g in range(0, 13, 2):
        b += f'<line x1="{X(g)}" x2="{X(g)}" y1="150" y2="500" stroke="{LINE}" stroke-width="1.5"/>' + t(X(g), 530, str(g), 18, "t", MUTED, "middle")
    b += t((x0 + x1) / 2, 560, "g węglowodanów na kg masy ciała dziennie", 18, "t", MUTED, "middle")
    b += t(1130, 140, "kolarz 70 kg", 17, "t b", MUTED, "end")
    rows = [("Lekkie", "dzień wolny, luźny ruch", 3, 5, "210–350 g"), ("Umiarkowane", "ok. 1 h treningu", 5, 7, "350–490 g"),
            ("Wysokie", "1–3 h, także intensywnie", 6, 10, "420–700 g"), ("Bardzo wysokie", "4–5 h+, obozy, etapówki", 8, 12, "560–840 g")]
    for i, (n, sub, a, c, g70) in enumerate(rows):
        y = 170 + i * 84
        b += t(56, y + 26, n, 24, "h") + t(56, y + 52, sub, 17, "t", MUTED)
        col = [SUN_SOFT, SUN, SUN_DEEP, INK][i]
        b += f'<rect x="{X(a)}" y="{y+6}" width="{X(c)-X(a)}" height="44" rx="22" fill="{col}"/>'
        b += t((X(a) + X(c)) / 2, y + 36, f"{a}–{c}", 22, "h", WHITE if i >= 2 else INK, "middle")
        b += t(1130, y + 36, g70, 20, "t b", INK, "end")
    b += footer("Dane: Burke i wsp. 2011; Thomas i wsp. (ACSM) 2016.", W, H)
    svg("zywienie-weglowodany-dziennie", W, H, b, "Dzienne zapotrzebowanie na węglowodany",
        "Obciążenie lekkie 3–5 g/kg, umiarkowane 5–7 g/kg, wysokie 6–10 g/kg, bardzo wysokie 8–12 g/kg; dla kolarza 70 kg od 210 do 840 g dziennie.")


def glukoza_fruktoza():
    W, H = 1200, 660
    b = header("Dlaczego mieszanka cukrów", "Glukoza + fruktoza = więcej energii na godzinę", W)
    # jelito
    b += f'<rect x="80" y="170" width="1040" height="120" rx="20" fill="{SAND}"/>' + t(110, 205, "Światło jelita", 18, "k", MUTED)
    b += f'<rect x="80" y="300" width="1040" height="26" fill="{SUN_SOFT}"/>' + t(600, 319, "Ściana jelita – transportery", 15, "k", SUN_DEEP, "middle")
    b += f'<rect x="80" y="336" width="1040" height="96" rx="20" fill="{INK}"/>' + t(110, 372, "Krew → mięśnie", 18, "k", "#d9d9dc")
    # kulki cukrów
    import random
    random.seed(4)
    for i in range(16):
        x = 150 + random.random() * 330; y = 225 + random.random() * 55
        b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="{INK}"/>'
    for i in range(12):
        x = 640 + random.random() * 300; y = 225 + random.random() * 55
        b += f'<rect x="{x:.0f}" y="{y:.0f}" width="20" height="20" rx="4" fill="{SUN_DEEP}"/>'
    # transportery
    for cx, name, sub, col in ((330, "SGLT1", "glukoza, maltodekstryna", INK), (870, "GLUT5", "fruktoza", SUN_DEEP)):
        b += f'<rect x="{cx-70}" y="292" width="140" height="42" rx="21" fill="{col}"/>' + t(cx, 320, name, 22, "h", WHITE, "middle")
        b += f'<path d="M{cx} 336 v70" stroke="{SUN if col==INK else WHITE}" stroke-width="6" marker-end="url(#a)"/>'
        b += t(cx, 470, sub, 19, "t b", INK, "middle")
    b = b.replace('<rect x="80" y="170"', f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="{SUN}"/></marker></defs><rect x="80" y="170"', 1)
    b += (f'<circle cx="{W-300}" cy="199" r="9" fill="{INK}"/>' + t(W - 284, 205, "glukoza", 16, "t", INK) +
          f'<rect x="{W-200}" y="190" width="18" height="18" rx="4" fill="{SUN_DEEP}"/>' + t(W - 174, 205, "fruktoza", 16, "t", INK))
    b += t(330, 500, "limit ok. 60 g/h", 22, "h", INK, "middle") + t(870, 500, "dodatkowa droga", 22, "h", SUN_DEEP, "middle")
    b += (f'<rect x="300" y="530" width="600" height="60" rx="30" fill="{SUN}"/>' +
          t(600, 569, "Razem: 90 g/h, u wytrenowanych do 120 g/h (1 : 0,8)", 22, "t b", INK, "middle"))
    b += footer("Dane: Jeukendrup 2014; Podlogar i wsp. 2022; Hearris i wsp. 2022.", W, H + 10)
    svg("zywienie-glukoza-fruktoza", W, H + 10, b, "Wchłanianie glukozy i fruktozy",
        "Glukoza i maltodekstryna są wchłaniane przez transporter SGLT1 z limitem ok. 60 g/h, a fruktoza osobną drogą przez GLUT5; mieszanka pozwala na 90 g/h, a u wytrenowanych do 120 g/h w proporcji 1:0,8.")


def dzien_wyscigu():
    W, H = 1200, 540
    b = header("Plan żywienia", "Dzień wyścigu krok po kroku", W)
    y = 300
    b += f'<line x1="70" x2="1130" y1="{y}" y2="{y}" stroke="{INK}" stroke-width="4"/>'
    b += f'<rect x="800" y="{y-12}" width="230" height="24" rx="12" fill="{SUN}"/>' + t(915, y + 6, "WYŚCIG", 18, "h", INK, "middle")
    steps = [(110, "D-2 / D-1", ["10–12 g/kg węgli", "przy starcie > 90 min", "mniej błonnika"]),
             (300, "3–4 h przed", ["1–4 g/kg węgli", "lekkostrawnie", "500 ml płynów"]),
             (480, "60 min", ["kofeina 3–6 mg/kg", "(jeśli testowana)"]),
             (640, "15–30 min", ["żel lub", "pół batona"]),
             (915, "w trakcie", ["30–120 g/h", "co 15–20 min", "płyny z sodem"]),
             (1090, "po", ["węgle + białko", "płyny i sód"])]
    for i, (x, lab, lines) in enumerate(steps):
        up = i % 2 == 0
        if x != 915:
            b += f'<circle cx="{x}" cy="{y}" r="12" fill="{SUN}" stroke="{INK}" stroke-width="3"/>'
        ly = y - 60 if up else y + 50
        b += f'<line x1="{x}" x2="{x}" y1="{y + (-14 if up else 14)}" y2="{ly + (12 if up else -24)}" stroke="{MUTED}" stroke-dasharray="3 5"/>'
        if up:
            b += t(x, ly - 18 * len(lines) - 10, lab, 24, "h", INK, "middle")
            for j, ln in enumerate(lines):
                b += t(x, ly - 18 * (len(lines) - j) + 12, ln, 17, "t", INK2, "middle")
        else:
            b += t(x, ly + 8, lab, 24, "h", INK, "middle")
            for j, ln in enumerate(lines):
                b += t(x, ly + 36 + j * 22, ln, 17, "t", INK2, "middle")
    b += footer("Dane: Thomas i wsp. (ACSM) 2016; Guest i wsp. 2021; Jeukendrup 2014.", W, H)
    svg("zywienie-dzien-wyscigu", W, H, b, "Plan żywienia w dniu wyścigu",
        "Dwa dni przed 10–12 g/kg węglowodanów, 3–4 h przed start posiłek 1–4 g/kg, 60 minut przed kofeina, 15–30 minut przed żel, w trakcie 30–120 g/h z płynami z sodem, po wyścigu węglowodany i białko.")


def piramida():
    W, H = 1200, 720
    b = header("Hierarchia suplementacji", "Piramida suplementów kolarza", W)
    tiers = [("Podstawy: energia, węglowodany, białko, nawodnienie, sen", "fundament – bez tego suplementy nie mają sensu", INK, WHITE),
             ("Kofeina", "najlepiej przebadany suplement wytrzymałościowy", SUN_DEEP, WHITE),
             ("Zależnie od celu: azotany, beta-alanina, wodorowęglan, kreatyna", "wybrane sytuacje i dyscypliny", SUN, INK),
             ("Regeneracja: cierpka wiśnia", "wokół startów i obozów", SUN_SOFT, INK),
             ("Reszta półki", "zwykle zbędna", SAND, MUTED)]
    cx, base_y, th, bw, top = 600, 620, 88, 1060, 300
    for i, (a, sub, fill, fc) in enumerate(tiers):
        yb = base_y - i * th; yt = yb - th + 6
        wb = bw - (bw - top) * i / len(tiers); wt = bw - (bw - top) * (i + 1) / len(tiers)
        b += f'<polygon points="{cx-wb/2},{yb} {cx+wb/2},{yb} {cx+wt/2},{yt} {cx-wt/2},{yt}" fill="{fill}"/>'
        size = 22 if len(a) < 40 else 19
        b += t(cx, yb - 48, a, size, "t b", fc, "middle") + t(cx, yb - 22, sub, 16, "t", fc, "middle")
    b += footer("Na podstawie: Maughan i wsp. (konsensus MKOl) 2018 i przeglądów cytowanych w artykule.", W, H)
    svg("zywienie-piramida-suplementow", W, H, b, "Piramida suplementów kolarza",
        "Podstawą są energia, węglowodany, białko, nawodnienie i sen; wyżej kofeina; dalej zależnie od celu azotany, beta-alanina, wodorowęglan sodu i kreatyna; potem cierpka wiśnia na regenerację; reszta suplementów zwykle zbędna.")


# ================================================================ HEAT TRAINING
def heat_os_czasu():
    W, H = 1200, 620
    b = header("Heat training – kiedy co działa", "Oś czasu adaptacji do ciepła", W)
    x0, x1 = 300, 1130
    X = lambda d: x0 + (x1 - x0) * d / 35          # dni 0–35
    for d in (0, 7, 14, 21, 28, 35):
        b += f'<line x1="{X(d)}" x2="{X(d)}" y1="150" y2="500" stroke="{LINE}" stroke-width="1.5"/>' + t(X(d), 530, f"{d}", 18, "t", MUTED, "middle")
    b += t((x0 + x1) / 2, 560, "dni treningu w cieple", 18, "t", MUTED, "middle")
    rows = [("Osocze, tętno", "niższe HR przy tej samej mocy", 3, 6, SUN_SOFT, INK),
            ("Pot", "mniej sodu, potem więcej potu", 3, 10, SUN, INK),
            ("Temperatura głęboka", "niższa w spoczynku i na koniec", 5, 14, SUN_DEEP, WHITE),
            ("Masa hemoglobiny", "+3–5% – forma także w chłodzie", 21, 35, INK, WHITE)]
    for i, (n, sub, a, c, col, fc) in enumerate(rows):
        y = 168 + i * 82
        b += t(56, y + 26, n, 23, "h") + t(56, y + 52, sub, 16, "t", MUTED)
        b += f'<rect x="{X(a)}" y="{y+6}" width="{X(c)-X(a)}" height="44" rx="22" fill="{col}"/>'
        lab = f"dni {a}–{c}" if c <= 14 else "tyg. 3–5"
        b += t((X(a) + X(c)) / 2, y + 36, lab, 20, "h", fc, "middle")
    b += footer("Dane: Klous i wsp. 2020; Tyler i wsp. 2016; Rønnestad i wsp. 2020; Lundby i wsp. 2023; Cubel i wsp. 2024.", W, H)
    svg("heat-os-czasu-adaptacji", W, H, b, "Oś czasu adaptacji do ciepła",
        "Objętość osocza i spadek tętna w dniach 3–6, zmiany potu w dniach 3–10, niższa temperatura głęboka w dniach 5–14, wzrost masy hemoglobiny o 3–5% po 3–5 tygodniach.")


# ================================================================ GROSS EFFICIENCY
def ge_porownanie():
    W, H = 1200, 640
    b = header("Gross Efficiency w liczbach", "Ta sama energia, inna moc na pedałach", W)
    kcal = 1075                                       # ≈ 1250 W mocy metabolicznej przez godzinę
    rows = [("GE 18%", 225, LINE, INK), ("GE 20%", 250, SUN, INK), ("GE 22%", 275, INK, WHITE)]
    x0, sc = 260, 3.2
    for i, (lab, w, col, fc) in enumerate(rows):
        y = 180 + i * 104
        b += t(56, y + 44, lab, 34, "h")
        b += f'<rect x="{x0}" y="{y}" width="{w*sc}" height="64" rx="12" fill="{col}"/>'
        b += t(x0 + w * sc - 20, y + 43, f"{w} W", 30, "h", fc, "end")
    b += t(x0, 160, f"Kolarz spala ok. {kcal} kcal na godzinę (moc metaboliczna ok. 1250 W)", 19, "t b", INK2)
    b += (f'<rect x="56" y="{H-150}" width="{W-112}" height="64" rx="12" fill="{SUN_SOFT}"/>' +
          t(80, H - 110, "+2 punkty procentowe GE = ok. +25 W przy tym samym koszcie energii", 22, "t b", INK) )
    b += footer("GE = moc mechaniczna / wydatek energetyczny × 100. Typowo 18–23% (Moseley i Jeukendrup 2001).", W, H)
    svg("ge-ta-sama-energia", W, H, b, "Gross Efficiency – ta sama energia, inna moc",
        "Przy tym samym wydatku energii ok. 1250 W mocy metabolicznej kolarz z GE 18% generuje 225 W, z GE 20% 250 W, a z GE 22% 275 W.")


# ================================================================ LAKTAT
def krzywa_mleczanowa():
    W, H = 1200, 680
    b = header("Test laktatowy", "Krzywa mleczanowa, LT1 i LT2", W)
    x0, x1, y0, y1 = 130, 1120, 560, 150
    X = lambda w: x0 + (x1 - x0) * (w - 100) / 300   # 100–400 W
    Y = lambda l: y0 - (y0 - y1) * l / 10             # 0–10 mmol/l
    lt1, lt2 = 205, 290
    b += f'<rect x="{x0}" y="{y1}" width="{X(lt1)-x0}" height="{y0-y1}" fill="{SAND}"/>'
    b += f'<rect x="{X(lt1)}" y="{y1}" width="{X(lt2)-X(lt1)}" height="{y0-y1}" fill="{SUN_SOFT}"/>'
    b += f'<rect x="{X(lt2)}" y="{y1}" width="{x1-X(lt2)}" height="{y0-y1}" fill="#ffe7e0"/>'
    for l in (0, 2, 4, 6, 8, 10):
        b += f'<line x1="{x0}" x2="{x1}" y1="{Y(l)}" y2="{Y(l)}" stroke="{LINE}" stroke-width="1.5"/>' + t(x0 - 14, Y(l) + 7, str(l), 18, "t", MUTED, "end")
    for w in range(100, 401, 50):
        b += t(X(w), y0 + 34, str(w), 18, "t", MUTED, "middle")
    b += t((x0 + x1) / 2, y0 + 66, "moc [W]", 18, "t", MUTED, "middle") + t(x0 - 14, y1 - 22, "mmol/l", 18, "t b", MUTED, "end")
    import math
    pts = [(w, 1.0 + 0.0 * w if w < 190 else 1.0 + 0.9 * math.exp((w - 250) / 38) - 0.9 * math.exp((190 - 250) / 38)) for w in range(100, 341, 5)]
    pts = [(w, min(l, 10)) for w, l in pts]
    b += f'<polyline points="{" ".join(f"{X(w):.1f},{Y(l):.1f}" for w, l in pts)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    for w, l in [(w, l) for w, l in pts if w % 25 == 0]:
        b += f'<circle cx="{X(w):.1f}" cy="{Y(l):.1f}" r="7" fill="{SUN}" stroke="{INK}" stroke-width="2.5"/>'
    for w, name, sub in ((lt1, "LT1", "pierwszy wzrost ponad spoczynek"), (lt2, "LT2", "szybki wzrost, okolice MLSS")):
        b += f'<line x1="{X(w)}" x2="{X(w)}" y1="{y1}" y2="{y0}" stroke="{INK}" stroke-width="2" stroke-dasharray="6 6"/>'
        if w == lt1:
            b += t(X(w) + 12, y1 + 34, name, 30, "h") + t(X(w) + 12, y1 + 60, sub, 16, "t", INK2)
        else:
            b += t(x1 - 14, y1 + 124, name + " ≈ 290 W", 30, "h", INK, "end") + t(x1 - 14, y1 + 150, sub, 16, "t", INK2, "end")
    b += t((x0 + X(lt1)) / 2, y0 - 20, "Strefa 1", 20, "h", INK2, "middle") + t((X(lt1) + X(lt2)) / 2, y0 - 20, "Strefa 2", 20, "h", SUN_DEEP, "middle") + t((X(lt2) + x1) / 2, y0 - 20, "Strefa 3", 20, "h", "#b3261e", "middle")
    b += footer("Przykładowa krzywa kolarza z FTP ok. 290 W. Model 3 stref: Seiler 2010; Faude i wsp. 2009.", W, H)
    svg("laktat-krzywa-lt1-lt2", W, H, b, "Krzywa mleczanowa z LT1 i LT2",
        "Stężenie mleczanu jest stałe do ok. 200 W (LT1), potem rośnie, a powyżej ok. 290 W (LT2) gwałtownie przyspiesza; progi dzielą intensywność na trzy strefy.")


# ================================================================ CELE
def cele_hierarchia():
    W, H = 1200, 600
    b = header("Wyznaczanie celów", "Od celu wynikowego do codziennego treningu", W)
    cols = [("Wynikowy", "np. top 10 w Gran Fondo", "zależy też od rywali i pogody", INK, WHITE),
            ("Wykonawczy", "np. FTP 4,0 W/kg, CP +15 W", "mierzalny, w Twojej kontroli", SUN_DEEP, WHITE),
            ("Procesowy", "np. 2 × interwały tygodniowo,", "sen 8 h, 80 g węgli/h na długich", SUN, INK)]
    cw, gap = 330, 45
    for i, (n, a, c, col, fc) in enumerate(cols):
        x = 56 + i * (cw + gap)
        b += f'<rect x="{x}" y="170" width="{cw}" height="230" rx="18" fill="{col}"/>'
        b += t(x + 26, 222, f"Cel {n}".upper() if False else n, 34, "h", fc) + t(x + 26, 290, a, 19, "t b", fc) + t(x + 26, 320, c, 18, "t", fc)
        b += t(x + 26, 375, ["sezon", "8–12 tygodni", "każdy tydzień"][i], 18, "k", fc)
        if i < 2:
            ax = x + cw + 6
            b += f'<path d="M{ax} 285 h{gap-14}" stroke="{INK}" stroke-width="4"/><path d="M{ax+gap-18} 275 l12 10 l-12 10" fill="none" stroke="{INK}" stroke-width="4"/>'
    b += (f'<rect x="56" y="430" width="{W-112}" height="64" rx="12" fill="{SAND}"/>' +
          t(80, 470, "Starty A / B / C: 1–3 starty A na sezon, B jako sprawdzian, C jako trening pod obciążeniem", 20, "t b", INK))
    b += footer("Cel wynikowy wyznacza kierunek, wykonawczy – plan, procesowy – codzienność.", W, H)
    svg("cele-hierarchia", W, H, b, "Hierarchia celów treningowych",
        "Cel wynikowy na sezon, cel wykonawczy na 8–12 tygodni i cele procesowe na każdy tydzień; starty dzielone na priorytety A, B i C.")


# ================================================================ TEST CP 3/12 MIN
def test_cp_protokol():
    W, H = 1200, 640
    b = header("Test CP w jednej sesji", "Przebieg testu 3 + 12 minut", W)
    x0, x1, base = 70, 1130, 470
    total = 20 + 10 + 3 + 30 + 12 + 10          # min (sprint i luz po nim w bloku 10 min)
    X = lambda m: x0 + (x1 - x0) * m / total
    hmax = 290
    blocks = [  # (start, dł., wysokość 0–1, kolor, podpis, podpis2)
        (0, 20, .42, SAND, "Rozgrzewka", "20 min Z2 + 3×1 min"),
        (20, 10, .30, SAND, "Luz", "10 min"),
        (30, 3, 1.0, INK, "3 min", "all-out"),
        (33, 30, .25, SAND, "Luz", "30 min spokojnie"),
        (63, 12, .78, INK, "12 min", "all-out"),
        (75, 10, .25, SAND, "Schłodzenie", "10 min"),
    ]
    for st, d, hh, col, a, c in blocks:
        h = hmax * hh
        b += f'<rect x="{X(st)+2}" y="{base-h}" width="{X(st+d)-X(st)-4}" height="{h}" rx="8" fill="{col}" stroke="{LINE if col==SAND else INK}" stroke-width="2"/>'
        cx = (X(st) + X(st + d)) / 2
        if col == INK:
            b += t(cx, base - h - 40, a, 30, "h", INK, "middle") + t(cx, base - h - 14, c, 18, "k", SUN_DEEP, "middle")
        else:
            b += t(cx, base + 34, a, 20, "h", INK, "middle") + t(cx, base + 58, c, 16, "t", MUTED, "middle")
    # rozgrzewka: 3 krótkie przebieżki
    for k in range(3):
        xm = X(8 + k * 4)
        b += f'<rect x="{xm}" y="{base-hmax*.62}" width="{X(1)-X(0)}" height="{hmax*.62}" rx="3" fill="{SUN}"/>'
    # opcjonalny sprint
    xs = X(21.5)
    b += f'<rect x="{xs}" y="{base-hmax*1.0}" width="8" height="{hmax*1.0}" rx="3" fill="{SUN}" stroke="{INK}" stroke-width="1.5"/>'
    b += t(xs - 12, base - hmax * .88, "sprint 12 s", 17, "t b", INK, "end") + t(xs - 12, base - hmax * .88 + 20, "(opcjonalnie)", 16, "t", MUTED, "end")
    b += f'<line x1="{x0}" x2="{x1}" y1="{base}" y2="{base}" stroke="{INK}" stroke-width="2"/>'
    b += footer("Ok. 85 min. Przerwa 30 min między próbami nie zmienia CP ani W' (Triska i in. 2021).", W, H)
    svg("test-cp-protokol", W, H, b, "Przebieg testu CP 3 + 12 minut",
        "Rozgrzewka 20 minut z trzema krótkimi przyspieszeniami, opcjonalny sprint 12 s, 3 minuty all-out, 30 minut spokojnej jazdy, 12 minut all-out i schłodzenie.")


def test_cp_model():
    W, H = 1200, 680
    b = header("Jak z dwóch wyników powstaje CP i W'", "Model mocy krytycznej", W)
    x0, x1, y0, y1 = 130, 1100, 560, 150
    tmax, pmin, pmax = 20, 250, 450
    X = lambda m: x0 + (x1 - x0) * m / tmax
    Y = lambda p: y0 - (y0 - y1) * (p - pmin) / (pmax - pmin)
    cp, wj = 280, 21600
    for pv in range(250, 451, 50):
        b += f'<line x1="{x0}" x2="{x1}" y1="{Y(pv)}" y2="{Y(pv)}" stroke="{LINE}" stroke-width="1.5"/>' + t(x0 - 14, Y(pv) + 7, f"{pv} W", 17, "t", MUTED, "end")
    for m in (2, 5, 10, 15, 20):
        b += t(X(m), y0 + 32, f"{m} min", 17, "t", MUTED, "middle")
    pts = [(m / 10, cp + wj / (m * 6)) for m in range(20, 201)]
    area = f"M{X(2)},{Y(cp)} " + " ".join(f"L{X(a)},{Y(min(p, pmax))}" for a, p in pts) + f" L{X(20)},{Y(cp)} Z"
    b += f'<path d="{area}" fill="{SUN_SOFT}"/>'
    b += f'<polyline points="{" ".join(f"{X(a)},{Y(min(p, pmax))}" for a, p in pts)}" fill="none" stroke="{INK}" stroke-width="5"/>'
    b += f'<line x1="{x0}" x2="{x1}" y1="{Y(cp)}" y2="{Y(cp)}" stroke="#d9362b" stroke-width="3" stroke-dasharray="10 8"/>'
    b += t(x1, Y(cp) + 30, "CP = 280 W – granica stanu równowagi", 19, "t b", "#d9362b", "end")
    for m, pv, lab in ((3, 400, "3 min: 400 W"), (12, 310, "12 min: 310 W")):
        b += f'<circle cx="{X(m)}" cy="{Y(pv)}" r="11" fill="{SUN}" stroke="{INK}" stroke-width="4"/>' + t(X(m) + 20, Y(pv) - 16, lab, 21, "h")
    b += t(X(4.3), Y(304), "W' = 21,6 kJ", 26, "h", SUN_DEEP) + t(X(4.3), Y(304) + 22, "„bak” pracy powyżej CP", 17, "t", SUN_DEEP)
    bx = X(13.2)
    b += (f'<rect x="{bx}" y="{Y(445)}" width="{x1-bx}" height="116" rx="12" fill="{SAND}"/>' +
          t(bx + 18, Y(445) + 34, "CP = (P12·720 − P3·180) / 540", 18, "t b") +
          t(bx + 18, Y(445) + 64, "W' = (P3 − CP) · 180", 18, "t b") +
          t(bx + 18, Y(445) + 94, "moc w W, czas w sekundach", 16, "t", MUTED))
    b += footer("Model 2-parametrowy (Monod i Scherrer 1965). Przykład: 400 W / 310 W.", W, H)
    svg("test-cp-model", W, H, b, "Model mocy krytycznej z testu 3 i 12 minut",
        "Z mocy 400 W w 3 minuty i 310 W w 12 minut wychodzi CP 280 W oraz W' 21,6 kJ – pole nad linią CP.")


# ================================================================ FATIGUE RESISTANCE
def fr_spadek():
    W, H = 1200, 660
    b = header("Po 2–2,5 h jazdy", "Ile mocy tracisz, gdy jesteś zmęczony", W)
    rows = [
        ("Próg tlenowy (VT1) po 2 h", "Stevenson i in. 2022", 10, None),
        ("5-min TT po 150 min – bez węglowodanów", "Dudley-Rode i in. 2024", 10, None),
        ("5-min TT po 150 min – z węglowodanami", "Dudley-Rode i in. 2024", 4, None),
        ("XCO po 140 min – słabsi zawodnicy", "Inoue i in. 2026", 17, None),
        ("XCO po 140 min – najlepsi zawodnicy", "Inoue i in. 2026", 6, None),
    ]
    x0, x1, y = 560, 1100, 150
    X = lambda v: x0 + (x1 - x0) * v / 20
    for v in (0, 5, 10, 15, 20):
        b += f'<line x1="{X(v)}" x2="{X(v)}" y1="{y-10}" y2="{y+5*78-20}" stroke="{LINE}" stroke-width="1.5"/>' + t(X(v), y + 5 * 78 + 8, f"−{v}%", 17, "t", MUTED, "middle")
    for i, (a, src, v, _) in enumerate(rows):
        yy = y + i * 78
        good = "z węglowodanami" in a or "najlepsi" in a
        b += t(56, yy + 22, a, 19, "t b") + t(56, yy + 46, src, 15, "t", MUTED)
        b += f'<rect x="{x0}" y="{yy+6}" width="{X(v)-x0}" height="38" rx="8" fill="{SUN if good else INK}"/>'
        b += t(X(v) + 12, yy + 33, f"−{v}%", 22, "h", SUN_DEEP if good else INK)
    b += footer("Wartości średnie z badań; indywidualnie różnice są duże – to właśnie jest „durability”.", W, H)
    svg("fatigue-resistance-spadek", W, H, b, "Spadek mocy po długiej jeździe",
        "Po 2–2,5 godziny jazdy moc na progu tlenowym i w 5-minutowej próbie spada o 4–17%; mniej u zawodników lepszych i przy jedzeniu węglowodanów.")


def fr_czynniki():
    W, H = 1200, 600
    b = header("Co decyduje o odporności na zmęczenie", "Fatigue resistance – od czego zależy", W)
    items = [
        ("Silnik tlenowy", "VO2max, CP i wysoki", "próg tlenowy"),
        ("Tłuszcze", "wysokie spalanie", "oszczędza glikogen"),
        ("Węglowodany", "60–90+ g/h od startu", "chronią próg i moc"),
        ("Ekonomia i siła", "mniejszy spadek", "sprawności i momentu"),
        ("Objętość", "długie jazdy", "z akcentami na końcu"),
    ]
    n = len(items); gap = 20; cw = (W - 112 - gap * (n - 1)) / n
    for i, (h, a, c) in enumerate(items):
        x = 56 + i * (cw + gap)
        b += f'<rect x="{x}" y="150" width="{cw}" height="260" rx="18" fill="{SAND}"/>'
        b += f'<circle cx="{x+40}" cy="196" r="22" fill="{INK}"/>' + t(x + 40, 204, str(i + 1), 22, "h", SUN, "middle")
        b += t(x + 22, 262, h, 24, "h") + t(x + 22, 300, a, 17, "t") + t(x + 22, 324, c, 17, "t", MUTED)
    b += (f'<rect x="56" y="440" width="{W-112}" height="70" rx="14" fill="{INK}"/>' +
          t(84, 484, "Mierz: moc 5–20 min po 1500–2500 kJ (lub 20–30 kJ/kg) i porównuj ze świeżą", 21, "t b", WHITE))
    b += footer("Maunder i in. 2021; Hunter i in. 2025; Mateo-March i in. 2026.", W, H)
    svg("fatigue-resistance-czynniki", W, H, b, "Czynniki odporności na zmęczenie",
        "Silnik tlenowy, spalanie tłuszczów, węglowodany w trakcie jazdy, ekonomia i siła oraz objętość treningu decydują o tym, ile mocy zostaje po wielu godzinach.")


if __name__ == "__main__":
    detrening(); minimalna_dawka(); sezon()
    wegle_na_godzine(); wegle_dziennie(); glukoza_fruktoza(); dzien_wyscigu(); piramida()
    heat_os_czasu(); ge_porownanie(); krzywa_mleczanowa(); cele_hierarchia()
    test_cp_protokol(); test_cp_model(); fr_spadek(); fr_czynniki()
