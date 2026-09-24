/* Sklep z planami: ankieta dopasowania (drzewko decyzyjne), wybór wariantu, płatność Stripe. */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  var dataEl = document.getElementById('shop-data');
  if (!dataEl) return;
  var SHOP = JSON.parse(dataEl.textContent);
  var cfg = window.KOM_CONFIG || {};
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  /* ---------- link do płatności ---------- */
  function buyUrl(slug, weeks, hours) {
    var link = (cfg.paymentLinks || {})[slug + '-' + weeks];
    var plan = SHOP.plans[slug];
    if (link) {
      var ref = (slug + '-' + weeks + 'w-' + hours + 'h').replace(/[^A-Za-z0-9_-]/g, '');
      return link + (link.indexOf('?') > -1 ? '&' : '?') + 'client_reference_id=' + encodeURIComponent(ref);
    }
    return '/kontakt/?temat=' + encodeURIComponent('Zakup planu: ' + plan.name + ' – ' + tyg(weeks) + ', ' + SHOP.hoursLabel[hours] + ' tygodniowo') + '#formularz';
  }
  function tyg(n) { n = +n; return n + (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? ' tygodnie' : n === 1 ? ' tydzień' : ' tygodni'); }
  function track(slug, weeks) {
    window.dataLayer && window.dataLayer.push({ event: 'begin_checkout', currency: 'PLN', value: SHOP.plans[slug].prices[weeks], items: [{ item_id: slug + '-' + weeks, item_name: SHOP.plans[slug].name }] });
  }

  /* ---------- strona produktu: warianty ---------- */
  var buy = $('#buy');
  if (buy) {
    var slug = buy.getAttribute('data-plan'), plan = SHOP.plans[slug];
    var q = new URLSearchParams(location.search);
    if (q.get('w')) { var rw = $('input[name=weeks][value="' + q.get('w') + '"]', buy); rw && (rw.checked = true); }
    if (q.get('h')) { var rh = $('input[name=hours][value="' + q.get('h') + '"]', buy); rh && (rh.checked = true); }
    var update = function () {
      var w = $('input[name=weeks]:checked', buy).value, h = $('input[name=hours]:checked', buy).value;
      $('#buy-price').innerHTML = plan.prices[w] + ' zł <small>jednorazowo</small>';
      $('#buy-summary').textContent = tyg(w) + ' · ' + SHOP.hoursLabel[h] + ' tygodniowo';
      $('#buy-btn').href = buyUrl(slug, w, h);
      var ph = $('#phases');
      if (ph && plan.phases[w]) ph.innerHTML = plan.phases[w].map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    };
    buy.addEventListener('change', update);
    $('#buy-btn').addEventListener('click', function () { track(slug, $('input[name=weeks]:checked', buy).value); });
    update();
  }

  /* ---------- katalog: filtry ---------- */
  $$('.chips .chip').forEach(function (c) {
    c.addEventListener('click', function () {
      $$('.chips .chip').forEach(function (x) { x.classList.toggle('on', x === c); });
      var f = c.getAttribute('data-filter');
      $$('#plan-grid .plan-card').forEach(function (card) { card.hidden = f !== 'all' && card.getAttribute('data-cat') !== f; });
    });
  });

  /* ---------- ankieta: drzewko decyzyjne ---------- */
  var quiz = $('#quiz'), startBtn = $('#quiz-start');
  if (!quiz || !startBtn) return;
  var body = $('#quiz-body'), bar = $('#quiz-bar'), stepEl = $('#quiz-step'), back = $('#quiz-back');
  var answers = {}, history = [];

  var Q = {
    goal: { q: 'Jaki jest Twój główny cel na najbliższe tygodnie?', opts: [
      ['start', 'Przygotowuję się do konkretnego startu', 'wyścig, maraton, Gran Fondo, ultra'],
      ['forma', 'Chcę poprawić formę', 'bez konkretnego startu w najbliższym czasie'],
      ['powrot', 'Wracam po przerwie albo zaczynam', 'kontuzja, choroba, dłuższa pauza lub pierwszy plan'],
      ['zima', 'Zima – trenuję głównie na trenażerze', 'krótkie, skuteczne jednostki indoor']],
      next: function (a) { return a === 'start' ? 'race' : a === 'forma' ? 'focus' : 'weeks'; } },
    race: { q: 'Jaki to start?', opts: [
      ['maraton-mtb', 'Maraton MTB / XC', 'mini, mega, giga'],
      ['wyscig-szosowy', 'Wyścig szosowy lub Gran Fondo', 'jazda w grupie, ataki, finisz'],
      ['gravel-ultra', 'Gravel, ultra, bikepacking', 'wiele godzin w siodle'],
      ['czasowka-triathlon', 'Jazda na czas lub triathlon', 'równa moc w pozycji aero'],
      ['podjazdy', 'Wyścig górski lub wyjazd w góry', 'długie podjazdy, przewyższenie']],
      next: function () { return 'heat'; } },
    heat: { q: 'Czy start odbędzie się w upale?', opts: [
      ['tak', 'Tak – spodziewam się 25°C i więcej', 'lato, ciepły kraj, obóz na południu'],
      ['nie', 'Nie albo nie wiem', '']],
      next: function () { return 'weeks'; } },
    focus: { q: 'Co chcesz poprawić najbardziej?', opts: [
      ['poprawa-ftp', 'Moc na długich wysiłkach', 'próg, FTP, długie podjazdy i ucieczki'],
      ['poprawa-vo2max', 'Moc na krótkich, mocnych akcjach', '2–8 min: strome podjazdy, ataki'],
      ['podjazdy', 'Podjazdy w górach', 'W/kg, pacing, siła na stromiznach'],
      ['baza-tlenowa', 'Wytrzymałość i baza', 'jeździć dłużej, równiej i ekonomiczniej']],
      next: function () { return 'weeks'; } },
    weeks: { q: function () { return answers.goal === 'start' ? 'Ile czasu zostało do startu?' : 'Jak długi blok treningowy chcesz?'; },
      opts: function () {
        return answers.goal === 'start'
          ? [['4', 'Mniej niż 5 tygodni', 'krótki blok specyficzny + taper'], ['8', '5–10 tygodni', 'najczęstszy wybór'], ['12', 'Ponad 10 tygodni', 'pełny cykl: baza → specyfika → taper']]
          : [['4', '4 tygodnie', 'szybki, konkretny bodziec'], ['8', '8 tygodni', 'polecane – dwa pełne bloki'], ['12', '12 tygodni', 'pełny cykl z największym progresem']];
      }, next: function () { return 'hours'; } },
    hours: { q: 'Ile godzin tygodniowo realnie możesz trenować?', opts: [
      ['4-6', '4–6 h', 'np. 3–4 treningi'], ['6-8', '6–8 h', 'np. 4–5 treningów'], ['8-10', '8–10 h', 'np. 5 treningów z długą jazdą'],
      ['10-12', '10–12 h', 'np. 5–6 treningów'], ['12+', 'Ponad 12 h', 'duża objętość']],
      next: function () { return 'exp'; } },
    exp: { q: 'Jak wygląda Twoje doświadczenie z treningiem?', opts: [
      ['nowy', 'To mój pierwszy plan', 'dotąd jeździłem/am „na czuja”'],
      ['sredni', 'Trenuję regularnie od kilku miesięcy', ''],
      ['zaawansowany', 'Trenuję z planem od lat, startuję', '']],
      next: function () { return 'lead'; } }
  };
  var ORDER_HINT = 7;

  var interacted = false;
  function render(key) {
    var node = Q[key];
    var qText = typeof node.q === 'function' ? node.q() : node.q;
    var opts = typeof node.opts === 'function' ? node.opts() : node.opts;
    var n = history.length + 1;
    stepEl.textContent = 'Pytanie ' + n;
    bar.style.width = Math.min(100, n / ORDER_HINT * 100) + '%';
    back.hidden = history.length === 0;
    body.innerHTML = '<h2 class="quiz__q">' + esc(qText) + '</h2><div class="quiz__opts">' + opts.map(function (o) {
      return '<button type="button" class="quiz__opt" data-v="' + esc(o[0]) + '"><b>' + esc(o[1]) + '</b>' + (o[2] ? '<small>' + esc(o[2]) + '</small>' : '') + '</button>';
    }).join('') + '</div>';
    $$('.quiz__opt', body).forEach(function (b) {
      b.addEventListener('click', function () {
        interacted = true;
        answers[key] = b.getAttribute('data-v');
        history.push(key);
        var nx = node.next(answers[key]);
        if (nx === 'lead') renderLead(recommend());
        else if (nx) render(nx);
        else result();
      });
    });
    if (interacted) { var first = $('.quiz__opt', body); first && first.focus({ preventScroll: true }); }
  }

  function recommend() {
    var notes = [], alts = [], addon = null;
    var slug = answers.goal === 'start' ? answers.race : answers.goal === 'forma' ? answers.focus : answers.goal === 'powrot' ? 'powrot-do-formy' : 'trenazer-zima';
    var weeks = answers.weeks || '8';
    var hours = answers.hours === '12+' ? '10-12' : (answers.hours || '6-8');
    var why = {
      'maraton-mtb': 'Specyfika maratonu MTB: zmienne tempo w terenie, moc na krótkich podjazdach i taper pod start.',
      'wyscig-szosowy': 'Wyścig szosowy wymaga odporności na zmęczenie i mocnej odpowiedzi na ataki – ten plan łączy jedno i drugie.',
      'gravel-ultra': 'Na długie dystanse liczy się durability, FatMax i żywienie w trakcie jazdy – na tym opiera się ten plan.',
      'czasowka-triathlon': 'Czasówka i rower w triathlonie to praca wokół progu i dobry pacing z modelu CP/W′.',
      'podjazdy': 'Podjazdy to próg, VO2max i siła na niskiej kadencji – plan łączy te trzy elementy.',
      'poprawa-ftp': 'Progresja sweet spot i pracy okołoprogowej to najskuteczniejsza droga do wyższego FTP.',
      'poprawa-vo2max': 'Interwały 30/15 i 4 × 4 min podnoszą pułap tlenowy i moc na 2–8 minut.',
      'baza-tlenowa': 'Solidna baza tlenowa to fundament – po niej każdy kolejny blok działa lepiej.',
      'powrot-do-formy': 'Stopniowy powrót z kontrolą obciążenia to najkrótsza droga do regularnego treningu bez kontuzji.',
      'trenazer-zima': 'Krótkie, strukturalne jednostki w trybie ERG budują formę zimą bez wychodzenia z domu.'
    }[slug];
    if (answers.exp === 'nowy' && (slug === 'poprawa-vo2max' || slug === 'podjazdy')) {
      alts.push(slug); slug = 'baza-tlenowa';
      why = 'Przy pierwszym planie najwięcej zyskasz na bazie tlenowej – bloki VO2max i podjazdowe dadzą więcej, gdy będziesz mieć już fundament.';
    }
    if (answers.exp === 'nowy' && answers.goal === 'start' && weeks === '4') notes.push('Przy pierwszym planie 4 tygodnie do startu to mało – plan skupi się na świeżości w dniu startu, a nie na dużym skoku formy.');
    if (answers.goal === 'start' && weeks === '12' && slug !== 'gravel-ultra') notes.push('Przy 12 tygodniach plan zaczyna się od bazy i siły, a specyfika startowa przychodzi w drugiej połowie.');
    if (answers.hours === '4-6' && slug === 'gravel-ultra') notes.push('Na dystanse ultra 4–6 h tygodniowo to minimum – jeśli możesz, dołóż jedną dłuższą jazdę w weekend.');
    if (answers.hours === '12+') notes.push('Przy ponad 12 h tygodniowo najlepiej sprawdzi się indywidualna opieka trenerska – plan dopasowany co tydzień do Twojej objętości. Gotowy plan wybrałem w wariancie 10–12 h.');
    if (answers.heat === 'tak') {
      if (weeks === '4') notes.push('Start w upale za mniej niż 5 tygodni: na pełny protokół heat jest za mało czasu, ale 5–10 dni aklimatyzacji wciąż sporo daje – zobacz protokół „Heat Blitz” w KOMpedium.');
      else addon = 'protokol-heat';
    }
    if (slug === 'poprawa-ftp') alts.push('poprawa-vo2max');
    if (slug === 'poprawa-vo2max') alts.push('poprawa-ftp');
    if (slug === 'trenazer-zima') alts.push('baza-tlenowa');
    if (slug === 'powrot-do-formy') alts.push('baza-tlenowa');
    if (answers.goal === 'start' && slug !== 'podjazdy') alts.push('podjazdy');
    alts = alts.filter(function (a, i) { return a !== slug && alts.indexOf(a) === i; }).slice(0, 2);
    return { slug: slug, weeks: weeks, hours: hours, why: why, notes: notes, alts: alts, addon: addon };
  }

  function renderLead(r) {
    var p = SHOP.plans[r.slug];
    stepEl.textContent = 'Ostatni krok'; bar.style.width = Math.min(100, (history.length + 1) / ORDER_HINT * 100) + '%'; back.hidden = false;
    body.innerHTML = '<h2 class="quiz__q">Ostatni krok — dokąd wysłać Twój plan?</h2>' +
      '<p class="muted">Na podstawie Twoich odpowiedzi dobrałem konkretny plan. Podaj e-mail, a pokażę Ci go od razu i dodatkowo wyślę na skrzynkę.</p>' +
      '<form class="form" data-form="newsletter" action="/api/newsletter.php" method="post" novalidate>' +
      '<input type="hidden" name="plan" value="' + esc(p.name + ' – ' + tyg(r.weeks) + ' / ' + SHOP.hoursLabel[r.hours]) + '">' +
      '<div class="row"><div class="field"><label for="quiz-imie">Imię</label><input id="quiz-imie" name="imie" type="text" autocomplete="given-name"></div>' +
      '<div class="field"><label for="quiz-email">E-mail *</label><input id="quiz-email" name="email" type="email" autocomplete="email" required></div></div>' +
      '<label class="consent"><input type="checkbox" name="zgoda" value="1" required><span>Chcę dostać ten plan i newsletter KOMpetition.cc na e-mail. Zgodę mogę wycofać w każdej chwili. Administratorem danych jest Jakub Obitko – szczegóły w <a href="/polityka-prywatnosci/">polityce prywatności</a>.</span></label>' +
      '<div class="hp" aria-hidden="true"><label>Strona www<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>' +
      '<div><button class="btn btn--sun" type="submit">Pokaż mi mój plan</button></div><p class="form-status" role="status" aria-live="polite"></p></form>';
    var form = $('form', body);
    if (window.KOM_bindForm) window.KOM_bindForm(form);
    form.addEventListener('submit', function () {
      if (!form.checkValidity()) return;
      history.push('lead');
      result(r);
    });
    if (interacted) { var first = $('#quiz-imie', body); first && first.focus({ preventScroll: true }); }
  }

  function result(r) {
    r = r || recommend();
    var p = SHOP.plans[r.slug];
    bar.style.width = '100%'; stepEl.textContent = 'Twój plan'; back.hidden = false;
    var detail = p.url + '?w=' + r.weeks + '&h=' + r.hours;
    var html = '<div class="quiz__result"><p class="eyebrow">Polecam Ci</p>' +
      '<img class="quiz__cover" src="' + esc(p.cover) + '" alt="" width="1200" height="750">' +
      '<h2 class="quiz__q">' + esc(p.name) + '</h2>' +
      '<p class="quiz__variant"><b>' + tyg(r.weeks) + '</b> · <b>' + SHOP.hoursLabel[r.hours] + '</b> tygodniowo · <b class="quiz__price">' + p.prices[r.weeks] + ' zł</b></p>' +
      '<p>' + esc(r.why) + '</p>' + r.notes.map(function (n) { return '<p class="note">' + esc(n) + '</p>'; }).join('') +
      '<div class="btn-row"><a class="btn btn--sun" id="quiz-buy" href="' + esc(buyUrl(r.slug, r.weeks, r.hours)) + '">Kup ten wariant ' + ARROW + '</a><a class="btn btn--ghost" href="' + esc(detail) + '">Zobacz szczegóły</a></div>';
    if (r.addon) {
      var hp = SHOP.plans[r.addon];
      html += '<div class="quiz__addon"><b>Start w upale?</b> Dołóż <a href="' + hp.url + '?h=' + r.hours + '">' + esc(hp.name) + '</a> – 5 tygodni, ' + hp.prices['5'] + ' zł. Najlepiej zacząć go 5 tygodni przed startem, równolegle z planem.</div>';
    }
    if (r.alts.length) html += '<p class="quiz__alts">Warto też rozważyć: ' + r.alts.map(function (a) { return '<a href="' + SHOP.plans[a].url + '?w=' + r.weeks + '&h=' + r.hours + '">' + esc(SHOP.plans[a].name) + '</a>'; }).join(' · ') + '</p>';
    html += '<p class="quiz__alts"><button type="button" class="link-arrow" id="quiz-restart">Zacznij od nowa</button> · <a href="#katalog">Przeglądaj wszystkie plany</a></p></div>';
    body.innerHTML = html;
    $('#quiz-buy').addEventListener('click', function () { track(r.slug, r.weeks); });
    $('#quiz-restart').addEventListener('click', function () { start(true); });
    window.dataLayer && window.dataLayer.push({ event: 'quiz_complete', plan: r.slug, weeks: r.weeks, hours: r.hours });
  }

  function start(scroll) {
    answers = {}; history = [];
    render('goal');
    if (scroll) { interacted = true; quiz.scrollIntoView({ behavior: 'smooth', block: 'center' }); var f = $('.quiz__opt', body); f && f.focus({ preventScroll: true }); }
  }
  back.addEventListener('click', function () {
    if (!history.length) return;
    var prev = history.pop(); delete answers[prev];
    prev === 'lead' ? renderLead(recommend()) : render(prev);
  });
  startBtn.addEventListener('click', function () { start(true); });
  start(location.hash === '#quiz-start');
});
