// Worker KOMpetition.cc: statyczna strona z dist/ + zapis na newsletter do Brevo.
// Zmienne (Cloudflare → Workers → kompetitioncc → Settings → Variables and Secrets, typ „Secret”):
//   BREVO_API_KEY            klucz API Brevo (SMTP & API → API Keys)
//   BREVO_LIST_ID            numer listy „Newsletter” w Brevo (Contacts → Lists, kolumna ID)
//   BREVO_DOI_TEMPLATE_ID    opcjonalnie: szablon double opt-in; bez niego zapis jest od razu (zgoda z checkboxa)
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

async function brevo(env, path, payload) {
  const r = await fetch('https://api.brevo.com/v3' + path, {
    method: 'POST',
    headers: { 'api-key': env.BREVO_API_KEY, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(payload),
  });
  if (r.ok) return { ok: true };
  const j = await r.json().catch(() => ({}));
  return { ok: false, status: r.status, code: j.code, message: j.message };
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

  const listId = Number(env.BREVO_LIST_ID);
  if (!env.BREVO_API_KEY || !listId) return json({ ok: false, error: 'Newsletter nie jest jeszcze skonfigurowany.' }, 503);

  const attributes = name ? { FIRSTNAME: name } : {};
  const doiTemplate = Number(env.BREVO_DOI_TEMPLATE_ID);
  const res = doiTemplate
    ? await brevo(env, '/contacts/doubleOptinConfirmation', {
        email, attributes, includeListIds: [listId], templateId: doiTemplate,
        redirectionUrl: new URL('/?newsletter=potwierdzony', request.url).href,
      })
    : await brevo(env, '/contacts', { email, attributes, listIds: [listId], updateEnabled: true });

  if (!res.ok) {
    console.error('Brevo error', res.status, res.code, res.message);
    return json({ ok: false, error: 'Nie udało się zapisać. Spróbuj ponownie.' }, 502);
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
