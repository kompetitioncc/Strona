<?php
require __DIR__ . '/lib.php';
require_login();
$posts = posts_all();
$drafts = count(array_filter($posts, fn($p) => !empty($p['draft'])));
$checks = [
    'PHP ' . PHP_VERSION => version_compare(PHP_VERSION, '8.0', '>='),
    'Biblioteka GD (obrazy)' => gd_ok(),
    'Zapis WebP' => webp_ok(),
    'Tytuł na grafikach OG' => atlas_ok(),
    'Zapis plików strony' => is_writable(ROOT . '/index.html') && is_writable(ROOT . '/blog'),
    'Zapis katalogu content/' => is_writable(CONTENT_DIR),
    'Zapis katalogu assets/uploads/' => is_writable(ROOT . '/assets/uploads') || is_writable(ROOT . '/assets'),
];
layout_start('Pulpit', 'index.php');
?>
<h1>Cześć, Kuba 👋</h1>
<div class="grid3">
  <a class="card tile" href="post-edit.php"><b>+ Nowy wpis</b><span>Dodaj artykuł na blog</span></a>
  <a class="card tile" href="posts.php"><b><?= count($posts) ?> wpisów</b><span><?= $drafts ? "$drafts szkic(e) · " : '' ?>zarządzaj blogiem</span></a>
  <a class="card tile" href="pages.php"><b>Edytuj stronę</b><span>Teksty, ceny, SEO</span></a>
</div>
<?php $sync = load_json(DATA_DIR . '/sync.json', null); ?>
<div class="card sync <?= $sync ? ($sync['ok'] ? 'sync--ok' : 'sync--bad') : '' ?>">
  <h2>Publikacja na stronie</h2>
  <?php if ($sync): ?><p><strong><?= h($sync['msg']) ?></strong><br><small class="muted"><?= h(date('d.m.Y H:i', strtotime($sync['time']))) ?></small></p>
  <?php else: ?><p class="muted">Po każdej zmianie w panelu (uruchomionym przez <code>npm run panel</code>) zmiany automatycznie trafiają na GitHub, a Cloudflare publikuje je w ok. minutę.</p><?php endif; ?>
  <button class="btn btn--ghost" type="button" onclick="fetch('/admin/sync-now',{method:'POST'}).then(()=>setTimeout(()=>location.reload(),4000));this.textContent='Publikuję…'">Opublikuj teraz</button>
</div>
<h2 class="mt">Stan serwera</h2>
<ul class="checks">
<?php foreach ($checks as $name => $ok): ?>
  <li class="<?= $ok ? 'ok' : 'bad' ?>"><?= $ok ? '✔' : '✖' ?> <?= h($name) ?></li>
<?php endforeach; ?>
</ul>
<p class="muted">Czerwone pozycje zgłoś hostingowi – bez nich część funkcji (np. wgrywanie zdjęć) nie zadziała.</p>
<?php layout_end();
