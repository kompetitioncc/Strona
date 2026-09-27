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


if __name__ == "__main__":
    detrening(); minimalna_dawka(); sezon()
    wegle_na_godzine(); wegle_dziennie(); glukoza_fruktoza(); dzien_wyscigu(); piramida()
