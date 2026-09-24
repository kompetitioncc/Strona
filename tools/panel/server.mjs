#!/usr/bin/env node
/*
 * Lokalny panel KOMpetition.cc: PHP (WebAssembly) + automatyczna publikacja na GitHub.
 *
 *   npm install        (raz)
 *   npm run panel      → otwórz http://localhost:8766/admin/
 *
 * Po każdej zmianie zapisanej w panelu (wpis, strona, ustawienia) serwer robi
 * git commit + git push. Cloudflare Pages widzi nowy commit i w ~1 min publikuje stronę.
 */
import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs';
import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { loadNodeRuntime, createNodeFsMountHandler } from '@php-wasm/node';
import { PHP, PHPRequestHandler } from '@php-wasm/universal';

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const PORT = +(process.env.PORT || 8766);
const AUTO_PUSH = process.env.AUTO_PUSH !== '0';
const SYNC_FILE = path.join(SITE, 'admin/data/sync.json');

const php = new PHP(await loadNodeRuntime('8.3', { emscriptenOptions: { processId: 1 } }));
php.mkdir('/site');
await php.mount('/site', createNodeFsMountHandler(SITE));
const handler = new PHPRequestHandler({ php, documentRoot: '/site', absoluteUrl: `http://localhost:${PORT}`, cookieStore: false });

/* ---------- synchronizacja z GitHub ---------- */
const git = (args) => new Promise((resolve) => execFile('git', args, { cwd: SITE, env: { ...process.env, GIT_TERMINAL_PROMPT: '0' } },
  (err, stdout, stderr) => resolve({ ok: !err, out: (stdout + stderr).trim() })));
const writeSync = (o) => { try { fs.writeFileSync(SYNC_FILE, JSON.stringify({ ...o, time: new Date().toISOString() })); } catch {} };
let timer = null, running = false, again = false;

async function sync(reason) {
  if (running) { again = true; return; }
  running = true;
  try {
    if (!fs.existsSync(path.join(SITE, '.git'))) { writeSync({ ok: false, msg: 'Folder strony nie jest repozytorium git.' }); return; }
    await git(['add', '-A']);
    const st = await git(['status', '--porcelain']);
    if (st.out) {
      const c = await git(['commit', '-m', `Panel: ${reason}`]);
      if (!c.ok) { writeSync({ ok: false, msg: 'Commit nieudany: ' + c.out.slice(0, 300) }); return; }
    }
    const p = await git(['push', '--quiet', 'origin', 'HEAD']);
    if (p.ok) { writeSync({ ok: true, msg: 'Opublikowano na GitHub – Cloudflare wdroży zmiany w ok. 1 minutę.' }); console.log('✓ GitHub: wypchnięto zmiany'); }
    else { writeSync({ ok: false, msg: 'Nie udało się wysłać na GitHub: ' + p.out.slice(0, 300) }); console.log('✗ git push:', p.out); }
  } finally {
    running = false;
    if (again) { again = false; sync(reason); }
  }
}
function schedule(reason) {
  if (!AUTO_PUSH) return;
  clearTimeout(timer);
  writeSync({ ok: true, pending: true, msg: 'Zmiany czekają na publikację…' });
  timer = setTimeout(() => sync(reason), 6000);   // grupuje kilka szybkich zapisów w jeden commit
}
const REASON = { 'post-edit.php': 'wpis na blogu', 'posts.php': 'blog', 'page-edit.php': 'edycja strony', 'settings.php': 'ustawienia', 'backups.php': 'przywrócenie kopii', 'upload.php': 'zdjęcie' };

/* ---------- serwer HTTP ---------- */
http.createServer(async (req, res) => {
  try {
    const chunks = []; for await (const c of req) chunks.push(c);
    const body = Buffer.concat(chunks);
    const headers = {};
    for (const [k, v] of Object.entries(req.headers)) headers[k] = Array.isArray(v) ? v.join(', ') : v;
    if (req.url === '/admin/sync-now' && req.method === 'POST') { sync('publikacja ręczna'); res.writeHead(204); return res.end(); }
    const r = await handler.request({ url: req.url, method: req.method, headers, body: body.length ? new Uint8Array(body) : undefined });
    res.writeHead(r.httpStatusCode, r.headers);
    res.end(Buffer.from(r.bytes));
    const file = (req.url.split('?')[0].match(/\/admin\/([a-z-]+\.php)$/) || [])[1];
    if (req.method === 'POST' && file && REASON[file] && r.httpStatusCode < 400 && file !== 'upload.php') schedule(REASON[file]);
  } catch (e) {
    console.error(e); res.writeHead(500); res.end(String(e?.stack || e));
  }
}).listen(PORT, '127.0.0.1', () => {
  console.log(`\nPanel KOMpetition.cc: http://localhost:${PORT}/admin/`);
  console.log(`Podgląd strony:       http://localhost:${PORT}/`);
  console.log(AUTO_PUSH ? 'Automatyczna publikacja na GitHub: WŁĄCZONA\n' : 'Automatyczna publikacja: wyłączona (AUTO_PUSH=0)\n');
});
