// Model raportu „Profil mocy” KOMpetition (kalkulator CP).
// Wejście: płeć, wiek, masa, tkanka tłuszczowa, średnia moc z 3 i 12 min (all-out), opcjonalnie PR z 12 s.
// Wspólny dla strony (cp-kalkulator/kalkulator.html) i Workera (mail z raportem), żeby liczby w mailu
// były dokładnie takie jak na ekranie i nie pochodziły z formularza.
//
// Założenia (szacunki, nie pomiar laboratoryjny):
//  • CP i W' – model 2-parametrowy praca–czas (Monod i Scherrer 1965; Vanhatalo i in. 2011) z testów 3 i 12 min.
//  • VO2max – równanie dla kolarzy szosowych z mocy 5-min: 16,6 + 8,87·W/kg (Sitko i in. 2021, IJSPP).
//    Wykorzystanie VO2max na CP – koszt tlenowy mocy wg ACSM (10,8 ml/min na W + 7 ml/kg/min).
//  • 60 min („FTP”) – moc 20-min z modelu × współczynnik zależny od poziomu (Sitko i in. 2023: 0,88–0,96).
//    CP z krótkich testów bywa wyżej niż MLSS/FTP o ok. 3–8% (Karsten i in. 2021; Mattioni Maturana i in. 2017).
//  • VLaMax – wskaźnik pośredni, głównie ze stosunku sprintu 12 s do CP (VLaMax testuje się sprintem 10–15 s);
//    bez sprintu tylko z W' na kg masy beztłuszczowej (mniej pewnie).
//  • Włókna – CP koreluje z udziałem typu I, a W' nie ma związku z typem włókien (Vanhatalo i in. 2016),
//    więc szacunek opiera się na wykorzystaniu VO2max na CP i stosunku sprintu do CP.
//  • FatMax i spalanie – krzywa utleniania tłuszczów wokół FatMax (Achten i Jeukendrup 2003), sprawność brutto 22%.

const r = Math.round;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const num = (v) => { const n = parseFloat(String(v ?? '').replace(',', '.')); return Number.isFinite(n) ? n : NaN; };
export const pl = (x, d = 0) => Number(x).toFixed(d).replace('.', ',');

const SCALES = {
  male: { cp: [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.5], sprint: [9.5, 11.0, 12.5, 14.0, 15.5, 17.5, 20.5] },
  female: { cp: [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0], sprint: [7.5, 9.0, 10.5, 12.0, 13.5, 15.0, 17.5] }
};
const RANKS = ['Rekreacja', 'Amator', 'Amator+', 'Cat 3', 'Cat 2', 'Cat 1', 'Elita'];

function rank(val, type, gender) {
  const sc = SCALES[gender][type];
  const min = sc[0] - 0.5, max = sc[sc.length - 1];
  let label = RANKS[0];
  for (let i = 0; i < sc.length; i++) if (val >= sc[i]) label = RANKS[i];
  return { pct: clamp(((val - min) / (max - min)) * 100, 0, 100), label };
}

export const PLANS = {
  'poprawa-vo2max': { name: 'Poprawa VO2max', url: '/plany-treningowe/poprawa-vo2max/', cover: '/assets/img/plan-poprawa-vo2max-og-1200.webp' },
  'poprawa-ftp': { name: 'Poprawa FTP', url: '/plany-treningowe/poprawa-ftp/', cover: '/assets/img/plan-poprawa-ftp-og-1200.webp' },
  'baza-tlenowa': { name: 'Baza tlenowa', url: '/plany-treningowe/baza-tlenowa/', cover: '/assets/img/plan-baza-tlenowa-3-og-1200.webp' },
  'powrot-do-formy': { name: 'Powrót do formy', url: '/plany-treningowe/powrot-do-formy/', cover: '/assets/img/plan-powrot-do-formy-og-1200.webp' }
};

