(function () {
  'use strict';
  var cfg = window.KOM_CONFIG || {};
  var doc = document, body = doc.body;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  /* Menu mobilne */
  var burger = $('.burger');
  var closeNav = function () { body.classList.remove('nav-open'); burger && burger.setAttribute('aria-expanded', 'false'); };
  if (burger) {
    burger.addEventListener('click', function () {
      var open = body.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
    });
    $$('.nav a').forEach(function (a) { a.addEventListener('click', closeNav); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });
    window.matchMedia('(min-width:1081px)').addEventListener('change', function (m) { if (m.matches) closeNav(); });
  }

  /* Nagłówek i mobilny pasek CTA zależne od przewinięcia */
  var hdr = $('.hdr'), mcta = $('.mcta'), ticking = false;
  var onScroll = function () {
    var y = window.scrollY;
    hdr && hdr.classList.toggle('is-scrolled', y > 24);
    if (mcta) {
      var nearEnd = window.innerHeight + y > doc.documentElement.scrollHeight - 520;
      mcta.classList.toggle('show', y > window.innerHeight * 0.6 && !nearEnd);
    }
    ticking = false;
  };
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* Wideo w tle — pauza przy ograniczonym ruchu / oszczędzaniu danych i poza ekranem */
  var vid = $('video[data-bg]');
  if (vid) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var save = navigator.connection && navigator.connection.saveData;
    if (reduce || save) { vid.removeAttribute('autoplay'); vid.pause(); }
    else if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        en.forEach(function (e) { e.isIntersecting ? vid.play().catch(function () {}) : vid.pause(); });
      }).observe(vid);
    }
  }

  /* Animacje pojawiania się */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(function (el) { io.observe(el); });
  } else { $$('.rv').forEach(function (el) { el.classList.add('in'); }); }

  /* Spis treści: podświetlanie bieżącej sekcji */
  var tocLinks = $$('.toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var tio = new IntersectionObserver(function (en) {
      en.forEach(function (e) {
        if (e.isIntersecting) { tocLinks.forEach(function (a) { a.classList.remove('on'); }); map[e.target.id] && map[e.target.id].classList.add('on'); }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var h = doc.getElementById(id); h && tio.observe(h); });
    if (window.matchMedia('(max-width:1040px)').matches) { var d = $('.toc details'); d && d.removeAttribute('open'); }
  }

  /* Osadzenia ładowane po kliknięciu (Kalendarz Google) */
  $$('[data-embed]').forEach(function (box) {
    var b = $('button', box);
    b && b.addEventListener('click', function () {
      var f = doc.createElement('iframe');
      f.src = box.getAttribute('data-embed');
      f.className = 'embed-frame';
      f.title = box.getAttribute('data-title') || 'Osadzona treść';
      box.replaceWith(f);
    });
  });

  /* Kalkulator w iframe: dopasowanie wysokości */
  $$('iframe.calc-frame').forEach(function (f) {
    var fit = function () { try { f.style.height = f.contentWindow.document.documentElement.scrollHeight + 'px'; } catch (e) {} };
    f.addEventListener('load', function () {
      fit();
      try { new ResizeObserver(fit).observe(f.contentWindow.document.body); } catch (e) { setInterval(fit, 1000); }
    });
  });

  /* Linki płatności */
  $$('[data-buy]').forEach(function (a) {
    var link = (cfg.paymentLinks || {})[a.getAttribute('data-buy')];
    if (link) { a.href = link; a.rel = 'noopener'; }
  });

  /* Wstępne uzupełnienie formularza (?temat= / ?plan=) */
  var params = new URLSearchParams(location.search);
  var topic = params.get('temat') || (params.get('plan') ? 'Chcę kupić plan: ' + params.get('plan') : '');
  if (topic) { var ta = $('form[data-form="contact"] textarea'); if (ta && !ta.value) ta.value = topic + '\n\n'; }

  /* Statystyki (Google Tag Manager) — dopiero po zgodzie */
  if (cfg.gtmId) {
    var KEY = 'kom-analytics-consent';
    var get = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
    var set = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };
    var loadGTM = function () {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
      var s = doc.createElement('script'); s.async = true;
      s.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(cfg.gtmId);
      doc.head.appendChild(s);
    };
    var c = get();
    if (c === 'yes') loadGTM();
    else if (c !== 'no') {
      var bar = doc.createElement('div');
      bar.className = 'consent-bar'; bar.setAttribute('role', 'dialog'); bar.setAttribute('aria-label', 'Zgoda na statystyki');
      bar.innerHTML = '<p>Korzystam z Google Analytics, żeby wiedzieć, które treści są przydatne. Włączę statystyki tylko za Twoją zgodą. <a href="/polityka-prywatnosci/">Więcej</a></p><div><button class="btn btn--ghost btn--sm" type="button" data-c="no">Odrzuć</button><button class="btn btn--sm" type="button" data-c="yes">Akceptuję</button></div>';
      bar.addEventListener('click', function (e) {
        var v = e.target.getAttribute && e.target.getAttribute('data-c'); if (!v) return;
        set(v); bar.remove(); if (v === 'yes') loadGTM();
      });
      body.appendChild(bar);
    }
  }

  /* Formularze */
  function bindForm(form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var status = $('.form-status', form), btn = $('[type=submit]', form);
      var type = form.getAttribute('data-form');
      var endpoint = type === 'newsletter' ? cfg.newsletterEndpoint : cfg.contactEndpoint;
      var data = new FormData(form); data.append('page', location.pathname);
      var say = function (m, ok) { if (status) { status.textContent = m; status.className = 'form-status ' + (ok ? 'ok' : 'err'); } };
      btn && (btn.disabled = true); say('Wysyłanie…', true);
      var done = function () {
        form.reset();
        if (type === 'newsletter') { try { localStorage.setItem('kom-nl', 'subscribed'); } catch (e2) {} var pop = form.closest('.nl-pop'); pop && setTimeout(function () { pop.classList.remove('show'); setTimeout(function () { pop.remove(); }, 300); }, 2200); }
        say(type === 'newsletter' ? 'Dziękuję! Jesteś na liście.' : 'Dziękuję! Wiadomość wysłana — odezwę się najszybciej, jak to możliwe.', true);
        window.dataLayer && window.dataLayer.push({ event: type === 'newsletter' ? 'sign_up' : 'generate_lead' });
      };
      // 2. ścieżka zapasowa: przekazanie na e-mail przez FormSubmit (działa także bez PHP)
      var relay = function () {
        if (!cfg.relay || !cfg.email) return Promise.reject(new Error('send-failed'));
        var payload = type === 'newsletter'
          ? { _subject: data.get('plan') ? 'Nowy lead z ankiety doboru planu – KOMpetition.cc' : 'Nowy zapis do newslettera – KOMpetition.cc', email: data.get('email') || '', imie: data.get('imie') || '', plan: data.get('plan') || '' }
          : { _subject: 'Wiadomość ze strony KOMpetition.cc', imie: data.get('imie') || '', nazwisko: data.get('nazwisko') || '', email: data.get('email') || '', wiadomosc: data.get('wiadomosc') || '' };
        payload._replyto = data.get('email') || ''; payload._template = 'table'; payload._captcha = 'false';
        payload._honey = data.get('website') || ''; payload.strona = location.pathname;
        if (data.get('zgoda')) payload.zgoda = 'tak – ' + new Date().toISOString();
        return fetch('https://formsubmit.co/ajax/' + encodeURIComponent(cfg.email), { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) })
          .then(function (r) { return r.json(); })
          .then(function (j) { if (String(j.success) !== 'true') throw new Error('send-failed'); });
      };
      // 1. własny skrypt PHP na serwerze
      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return null; }).then(function (j) { return { ok: r.ok, status: r.status, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j && res.j.ok !== false) return done();
          // błąd walidacji z naszego skryptu (np. zły e-mail) – pokaż go, nie przekierowuj
          if (res.j && res.j.error && (res.status === 422 || res.status === 429)) { var ve = new Error(res.j.error); ve.validation = true; throw ve; }
          return relay().then(done);
        }, function () { return relay().then(done); })
        .catch(function (err) {
          if (err && err.validation) { say(err.message, false); return; }
          if (type === 'contact' && cfg.email) {
            var txt = ['Imię: ' + (data.get('imie') || ''), 'Nazwisko: ' + (data.get('nazwisko') || ''), 'E-mail: ' + (data.get('email') || ''), '', data.get('wiadomosc') || ''].join('\n');
            say('Nie udało się wysłać formularza — otwieram program pocztowy z wiadomością do ' + cfg.email + '…', false);
            location.href = 'mailto:' + cfg.email + '?subject=' + encodeURIComponent('Wiadomość ze strony KOMpetition.cc') + '&body=' + encodeURIComponent(txt);
          } else {
            say('Nie udało się wysłać. Napisz na ' + cfg.email + '.', false);
          }
        })
        .finally(function () { btn && (btn.disabled = false); });
    });
  }
  $$('form[data-form]').forEach(bindForm);
  window.KOM_bindForm = bindForm;

  /* Popup newslettera */
  (function () {
    var path = location.pathname;
    if (/^\/(plany-treningowe|kontakt|dziekuje|admin|polityka-prywatnosci|regulamin)/.test(path)) return;
    var get = function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } };
    var st = get('kom-nl');
    if (st === 'subscribed' || (st && Date.now() - (+st) < 21 * 864e5)) return;
    try { if (sessionStorage.getItem('kom-nl-shown')) return; } catch (e) {}
    var shown = false, t0 = Date.now();
    function show() {
      if (shown || document.querySelector('.consent-bar') || body.classList.contains('nav-open')) return;
      shown = true;
      try { sessionStorage.setItem('kom-nl-shown', '1'); } catch (e) {}
      var w = doc.createElement('div');
      w.className = 'nl-pop'; w.setAttribute('role', 'dialog'); w.setAttribute('aria-modal', 'true'); w.setAttribute('aria-labelledby', 'nl-pop-h');
      w.innerHTML = '<div class="nl-pop__box"><button class="nl-pop__x" type="button" aria-label="Zamknij">×</button>' +
        '<p class="eyebrow">KOMpedium w skrzynce</p><h2 id="nl-pop-h">Trenuj mądrzej – bez przekopywania internetu</h2>' +
        '<p>Zapisz się na newsletter i dostawaj wiedzę, którą sam stosuję w pracy z zawodnikami:</p>' +
        '<ul><li>nowe artykuły z KOMpedium – badania przełożone na konkretne treningi</li><li>gotowe protokoły i sesje do wrzucenia w plan</li><li>pierwszeństwo przy nowych planach i wyjazdach treningowych</li></ul>' +
        '<form class="form" data-form="newsletter" action="/api/newsletter.php" method="post" novalidate>' +
        '<div class="row"><div class="field"><label for="pop-imie">Imię</label><input id="pop-imie" name="imie" type="text" autocomplete="given-name"></div>' +
        '<div class="field"><label for="pop-email">E-mail *</label><input id="pop-email" name="email" type="email" autocomplete="email" required></div></div>' +
        '<label class="consent"><input type="checkbox" name="zgoda" value="1" required><span>Chcę otrzymywać newsletter KOMpetition.cc na podany adres e-mail. Zgodę mogę wycofać w każdej chwili. Administratorem danych jest Jakub Obitko – szczegóły w <a href="/polityka-prywatnosci/">polityce prywatności</a>.</span></label>' +
        '<div class="hp" aria-hidden="true"><label>Strona www<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>' +
        '<div><button class="btn btn--sun" type="submit">Zapisuję się</button></div><p class="form-status" role="status" aria-live="polite"></p></form>' +
        '<p class="muted" style="font-size:.85rem;margin:.8em 0 0">Maksymalnie 2 maile w miesiącu. Bez spamu – możesz wypisać się w każdej chwili.</p>' +
        '<button class="nl-pop__later" type="button">Nie teraz</button></div>';
      body.appendChild(w);
      bindForm($('form', w));
      requestAnimationFrame(function () { w.classList.add('show'); });
      var last = doc.activeElement;
      var close = function () {
        try { if (get('kom-nl') !== 'subscribed') localStorage.setItem('kom-nl', String(Date.now())); } catch (e) {}
        w.classList.remove('show'); setTimeout(function () { w.remove(); last && last.focus && last.focus(); }, 300);
        doc.removeEventListener('keydown', onKey);
      };
      var onKey = function (e) { if (e.key === 'Escape') close(); };
      doc.addEventListener('keydown', onKey);
      $('.nl-pop__x', w).addEventListener('click', close);
      $('.nl-pop__later', w).addEventListener('click', close);
      w.addEventListener('click', function (e) { if (e.target === w) close(); });
      setTimeout(function () { var f = $('#pop-email', w); f && f.focus({ preventScroll: true }); }, 350);
      window.dataLayer && window.dataLayer.push({ event: 'newsletter_popup_view' });
    }
    setTimeout(show, 5000);
    if (/^\/blog\/.+/.test(path)) {
      window.addEventListener('scroll', function onS() {
        var h = doc.documentElement;
        if ((window.scrollY + window.innerHeight) / h.scrollHeight > 0.55) { window.removeEventListener('scroll', onS); show(); }
      }, { passive: true });
    }
    if (window.matchMedia('(pointer:fine)').matches) {
      doc.addEventListener('mouseout', function (e) { if (!e.relatedTarget && e.clientY < 10 && Date.now() - t0 > 10000) show(); });
    }
  })();
})();
