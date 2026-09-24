<?php
require __DIR__ . '/lib.php';
require_login();
layout_start('Strony', 'pages.php');
?>
<div class="head"><h1>Strony</h1></div>
<p class="muted">Kliknij „Edytuj”, a strona otworzy się w trybie edycji: klikasz w tekst i po prostu go zmieniasz. Zdjęcia podmienisz kliknięciem w obrazek.</p>
<table class="list">
<thead><tr><th>Strona</th><th>Ostatnia zmiana</th><th></th></tr></thead>
<tbody>
<?php foreach (editable_pages() as $pg): ?>
<tr>
  <td><a href="page-edit.php?path=<?= urlencode($pg['path']) ?>"><strong><?= h($pg['name']) ?></strong></a><br><small class="muted"><?= h($pg['path']) ?></small></td>
  <td><?= h($pg['lastmod']) ?></td>
  <td class="actions"><a href="page-edit.php?path=<?= urlencode($pg['path']) ?>">Edytuj</a><a href="<?= h($pg['path']) ?>" target="_blank" rel="noopener">Zobacz ↗</a></td>
</tr>
<?php endforeach; ?>
</tbody>
</table>
<p class="muted">Wpisy na blogu edytujesz w zakładce <a href="posts.php">Blog</a>.</p>
<?php layout_end();