// inp: { gender, age, weight, bf, p3, p12, sprint } – moce w W, sprint opcjonalny (PR z 12 s)
export function cpModel(inp) {
  const gender = inp.gender === 'female' ? 'female' : 'male';
  const F = gender === 'female';
  const age = num(inp.age), m = num(inp.weight), bfIn = num(inp.bf);
  const p3 = num(inp.p3), p12 = num(inp.p12);
  const sprint = num(inp.sprint) > 0 ? num(inp.sprint) : 0;

  if (!(age >= 12 && age <= 90)) return { error: 'Podaj wiek (12–90 lat).' };
  if (!(m >= 35 && m <= 160)) return { error: 'Podaj masę ciała w kg (35–160).' };
  if (!(bfIn >= 3 && bfIn <= 50)) return { error: 'Podaj tkankę tłuszczową w % (3–50). Jeśli nie znasz, wpisz szacunek: mężczyźni zwykle 12–18%, kobiety 20–26%.' };
  if (!(p3 > 0) || !(p12 > 0)) return { error: 'Podaj średnią moc z 3 i 12 minut.' };
  if (p3 <= p12) return { error: 'Moc z 3 minut musi być wyższa niż z 12 minut.' };
  if (p3 > 1000 || p12 > 700) return { error: 'Sprawdź moce – wyglądają na zbyt wysokie dla wysiłku 3 i 12 minut.' };
  if (sprint && sprint <= p3) return { error: 'PR z 12 s musi być wyższy niż moc z 3 minut (albo zostaw to pole puste).' };

  const bf = bfIn;
  const ffm = m * (1 - bf / 100);                          // beztłuszczowa masa ciała

  // CP i W' (praca = CP·t + W'); t = 180 s i 720 s
  const cp = (p12 * 720 - p3 * 180) / 540;
  const wJ = (p3 - cp) * 180;
  const wk = wJ / 1000;
  if (!(cp > 0)) return { error: 'Te dwie moce nie układają się w model CP – sprawdź, czy to średnie z pełnych, maksymalnych wysiłków.' };

  const cpKg = cp / m, cpFfm = cp / ffm;
  const wKg = wJ / m, wFfm = wJ / ffm;                    // J/kg
  const ageFactor = age > 35 ? 1 - 0.008 * (age - 35) : 1; // ~0,8%/rok spadku po 35 r.ż.
  const cpKgAge = cpKg / ageFactor;

  // Krzywa mocy z modelu (2–20 min wiarygodnie; 60 min ≈ 0,92·CP)
  const pAt = (t) => cp + wJ / t;
  const p5 = pAt(300), p20 = pAt(1200);

  // VO2max (Sitko 2021) i wykorzystanie pułapu na CP (koszt tlenowy wg ACSM)
  const vo2 = 16.6 + 8.87 * (p5 / m);
  const util = Math.min(95, (((10.8 * cp) / m + 7) / vo2) * 100);

  // 60 min: P20 × współczynnik poziomu (Sitko 2023; poziom wg VO2max)
  const k60 = vo2 < 50 ? 0.88 : vo2 < 60 ? 0.92 : vo2 < 70 ? 0.95 : 0.96;
  const ftp = Math.min(p20 * k60, cp);
  const curve = [
    { t: '1 min', w: sprint ? Math.min(pAt(60), sprint * 0.75) : pAt(60), note: 'orientacyjnie' },
    { t: '5 min', w: p5 },
    { t: '8 min', w: pAt(480) },
    { t: '20 min', w: pAt(1200) },
    { t: '60 min', w: ftp, note: 'szac. FTP' }
  ].map((x) => ({ ...x, w: r(x.w), wkg: x.w / m }));

  // VLaMax (mmol/l/s) – wskaźnik pośredni
  const vlaW = 0.002 * wFfm - 0.10;
  const ratio = sprint ? sprint / cp : 0;
  const vlaS = ratio ? 0.14 * ratio - 0.12 : 0;
  const vla = clamp(ratio ? 0.75 * vlaS + 0.25 * vlaW : vlaW, 0.2, 1.0);
  const vlaSure = Boolean(ratio);
  const vlaLabel = vla < 0.35 ? 'Niski' : vla < 0.55 ? 'Umiarkowany' : vla < 0.75 ? 'Wysoki' : 'Bardzo wysoki';

  // Udział włókien typu I (szacunek): wyżej przy wysokim wykorzystaniu VO2max na CP, niżej przy mocnym sprincie
  const type1 = r(clamp(55 + (util - 80) * 1.2 - (ratio ? (ratio - 3.5) * 8 : 0) + (F ? 2 : 0), 30, 80));
  const type1Range = ratio ? 8 : 12;

  // FatMax i spalanie
  const fmPct = clamp(0.66 + (vo2 - 55) * 0.004 - (vla - 0.45) * 0.25 + (F ? 0.02 : 0), 0.52, 0.80);
  const fatMax = cp * fmPct;
  const mfo = clamp(0.10 + 0.0065 * vo2 - (vla - 0.45) * 0.3 + (F ? 0.03 : 0), 0.2, 1.0);  // g/min
  const fatAt = (x) => {                                   // x = moc/CP → g/min tłuszczu
    if (x <= fmPct) return mfo * Math.max(0.45, 1 - ((fmPct - x) / fmPct) ** 2 * 1.6);
    return mfo * Math.max(0, 1 - ((x - fmPct) / (1.02 - fmPct)) ** 2);
  };
  const fuel = [
    { n: 'Spokojnie (Z2)', x: 0.65 }, { n: 'Tempo', x: 0.80 }, { n: 'Sweet spot', x: 0.90 }, { n: 'CP (próg)', x: 1.0 }
  ].map(({ n, x }) => {
    const w = cp * x;
    const kcal = (w * 3600) / (0.22 * 4184);
    const fatG = fatAt(x) * 60;
    const choG = Math.max(0, (kcal - fatG * 9.4) / 4.1);
    return { n, pct: r(x * 100), w: r(w), kcal: r(kcal), fat: r(fatG), cho: r(choG), choPct: r((choG * 4.1 / kcal) * 100) };
  });

  // Rangi
  const cpRank = rank(cpKg, 'cp', gender);
  const sprintRank = sprint ? rank(sprint / m, 'sprint', gender) : null;
  const wLo = F ? 190 : 220, wHi = F ? 310 : 360;          // J/kg masy ciała (W' z testu 3/12 min)
  const wLabel = wKg < wLo ? 'Niska' : wKg < wHi ? 'Średnia' : wKg < wHi + 60 ? 'Wysoka' : 'Bardzo wysoka';
  const wPct = clamp(100 / 3 + ((wKg - wLo) / (wHi - wLo)) * (100 / 3), 2, 98);   // wLo → 1/3 skali, wHi → 2/3

  // Fenotyp
  const climbKg = F ? 3.7 : 4.3, bigCp = F ? 240 : 300;
  let type, typeDesc;
  if (ratio >= 4.6 || wKg > wHi + 60) {
    type = 'Sprinter'; typeDesc = 'Duża moc beztlenowa i wysoka glikoliza. Wygrywasz krótkie, eksplozywne akcje, ale płacisz za nie na długich podjazdach.';
  } else if (cpKg >= climbKg && wKg < wHi) {
    type = 'Góral'; typeDesc = 'Wysoka moc względna na progu przy umiarkowanym W\'. Najlepiej czujesz się na długich podjazdach w równym tempie.';
  } else if (wKg >= wHi - 20 && cpKg >= (F ? 3.2 : 3.7)) {
    type = 'Puncher'; typeDesc = 'Mocny próg i spory „bak” W\'. Idealny profil na krótkie, strome podjazdy i ataki z grupy.';
  } else if (cp >= bigCp && wKg < wHi) {
    type = 'Czasowiec / rouleur'; typeDesc = 'Wysoka moc absolutna na progu. Twoje tereny to płaskie odcinki, czasówki i praca na czele grupy.';
  } else if (wKg < wLo) {
    type = 'Diesel'; typeDesc = 'Silnik tlenowy z małym zapasem beztlenowym. Jedziesz równo i długo, trudniej Ci odpowiadać na zrywy.';
  } else {
    type = 'Wszechstronny'; typeDesc = 'Zbalansowany profil bez wyraźnej słabej strony – dobra baza, żeby celować w konkretny typ wyścigu.';
  }

  // Mocne strony i ograniczniki
  const strengths = [], limiters = [];
  if (util >= 85) strengths.push(`Wysokie wykorzystanie pułapu tlenowego na progu (${r(util)}% VO2max).`);
  if (util < 78) limiters.push(`Próg (CP) leży nisko względem VO2max (${r(util)}%) – masz „sufit”, którego nie wykorzystujesz.`);
  if (util >= 87) limiters.push(`Próg jest już blisko sufitu (${r(util)}% VO2max) – dalszy wzrost CP wymaga podniesienia VO2max.`);
  if (vo2 >= (F ? 55 : 62)) strengths.push(`Wysokie szacowane VO2max (${r(vo2)} ml/kg/min).`);
  else if (vo2 < (F ? 42 : 48)) limiters.push(`Pułap tlenowy (VO2max ≈ ${r(vo2)} ml/kg/min) ogranicza wszystko powyżej progu.`);
  if (wKg >= wHi - 30) strengths.push(`Duży zapas beztlenowy: W' ${pl(wk, 1)} kJ – starczy na kilka mocnych akcji.`);
  if (wKg < wLo) limiters.push(`Mały zapas beztlenowy (W' ${pl(wk, 1)} kJ) – ataki i finisze szybko Cię „odcinają”.`);
  if (vla >= 0.65) limiters.push(`Wysoki VLaMax (≈ ${pl(vla, 2)}) podnosi zużycie węglowodanów i obniża FatMax na długich dystansach.`);
  if (vla <= 0.35) strengths.push(`Niski VLaMax (≈ ${pl(vla, 2)}) – oszczędna gospodarka węglowodanami na długich dystansach.`);
  if (cpKg >= climbKg) strengths.push(`Bardzo dobra moc względna na progu: ${pl(cpKg, 2)} W/kg.`);
  if (sprintRank && sprint / m >= (F ? 13.5 : 15.5)) strengths.push(`Mocny sprint: ${r(sprint)} W (${pl(sprint / m, 1)} W/kg).`);
  if (util >= 78 && util < 85) strengths.push(`Zbalansowane wykorzystanie pułapu (${r(util)}% VO2max) – możesz podnosić i próg, i VO2max.`);
  if (vla > 0.35 && vla < 0.6) strengths.push(`Umiarkowany VLaMax (≈ ${pl(vla, 2)}) – dobry kompromis między dynamiką a ekonomią.`);
  if (cpKg < climbKg && RANKS.indexOf(cpRank.label) >= 3) strengths.push(`Próg na poziomie ${cpRank.label}: ${pl(cpKg, 2)} W/kg.`);
  if (vo2 >= (F ? 42 : 48) && vo2 < (F ? 52 : 60) && util < 85) limiters.push(`VO2max ≈ ${r(vo2)} ml/kg/min – podniesienie pułapu otworzy drogę do wyższego CP.`);
  if (sprintRank && RANKS.indexOf(sprintRank.label) <= 2) limiters.push(`Sprint ${r(sprint)} W (${pl(sprint / m, 1)} W/kg) – dynamika do rozwinięcia, np. krótkie sprinty i siłownia.`);
  if (bf > (F ? 24 : 18)) limiters.push(`Tkanka tłuszczowa ${pl(bf, 0)}% – rezerwa W/kg na podjazdach (patrz: skład ciała).`);
  if (!strengths.length) strengths.push('Równy profil – żaden parametr nie odstaje w dół.');
  if (!limiters.length) limiters.push('Brak wyraźnego ogranicznika – kluczem jest systematyczna progresja obciążeń.');

  // Priorytet, sesje i plan
  const W = (x) => `${r(x)} W`;
  const vo2Rep = cp + (wJ * 0.6) / 240;
  let focus, sessions, recSlug, recWhy;
  if (cpKg < (F ? 2.0 : 2.5)) {
    focus = 'Zbuduj regularność i bazę tlenową – na tym etapie każdy tydzień konsekwentnego treningu podnosi CP.';
    sessions = [
      ['Baza Z2', `2–3× w tygodniu 60–120 min przy ${W(cp * 0.60)}–${W(cp * 0.72)}.`],
      ['Tempo', `2×15 min przy ${W(cp * 0.80)}–${W(cp * 0.85)}.`],
      ['Siła', 'Siłownia 2× w tygodniu: przysiad, martwy ciąg, wykroki.']
    ];
    recSlug = 'powrot-do-formy'; recWhy = 'Plan, który bezpiecznie buduje regularność i bazę, zanim dołożysz mocne interwały.';
  } else if (util >= 85) {
    focus = 'Podnieś sufit, czyli VO2max. Twój próg jest już wysoko względem pułapu tlenowego – dalszy wzrost CP przyjdzie z „góry”.';
    sessions = [
      ['VO2max 5×4 min', `${W(vo2Rep)}, przerwy 4 min spokojnie.`],
      ['30/15 · 3×13', `30 s mocno (${W(cp * 1.15)}–${W(cp * 1.25)}, tyle, ile utrzymasz we wszystkich), 15 s luzu (Rønnestad).`],
      ['Długa Z2', `2–4 h przy ${W(fatMax * 0.95)}–${W(fatMax * 1.05)} (FatMax).`]
    ];
    recSlug = 'poprawa-vo2max'; recWhy = `Twój próg wykorzystuje już ${r(util)}% VO2max. Najwięcej zyskasz, podnosząc pułap – moc na 3–8 minut.`;
  } else if (vla >= 0.62) {
    focus = 'Obniż VLaMax i podnieś FatMax: więcej objętości w Z2 i tempie, mniej przypadkowej intensywności.';
    sessions = [
      ['Długa Z2', `3–4 h przy ${W(fatMax * 0.95)}–${W(fatMax * 1.05)}.`],
      ['Tempo niska kadencja', `3×20 min przy ${W(cp * 0.82)}, 60–70 rpm.`],
      ['Sweet spot', `3×15 min przy ${W(cp * 0.88)}–${W(cp * 0.93)}.`]
    ];
    recSlug = 'baza-tlenowa'; recWhy = `Twój szacowany VLaMax (≈ ${pl(vla, 2)}) jest wysoki. Mocna baza tlenowa obniży zużycie węglowodanów i podniesie próg.`;
  } else {
    focus = 'Podnieś próg (CP): masz jeszcze zapas między CP a VO2max, który przełożysz na dłuższą, wyższą moc.';
    sessions = [
      ['Próg 3×15 min', `${W(cp * 0.93)}–${W(cp * 0.98)}, przerwy 5 min.`],
      ['Over-under 3×12 min', `2 min ${W(cp * 0.92)} / 1 min ${W(cp * 1.08)}.`],
      ['Długa Z2', `2–4 h przy ${W(fatMax * 0.95)}–${W(fatMax * 1.05)}.`]
    ];
    recSlug = 'poprawa-ftp'; recWhy = `Masz zapas między progiem a pułapem (${r(util)}% VO2max). Plan progresji progu przełoży go na wyższe CP.`;
  }
  if (wKg < wLo && recSlug !== 'powrot-do-formy') sessions.push(['Dynamika', `6–8 × 12 s sprint + 1–2 serie 6×1 min przy ${W(pAt(60) * 0.95)}.`]);
  if (age >= 40) sessions.push(['Siła (masters)', 'Siłownia 2× w tygodniu, ciężko i krótko – chroni włókna szybkokurczliwe i moc sprintu.']);

  // Skład ciała
  const bfTarget = F ? 20 : 13;
  let body = null;
  if (bf > bfTarget + 2) {
    const leanTo = ffm / (1 - bfTarget / 100);
    body = { targetBf: bfTarget, mass: leanTo, lose: m - leanTo, cpKg: cp / leanTo };
  }

  // Jakość danych
  const warnings = [];
  if (wk > 35) warnings.push('W\' wychodzi bardzo wysokie – możliwe, że 12 minut nie było jechane na maksa albo 3 minuty były z „rozbiegu”.');
  if (wk < 6) warnings.push('W\' wychodzi bardzo niskie – możliwe, że 3 minuty nie były jechane na maksa. Test powtórzony wypoczętym da pewniejszy wynik.');

  return {
    gender, age, weight: m, bf, ffm, p3, p12, sprint,
    cp, wJ, wk, cpKg, cpFfm, wKg, wFfm, cpKgAge, ageFactor, ftp, curve,
    p5, p20, k60, vo2, util, vla, vlaLabel, vlaSure, ratio, type1, type1Range,
    fmPct, fatMax, mfo, fuel,
    cpRank, sprintRank, wLabel, wPct,
    type, typeDesc, strengths, limiters, focus, sessions, body, warnings,
    rec: { slug: recSlug, why: recWhy, weeks: '8', hours: '6-8', ...PLANS[recSlug] }
  };
}
