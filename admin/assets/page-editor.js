/* Edytor wizualny strony – działa w podglądzie (iframe) w panelu. */
(function () {
  var main = document.querySelector('main');
  var TEXT = 'h1,h2,h3,h4,p,li,blockquote,figcaption,summary,td,th,dt,dd,.price,.price-big,.tag,.eyebrow,.lead,a.btn,a.link-arrow,.stat b,.stat span,.facts b,.facts span,.hero__trust span,.badge,label.consent span';
  var SKIP = 'form,.crumbs,.embed-gate,.calc-frame,iframe,.stars,.kom-tools';

  function editable() {
    main.querySelectorAll('details:not([open])').forEach(function (d) { d.setAttribute('open', ''); d.setAttribute('data-kom-closed', '1'); });
    main.querySelectorAll(TEXT).forEach(function (el) {
      if (el.closest(SKIP)) return;
      if (el.parentElement && el.parentElement.closest('[contenteditable="true"]')) return;   // rodzic już edytowalny
      el.setAttribute('contenteditable', 'true');
      el.setAttribute('spellcheck', 'true');
    });
  }
  editable();

  // nie przechodź w linki i nie zwijaj FAQ podczas edycji
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a,summary,button');
    if (a && main.contains(a)) e.preventDefault();
    if (a && !main.contains(a)) e.preventDefault();
  }, true);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.matches && e.target.matches('h1,h2,h3,h4,summary,a.btn,.tag,.eyebrow,.price,td,th')) e.preventDefault();
  }, true);
  // wklejanie jako czysty tekst
  document.addEventListener('paste', function (e) {
    if (!e.target.closest || !e.target.closest('[contenteditable]')) return;
    e.preventDefault();
    var t = (e.clipboardData || window.clipboardData).getData('text/plain');
    document.execCommand('insertText', false, t);
  });
  // dwuklik w link = zmiana adresu
  document.addEventListener('dblclick', function (e) {
    var a = e.target.closest('main a');
    if (!a) return;
    var u = prompt('Adres linku:', a.getAttribute('href') || '');
    if (u !== null) a.setAttribute('href', u.trim());
  });

  // zdjęcia: podmiana i opis
  var tools = document.createElement('div');
  tools.className = 'kom-tools'; tools.hidden = true;
  tools.innerHTML = '<button type="button" data-a="replace">Podmień zdjęcie</button><button type="button" data-a="alt">Opis (alt)</button>';
  document.body.appendChild(tools);
  var current = null;
  var picker = document.createElement('input'); picker.type = 'file'; picker.accept = 'image/jpeg,image/png,image/webp';
  main.addEventListener('click', function (e) {
    var img = e.target.closest('img');
    if (!img || img.closest(SKIP)) { if (!e.target.closest('.kom-tools')) tools.hidden = true; return; }
    current = img;
    var r = img.getBoundingClientRect();
    tools.style.top = (window.scrollY + r.top + 12) + 'px'; tools.style.left = (window.scrollX + r.left + 12) + 'px';
    tools.hidden = false;
  });
  // obrazy w tle hero nie łapią kliknięć przez nakładkę – dodaj przycisk
  document.querySelectorAll('.hero__bg').forEach(function (bg) {
    if (bg.tagName !== 'IMG') return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'kom-hero-btn'; b.textContent = 'Podmień tło';
    b.addEventListener('click', function (e) { e.stopPropagation(); current = bg; picker.click(); });
    bg.parentElement.appendChild(b);
  });
  tools.addEventListener('click', function (e) {
    var a = e.target.getAttribute('data-a');
    if (!current) return;
    if (a === 'alt') { var v = prompt('Opis zdjęcia (dla Google i osób niewidomych):', current.getAttribute('alt') || ''); if (v !== null) { current.setAttribute('alt', v); markDirty(); } }
    if (a === 'replace') picker.click();
    tools.hidden = true;
  });
  picker.addEventListener('change', function () {
    var f = picker.files[0]; if (!f || !current) return;
    current.style.opacity = '.4';
    parent.KOM_UPLOAD(f).then(function (j) {
      current.style.opacity = '';
      if (j.error) { alert(j.error); return; }
      current.src = j.location; current.setAttribute('srcset', j.srcset);
      current.setAttribute('width', j.width); current.setAttribute('height', j.height);
      markDirty();
    }).catch(function () { current.style.opacity = ''; alert('Nie udało się wgrać zdjęcia.'); });
    picker.value = '';
  });
  function markDirty() { document.dispatchEvent(new Event('input', { bubbles: true })); }

  window.KOM_getMain = function () {
    var c = main.cloneNode(true);
    c.querySelectorAll('[contenteditable]').forEach(function (el) { el.removeAttribute('contenteditable'); el.removeAttribute('spellcheck'); });
    c.querySelectorAll('[data-kom-closed]').forEach(function (d) { d.removeAttribute('open'); d.removeAttribute('data-kom-closed'); });
    c.querySelectorAll('.kom-tools,.kom-hero-btn').forEach(function (el) { el.remove(); });
    c.querySelectorAll('[style=""]').forEach(function (el) { el.removeAttribute('style'); });
    return c.innerHTML;
  };
  window.KOM_setMain = function (html) { main.innerHTML = html; editable(); };
})();
