// Worker KOMpetition.cc: statyczna strona z dist/ + zapis na newsletter do Brevo.
// Zmienne (Cloudflare → Workers → kompetitioncc → Settings → Variables and Secrets, typ „Secret”):
//   BREVO_API_KEY            klucz API Brevo (SMTP & API → API Keys)
//   BREVO_LIST_ID            numer listy „Newsletter” w Brevo (Contacts → Lists, kolumna ID)
//   BREVO_DOI_TEMPLATE_ID    szablon double opt-in (tag „optin”, link {{ doubleoptin }}); nowe osoby potwierdzają zapis,
//                            raport CP / mail z planem idą dopiero po kliknięciu (dane czekają w CP_KV jako pending:<token>, 7 dni)
//   BREVO_WELCOME_TEMPLATE_ID szablon maila powitalnego wysyłanego od razu nowej osobie (0 = wyłączone)
//   BREVO_CP_TEMPLATE_ID     szablon maila z raportem z kalkulatora CP (0 = zamiast niego zwykłe powitanie)
//   BREVO_CP_REMINDER_TEMPLATE_ID szablon przypomnienia o powtórce testu po CP_REMINDER_DAYS dniach (cron codziennie rano)
//   CP_KV                    KV z terminami przypomnień: due:RRRR-MM-DD:email → dane z raportu
// Bez klucza lub listy Worker zwraca 503, a strona sama przechodzi na zapasowe powiadomienie mailem (FormSubmit).

import { cpModel, pl } from './assets/js/cp-model.js';

const NEWSLETTER_PATHS = new Set(['/api/newsletter', '/api/newsletter.php']);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' } });

async function readForm(request) {
  const type = request.headers.get('Content-Type') || '';
  if (type.includes('application/json')) return await request.json();
  const fd = await request.formData();
  return Object.fromEntries([...fd.entries()].map(([k, v]) => [k, typeof v === 'string' ? v : '']));
}

