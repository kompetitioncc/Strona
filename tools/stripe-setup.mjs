#!/usr/bin/env node
/*
 * KOMpetition.cc – jednorazowa konfiguracja płatności Stripe.
 *
 * Tworzy w Twoim koncie Stripe produkty, ceny i linki płatności (Payment Links) dla
 * wszystkich planów z content/shop.json, a potem wpisuje linki do strony
 * (content/settings.json + assets/js/config.js).
 *
 * Użycie (w katalogu strony):
 *   STRIPE_SECRET_KEY=sk_test_... node tools/stripe-setup.mjs --dry-run   # podgląd, nic nie tworzy
 *   STRIPE_SECRET_KEY=sk_test_... node tools/stripe-setup.mjs             # tryb testowy
 *   STRIPE_SECRET_KEY=sk_live_... node tools/stripe-setup.mjs             # na produkcji
 * Opcje:
 *   --tos      wymagaj zgody na regulamin w Checkout (najpierw ustaw adres regulaminu w Stripe: Settings → Public details)
 *   --force    utwórz linki ponownie, nawet jeśli już istnieją w content/stripe-links.json
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SITE_URL = 'https://kompetition.cc';
const args = new Set(process.argv.slice(2));
const DRY = args.has('--dry-run'), FORCE = args.has('--force'), TOS = args.has('--tos');
const KEY = process.env.STRIPE_SECRET_KEY || '';
if (!DRY && !/^[sr]k_(test|live)_/.test(KEY)) {
  console.error('Brak klucza. Ustaw zmienną STRIPE_SECRET_KEY (Stripe → Developers → API keys → Secret key albo klucz ograniczony rk_ z uprawnieniami Write: Products, Prices, Payment Links).');
  process.exit(1);
}
const MODE = /^[sr]k_live_/.test(KEY) ? 'LIVE' : 'TEST';

const shop = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/shop.json'), 'utf8'));
const linksFile = path.join(ROOT, 'content/stripe-links.json');
const links = fs.existsSync(linksFile) ? JSON.parse(fs.readFileSync(linksFile, 'utf8')) : {};

// Stripe przyjmuje parametry w formacie application/x-www-form-urlencoded z zagnieżdżeniami a[b][0][c]=…
function encode(obj, prefix = '', out = []) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}[${k}]` : k;
    if (v === undefined || v === null) continue;
    if (typeof v === 'object') encode(v, key, out);
    else out.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(v))}`);
  }
  return out.join('&');
}
async function stripe(endpoint, params) {
  if (DRY) { console.log(`  [dry-run] POST /v1/${endpoint}`); return { id: `dry_${endpoint}`, url: `https://buy.stripe.com/test_${Math.random().toString(36).slice(2, 8)}` }; }
  const r = await fetch(`https://api.stripe.com/v1/${endpoint}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/x-www-form-urlencoded', 'Stripe-Version': '2024-06-20' },
    body: encode(params),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(`${endpoint}: ${j.error?.message || r.status}`);
  return j;
}

const hours = shop.hours.map((h) => ({ label: `${shop.hoursLabel[h]} tygodniowo`, value: h.replace('-', '_') }));
console.log(`Stripe – tryb ${DRY ? 'PODGLĄD (dry-run)' : MODE}\n`);

for (const [slug, plan] of Object.entries(shop.plans)) {
  for (const w of plan.weeks) {
    const key = `${slug}-${w}`;
    if (links[key] && !FORCE) { console.log(`• ${key}: już istnieje – pomijam`); continue; }
    const price = plan.prices[String(w)];
    const weeksTxt = w === 4 ? '4 tygodnie' : `${w} tygodni`;
    console.log(`• ${plan.name} – ${weeksTxt} – ${price} zł`);
    const product = await stripe('products', {
      name: `${plan.name} – plan treningowy (${weeksTxt})`,
      description: plan.tagline,
      images: { 0: SITE_URL + plan.cover },
      metadata: { plan: slug, weeks: w },
      tax_code: 'txcd_10000000',   // usługi/treści elektroniczne ogólne
    });
    const pr = await stripe('prices', { product: product.id, currency: 'pln', unit_amount: price * 100, metadata: { plan: slug, weeks: w } });
    const link = await stripe('payment_links', {
      line_items: { 0: { price: pr.id, quantity: 1 } },
      after_completion: { type: 'redirect', redirect: { url: `${SITE_URL}/dziekuje/?plan=${slug}&w=${w}` } },
      invoice_creation: { enabled: true },
      allow_promotion_codes: true,
      billing_address_collection: 'auto',
      custom_fields: {
        0: { key: 'godziny', label: { type: 'custom', custom: 'Dostępny czas tygodniowo' }, type: 'dropdown', optional: false,
             dropdown: { options: Object.fromEntries(hours.map((h, i) => [i, h])) } },
        1: { key: 'konto', label: { type: 'custom', custom: 'E-mail konta Intervals.icu / TrainingPeaks' }, type: 'text', optional: true },
      },
      ...(TOS ? { consent_collection: { terms_of_service: 'required' } } : {}),
      metadata: { plan: slug, weeks: w },
    });
    links[key] = link.url;
    console.log(`  → ${link.url}`);
    if (!DRY) fs.writeFileSync(linksFile, JSON.stringify(links, null, 2));
  }
}

// wpisanie linków do ustawień strony i config.js (ten sam format co panel /admin)
const sFile = path.join(ROOT, 'content/settings.json');
const s = fs.existsSync(sFile) ? JSON.parse(fs.readFileSync(sFile, 'utf8')) : {};
s.paymentLinks = { ...(s.paymentLinks || {}), ...links };
const cfg = {
  contactEndpoint: s.contactEndpoint ?? '/api/kontakt.php', newsletterEndpoint: s.newsletterEndpoint ?? '/api/newsletter.php',
  email: s.email ?? 'kontakt@kompetition.cc', relay: s.relay ?? true, ga4Id: s.ga4Id ?? '', paymentLinks: s.paymentLinks,
};
if (DRY) { console.log(`\n[dry-run] Zapisałbym ${Object.keys(links).length} linków do content/settings.json i assets/js/config.js.`); process.exit(0); }
fs.writeFileSync(sFile, JSON.stringify(s, null, 4));
fs.writeFileSync(path.join(ROOT, 'assets/js/config.js'),
  '/* Plik generowany przez panel /admin → Ustawienia. Zmiany wprowadzaj w panelu. */\nwindow.KOM_CONFIG = ' + JSON.stringify(cfg, null, 4) + ';\n');
console.log(`\nGotowe: ${Object.keys(links).length} linków płatności zapisanych w stronie.`);
console.log('Pamiętaj: w Stripe → Settings → Payment methods włącz BLIK i Przelewy24.');
