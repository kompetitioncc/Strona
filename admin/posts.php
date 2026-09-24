<?php
require __DIR__ . '/lib.php';
require_login();
$ok = $err = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    try {
        $slug = (string)($_POST['slug'] ?? '');
        $all = posts_all();
        if (($_POST['action'] ?? '') === 'delete' && post_find($slug)) {
            $file = ROOT . "/blog/$slug/index.html";
            backup_file($file); backup_file(CONTENT_DIR . "/posts/$slug.html");
            @unlink($file); @rmdir(dirname($file)); @unlink(CONTENT_DIR . "/posts/$slug.html");
            posts_save(array_filter($all, fn($p) => $p['slug'] !== $slug));
            rebuild_all();
            $ok = 'Wpis usunięty (kopia została w „Kopiach zapasowych”).';
        } elseif (($_POST['action'] ?? '') === 'rebuild') {
            rebuild_all();
            $ok = 'Blog, strona główna, RSS i sitemapa zostały przebudowane.';
        }
    } catch (Throwable $e) { $err = $e->getMessage(); }
}
$posts = posts_all();
layout_start('Blog', 'posts.php');
?>
<div class="head"><h1>Blog</h1><a class="btn" href="post-edit.php">+ Nowy wpis</a></div>
<?= flash($ok, $err) ?>
<table class="list">
<thead><tr><th>Tytuł</th><th>Data</th><th>Status</th><th></th></tr></thead>
<tbody>
<?php foreach ($posts as $p): ?>
<tr>
  <td><a href="post-edit.php?slug=<?= urlencode($p['slug']) ?>"><strong><?= h($p['title']) ?></strong></a><br><small class="muted">/blog/<?= h($p['slug']) ?>/<?= !empty($p['kompedium']) ? ' · KOMpedium' : '' ?></small></td>
  <td><?= h(human_date($p['date'])) ?></td>
  <td><?= !empty($p['draft']) ? '<span class="pill">Szkic</span>' : '<span class="pill pill--ok">Opublikowany</span>' ?></td>
  <td class="actions">
    <a href="post-edit.php?slug=<?= urlencode($p['slug']) ?>">Edytuj</a>
    <?php if (empty($p['draft'])): ?><a href="/blog/<?= h($p['slug']) ?>/" target="_blank" rel="noopener">Zobacz ↗</a><?php else: ?><a href="preview.php?slug=<?= urlencode($p['slug']) ?>" target="_blank">Podgląd ↗</a><?php endif; ?>
    <form method="post" onsubmit="return confirm('Usunąć wpis „<?= h(addslashes($p['title'])) ?>”?')"><?= csrf_field() ?><input type="hidden" name="slug" value="<?= h($p['slug']) ?>"><button class="link danger" name="action" value="delete">Usuń</button></form>
  </td>
</tr>
<?php endforeach; ?>
</tbody>
</table>
<form method="post" class="mt"><?= csrf_field() ?><button class="btn btn--ghost" name="action" value="rebuild">Przebuduj blog</button> <span class="muted">Użyj, jeśli coś wygląda nieaktualnie.</span></form>
<?php layout_end();
