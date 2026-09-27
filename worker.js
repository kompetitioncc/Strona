// Worker KOMpetition.cc: statyczna strona z dist/ + zapis na newsletter do Brevo.
// Zmienne (Cloudflare → Workers → kompetitioncc → Settings → Variables and Secrets, typ „Secret”):
//   BREVO_API_KEY            klucz API Brevo (SMTP & API → API Keys)
//   BREVO_LIST_ID            numer listy „Newsletter” w Brevo (Contacts → Lists, kolumna ID)
//   BREVO_DOI_TEMPLATE_ID    opcjonalnie: szablon double opt-in; bez niego zapis jest od razu (zgoda z checkboxa)
//   BREVO_WELCOME_TEMPLATE_ID szablon maila powitalnego wysyłanego od razu nowej osobie (0 = wyłączone)
// Bez klucza lub listy Worker zwraca 503, a strona sama przechodzi na zapasowe powiadomienie mailem (FormSubmit).

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
    PLAN_PHASES: (plan.phases && plan.phases[weeks]) || [],
    PLAN_IMG: `${origin}/assets/email/plan-${slug}.jpg`,
    PLAN_URL: `${origin}${plan.url}?w=${weeks}&h=${hours}&${utm}`,
    PLAN_BUY: buy,
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
  const res = doiTemplate
    ? await brevo(apiKey, '/contacts/doubleOptinConfirmation', {
        email, attributes, includeListIds: [listId], templateId: doiTemplate,
        redirectionUrl: new URL('/?newsletter=potwierdzony', request.url).href,
      })
    : await brevo(apiKey, '/contacts', { email, attributes, listIds: [listId], updateEnabled: true });

  if (!res.ok) {
    console.error('Brevo error', res.status, res.code, res.message);
    return json({ ok: false, error: 'Nie udało się zapisać. Spróbuj ponownie.' }, 502);
  }

  // mail powitalny od razu: nowemu kontaktowi (201) albo każdemu, kto przyszedł z ankiety doboru planu
  // (prosił o przesłanie planu) – wtedy z kartą polecanego planu
  const welcomeTemplate = Number(env.BREVO_WELCOME_TEMPLATE_ID);
  let params = null;
  if (f.plan_slug) {
    try { params = await planParams(f, email, request, env); } catch (e) { console.error('plan params error', e && e.message); }
  }
  if (!doiTemplate && welcomeTemplate && (res.status === 201 || params)) {
    const msg = { templateId: welcomeTemplate, to: [name ? { email, name } : { email }], tags: [params ? 'ankieta' : 'powitanie'] };
    if (params) { msg.params = params; msg.subject = `Twój plan: ${params.PLAN_NAME} + kod −10%`; }
    const sent = await brevo(apiKey, '/smtp/email', msg);
    if (!sent.ok) console.error('Brevo welcome error', sent.status, sent.code, sent.message);
  }
  // ankieta doboru planu: kontakt jest w Brevo, ale strona wysyła też powiadomienie mailem z wybranym planem
  return json({ ok: true, relay: Boolean(f.plan) });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (NEWSLETTER_PATHS.has(pathname)) return newsletter(request, env);
    return env.ASSETS.fetch(request);
  },
};