async function brevo(apiKey, path, payload) {
  const r = await fetch('https://api.brevo.com/v3' + path, {
    method: 'POST',
    headers: { 'api-key': apiKey, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(payload),
  });
  if (r.ok) return { ok: true, status: r.status };
  const j = await r.json().catch(() => ({}));
  return { ok: false, status: r.status, code: j.code, message: j.message };
}

const tyg = (n) => n + (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? ' tygodnie' : ' tygodni');

// Plan z ankiety doboru: dane bierzemy ze strony (shop-data + config.js), a nie z formularza,
// więc do maila trafiają tylko nasze treści i linki.
async function planParams(f, email, request, env) {
  const slug = String(f.plan_slug || ''), weeks = String(f.plan_weeks || ''), hours = String(f.plan_hours || '');
  if (!/^[a-z0-9-]{3,40}$/.test(slug) || !/^\d{1,2}$/.test(weeks) || !/^\d{1,2}-\d{1,2}$/.test(hours)) return null;
  const origin = new URL(request.url).origin;
  const [shopHtml, cfgJs] = await Promise.all([
    env.ASSETS.fetch(new Request(origin + '/plany-treningowe/')).then((r) => r.text()),
    env.ASSETS.fetch(new Request(origin + '/assets/js/config.js')).then((r) => r.text()),
  ]);
  const shopJson = shopHtml.match(/<script[^>]*id="shop-data"[^>]*>([\s\S]*?)<\/script>/);
  const linksJson = cfgJs.match(/"paymentLinks":\s*(\{[\s\S]*?\})/);
  if (!shopJson) return null;
  const shop = JSON.parse(shopJson[1]);
  const plan = shop.plans && shop.plans[slug];
  if (!plan || !plan.prices || !plan.prices[weeks] || !(shop.hoursLabel || {})[hours]) return null;
  const links = linksJson ? JSON.parse(linksJson[1]) : {};
  const utm = 'utm_source=newsletter&utm_medium=email&utm_campaign=ankieta';
  let buy = links[slug + '-' + weeks];
  if (buy) buy += '?client_reference_id=' + encodeURIComponent(`${slug}-${weeks}w-${hours}h`) +
    '&prefilled_email=' + encodeURIComponent(email) + '&prefilled_promo_code=WITAJ10';
  else buy = `${origin}/kontakt/?temat=${encodeURIComponent(`Zakup planu: ${plan.name}`)}#formularz`;
  return {
    PLAN_NAME: plan.name,
    PLAN_VARIANT: `${tyg(+weeks)} · ${shop.hoursLabel[hours]} tygodniowo`,
    PLAN_PRICE: String(plan.prices[weeks]),
    PLAN_PRICE_CODE: String(Math.round(plan.prices[weeks] * 0.9)),
    PLAN_TAGLINE: plan.tagline || '',
    PLAN_IMG: `${origin}/assets/email/plan-${slug}.jpg`,
    PLAN_URL: `${origin}${plan.url}?w=${weeks}&h=${hours}&${utm}`,
    PLAN_BUY: buy,
  };
}

// Raport z kalkulatora CP: przeliczamy go tutaj z danych wejściowych (ten sam model co na stronie),
// więc do maila trafiają tylko nasze liczby i teksty, nie wartości z formularza.
function cpParams(raw) {
  let inp;
  try { inp = JSON.parse(String(raw || '')); } catch { return null; }
  if (!inp || typeof inp !== 'object') return null;
  const keys = ['age', 'weight', 'bf', 'p3', 'p12', 'sprint'];
  const clean = { gender: inp.gender === 'female' ? 'female' : 'male' };
  for (const k of keys) clean[k] = String(inp[k] ?? '').replace(/[^\d.,]/g, '').slice(0, 8);
  const m = cpModel(clean);
  if (m.error) return null;
  const r = Math.round;
  const z2 = m.fuel[0], ss = m.fuel[2];
  return {
    model: m,
    params: {
      TYPE: m.type, TYPE_DESC: m.typeDesc,
      CP: String(r(m.cp)), CP_KG: pl(m.cpKg, 2), CP_RANK: m.cpRank.label,
      WK: pl(m.wk, 1), W_KG: String(r(m.wKg)), W_LABEL: m.wLabel,
      VO2: String(r(m.vo2)), UTIL: String(r(m.util)), FTP: String(r(m.ftp)), FFM: pl(m.ffm, 1),
      UTIL_TXT: m.util >= 85 ? 'Próg jest blisko pułapu tlenowego – żeby dalej podnosić CP, podnieś VO2max.'
        : m.util < 78 ? 'Między progiem a pułapem jest duży zapas – praca nad progiem da szybkie efekty.'
        : 'Typowy zakres. U większości kolarzy o mocy progowej decydują VO2max i ekonomia jazdy.',
      VLA: pl(m.vla, 2), VLA_LABEL: m.vlaLabel,
      FATMAX: `${r(m.fatMax * 0.95)}–${r(m.fatMax * 1.05)}`, MFO_GH: String(r(m.mfo * 60)),
      TYPE1: String(m.type1), T1_RANGE: String(m.type1Range), SPRINT: m.sprint ? String(r(m.sprint)) : '',
      CURVE: [...(m.sprint ? [{ t: '12 s (PR)', w: r(m.sprint), wkg: pl(m.sprint / m.weight, 1) }] : []),
        ...m.curve.map((c) => ({ t: c.t, w: c.w, wkg: pl(c.wkg, 2) }))],
      FUEL: m.fuel.map((f) => ({ n: `${f.n} · ${f.pct}% CP`, w: f.w, fat: f.fat, cho: f.cho })),
      FUEL_NOTE: `Przy sweet spocie spalasz ok. ${ss.cho} g węglowodanów na godzinę – więcej, niż wchłoną jelita (zwykle 60–90 g/h, po treningu jelit do 120 g/h). Na długich startach celuj w 80–100 g/h od pierwszych minut. Na spokojnej Z2 (${z2.w} W) wystarczy ok. ${Math.min(90, Math.max(40, r(z2.cho * 0.6 / 10) * 10))} g/h.`,
      STRENGTHS: m.strengths, LIMITERS: m.limiters,
      BODY: m.body ? `Przy ${pl(m.body.targetBf, 0)}% tkanki tłuszczowej (−${pl(m.body.lose, 1)} kg tłuszczu, bez utraty mięśni) Twoje CP dałoby ${pl(m.body.cpKg, 2)} W/kg zamiast ${pl(m.cpKg, 2)}. Redukcję planuj poza sezonem startowym.` : '',
      FOCUS: m.focus, SESSIONS: m.sessions.map(([n, d]) => ({ n, d })),
    },
  };
}

async function newsletter(request, env) {
  if (request.method !== 'POST') return json({ ok: false, error: 'Metoda niedozwolona.' }, 405);

  const origin = request.headers.get('Origin');
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({ ok: false, error: 'Niedozwolone źródło.' }, 403);

  let f;
  try { f = await readForm(request); } catch { return json({ ok: false, error: 'Nieprawidłowe dane formularza.' }, 422); }

  // honeypot: bot wypełnił ukryte pole – udajemy sukces, nic nie zapisujemy
  if ((f.website || '').trim()) return json({ ok: true });

  const email = String(f.email || '').trim().toLowerCase();
  const name = String(f.imie || '').trim().slice(0, 60);
  if (!EMAIL_RE.test(email) || email.length > 254) return json({ ok: false, error: 'Podaj poprawny adres e-mail.' }, 422);
  if (name.length < 2) return json({ ok: false, error: 'Podaj swoje imię.' }, 422);
  if (!f.zgoda) return json({ ok: false, error: 'Zaznacz zgodę na otrzymywanie newslettera.' }, 422);

  // tolerancja na spacje/cudzysłowy wklejone razem z wartością w panelu Cloudflare
  const apiKey = String(env.BREVO_API_KEY || '').trim().replace(/^["']|["']$/g, '');
  const listId = parseInt(String(env.BREVO_LIST_ID || '').replace(/\D/g, ''), 10);
  if (!apiKey || !listId) {
    const missing = [!apiKey && 'BREVO_API_KEY', !listId && 'BREVO_LIST_ID'].filter(Boolean).join(', ');
    return json({ ok: false, error: 'Newsletter nie jest jeszcze skonfigurowany.', missing }, 503);
  }

  const attributes = name ? { FIRSTNAME: name } : {};
  const doiTemplate = Number(env.BREVO_DOI_TEMPLATE_ID);
  const cpTemplate = Number(env.BREVO_CP_TEMPLATE_ID);
  const cp = f.cp && cpTemplate ? cpParams(f.cp) : null;

  // double opt-in: nowa osoba (albo wypisana / spoza listy) najpierw potwierdza adres linkiem z maila.
  // Raport CP i mail z planem wysyłamy dopiero po kliknięciu – dane czekają w KV pod losowym tokenem.
  if (doiTemplate && !(await isSubscribed(apiKey, email, listId))) {
    if (!env.CP_KV) return json({ ok: false, error: 'Newsletter nie jest jeszcze skonfigurowany.' }, 503);
    const token = crypto.randomUUID().replace(/-/g, '');
    const pending = { email, name, cp: cp ? String(f.cp).slice(0, 1000) : '', plan_slug: f.plan_slug || '', plan_weeks: f.plan_weeks || '', plan_hours: f.plan_hours || '' };
    await env.CP_KV.put('pending:' + token, JSON.stringify(pending), { expirationTtl: 7 * 86400 });
    const res = await brevo(apiKey, '/contacts/doubleOptinConfirmation', {
      email, attributes, includeListIds: [listId], templateId: doiTemplate,
      redirectionUrl: new URL('/api/newsletter/potwierdz?t=' + token, request.url).href,
    });
    if (!res.ok) {
      console.error('Brevo DOI error', res.status, res.code, res.message);
      return json({ ok: false, error: 'Nie udało się zapisać. Spróbuj ponownie.' }, 502);
    }
    // ankieta doboru planu: strona i tak wysyła powiadomienie mailem z wybranym planem (relay)
    return json({ ok: true, confirm: true, relay: Boolean(f.plan), report: Boolean(cp) });
  }

  // osoba już zapisana (albo double opt-in wyłączony): aktualizacja kontaktu i maile od razu
  const res = await brevo(apiKey, '/contacts', { email, attributes, listIds: [listId], updateEnabled: true });
  if (!res.ok) {
    console.error('Brevo error', res.status, res.code, res.message);
    return json({ ok: false, error: 'Nie udało się zapisać. Spróbuj ponownie.' }, 502);
  }
  await sendFollowUp(env, request, apiKey, { email, name, cp, f, isNew: res.status === 201 });
  return json({ ok: true, relay: Boolean(f.plan), report: Boolean(cp) });
}

async function isSubscribed(apiKey, email, listId) {
  const r = await fetch('https://api.brevo.com/v3/contacts/' + encodeURIComponent(email), { headers: { 'api-key': apiKey, Accept: 'application/json' } });
  if (!r.ok) return false;
  const c = await r.json().catch(() => ({}));
  return !c.emailBlacklisted && (c.listIds || []).includes(listId);
}

// raport CP albo mail powitalny (z kartą planu, jeśli przyszedł z ankiety doboru)
async function sendFollowUp(env, request, apiKey, { email, name, cp, f, isNew }) {
  const welcomeTemplate = Number(env.BREVO_WELCOME_TEMPLATE_ID);
  const cpTemplate = Number(env.BREVO_CP_TEMPLATE_ID);
  if (cp) {
    // polecany plan liczymy z modelu, nie z pól formularza
    f.plan_slug = cp.model.rec.slug; f.plan_weeks = cp.model.rec.weeks; f.plan_hours = cp.model.rec.hours;
  }
  let params = null;
  if (f.plan_slug) {
    try { params = await planParams(f, email, request, env); } catch (e) { console.error('plan params error', e && e.message); }
  }
  if (cp) {
    // raport z kalkulatora CP wysyłamy zawsze (także osobom już zapisanym) – zamiast zwykłego powitania
    const msg = { templateId: cpTemplate, to: [{ email, name }], tags: ['kalkulator-cp'],
      params: { ...(params || {}), ...cp.params },
      subject: `Twój profil mocy: ${cp.params.TYPE} · CP ${cp.params.CP} W` };
    const sent = await brevo(apiKey, '/smtp/email', msg);
    if (!sent.ok) console.error('Brevo CP report error', sent.status, sent.code, sent.message);
    else await scheduleReminder(env, email, name, cp.params);
  } else if (welcomeTemplate && (isNew || params)) {
    const msg = { templateId: welcomeTemplate, to: [name ? { email, name } : { email }], tags: [params ? 'ankieta' : 'powitanie'] };
    if (params) { msg.params = params; msg.subject = `Twój plan: ${params.PLAN_NAME} + kod −10%`; }
    const sent = await brevo(apiKey, '/smtp/email', msg);
    if (!sent.ok) console.error('Brevo welcome error', sent.status, sent.code, sent.message);
  }
}

// kliknięcie linku z maila potwierdzającego: Brevo dopisuje kontakt do listy i przekierowuje tutaj
async function confirmSubscription(request, env) {
  const url = new URL(request.url);
  const home = (q) => Response.redirect(new URL('/' + q, request.url).href, 302);
  const token = (url.searchParams.get('t') || '').replace(/[^a-f0-9]/g, '');
  if (!token || !env.CP_KV) return home('?newsletter=potwierdzony');
  const raw = await env.CP_KV.get('pending:' + token);
  if (!raw) return home('?newsletter=potwierdzony');
  const p = JSON.parse(raw);
  const apiKey = String(env.BREVO_API_KEY || '').trim().replace(/^["']|["']$/g, '');
  const listId = parseInt(String(env.BREVO_LIST_ID || '').replace(/\D/g, ''), 10);
  // maile wysyłamy tylko wtedy, gdy adres faktycznie jest już potwierdzony na liście
  if (!apiKey || !listId || !(await isSubscribed(apiKey, p.email, listId))) return home('?newsletter=potwierdzony');
  await env.CP_KV.delete('pending:' + token);
  const cp = p.cp ? cpParams(p.cp) : null;
  try {
    await sendFollowUp(env, request, apiKey, { email: p.email, name: p.name, cp, isNew: true,
      f: { plan_slug: p.plan_slug, plan_weeks: p.plan_weeks, plan_hours: p.plan_hours } });
  } catch (e) { console.error('confirm follow-up error', e && e.message); }
  return cp ? Response.redirect(new URL('/cp-kalkulator/?raport=wyslany', request.url).href, 302) : home('?newsletter=potwierdzony');
}

// ---------- przypomnienie o powtórce testu CP ----------
const day = (d) => d.toISOString().slice(0, 10);

async function scheduleReminder(env, email, name, p) {
  if (!env.CP_KV) return;
  try {
    const days = parseInt(env.CP_REMINDER_DAYS || '56', 10);
    const now = new Date();
    const due = day(new Date(now.getTime() + days * 864e5));
    const lastKey = 'last:' + email;
    const prev = await env.CP_KV.get(lastKey);
    if (prev) await env.CP_KV.delete(prev);            // nowy raport = nowy termin, stary znika
    const key = `due:${due}:${email}`;
    const data = { email, name, date: now.toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Warsaw' }),
      TYPE: p.TYPE, CP: p.CP, CP_KG: p.CP_KG, WK: p.WK, VO2: p.VO2 };
    await env.CP_KV.put(key, JSON.stringify(data), { expirationTtl: (days + 30) * 86400 });
    await env.CP_KV.put(lastKey, key, { expirationTtl: (days + 30) * 86400 });
  } catch (e) { console.error('KV reminder error', e && e.message); }
}

async function sendReminders(env) {
  const apiKey = String(env.BREVO_API_KEY || '').trim().replace(/^["']|["']$/g, '');
  const tpl = Number(env.BREVO_CP_REMINDER_TEMPLATE_ID);
  const listId = parseInt(String(env.BREVO_LIST_ID || '').replace(/\D/g, ''), 10);
  if (!env.CP_KV || !apiKey || !tpl) return;
  const today = day(new Date());
  let cursor, sent = 0;
  do {
    const page = await env.CP_KV.list({ prefix: 'due:', cursor });
    for (const k of page.keys) {
      if (k.name.slice(4, 14) > today) continue;       // termin jeszcze nie minął
      const data = JSON.parse((await env.CP_KV.get(k.name)) || 'null');
      await env.CP_KV.delete(k.name);
      if (!data) continue;
      // tylko do osób wciąż zapisanych na newsletter
      const r = await fetch('https://api.brevo.com/v3/contacts/' + encodeURIComponent(data.email), { headers: { 'api-key': apiKey, Accept: 'application/json' } });
      if (!r.ok) continue;
      const c = await r.json().catch(() => ({}));
      if (c.emailBlacklisted || (listId && !(c.listIds || []).includes(listId))) continue;
      const res = await brevo(apiKey, '/smtp/email', {
        templateId: tpl, to: [{ email: data.email, name: data.name }], tags: ['przypomnienie-cp'],
        params: { DATE: data.date, TYPE: data.TYPE, CP: data.CP, CP_KG: data.CP_KG, WK: data.WK, VO2: data.VO2 },
      });
      if (res.ok) sent++; else console.error('Brevo reminder error', res.status, res.code, res.message);
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  console.log('Przypomnienia CP wysłane:', sent);
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(sendReminders(env));
  },
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === '/api/newsletter/potwierdz') return confirmSubscription(request, env);
    if (NEWSLETTER_PATHS.has(pathname)) return newsletter(request, env);
    return env.ASSETS.fetch(request);
  },
};
