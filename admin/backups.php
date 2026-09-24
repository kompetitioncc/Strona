<?php
require __DIR__ . '/lib.php';
require_login();
$ok = $err = null;
$bdir = CONTENT_DIR . '/backups';

function backup_target(string $dirName): ?string {
    $rel = str_replace('__', '/', $dirName);
    if (str_contains($rel, '..') || !preg_match('~\.(html|js|json)$~', $rel)) return null;
    $abs = ROOT . '/' . $rel;
    $dir = realpath(dirname($abs));
    return ($dir && str_starts_with($dir, ROOT)) ? $abs : null;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    try {
        $d = basename((string)($_POST['dir'] ?? '')); $f = basename((string)($_POST['file'] ?? ''));
        $src = "$bdir/$d/$f";
        $target = backup_target($d);
        if (!$target || !is_file($src)) throw new RuntimeException('Nie znaleziono kopii.');
        backup_file($target);
        write_file($target, (string)file_get_contents($src));
        if (str_starts_with($d, 'content__posts__')) rebuild_all();
        $ok = 'Przywrócono wersję z ' . str_replace('_', ' ', substr($f, 0, -5)) . '.';
    } catch (Throwable $e) { $err = $e->getMessage(); }
}

$groups = [];
foreach (glob("$bdir/*", GLOB_ONLYDIR) ?: [] as $dir) {
    $files = glob("$dir/*.html") ?: []; rsort($files);
    if ($files) $groups[basename($dir)] = array_map('basename', $files);
}
ksort($groups);
layout_start('Kopie zapasowe', 'backups.php');
?>
<h1>Kopie zapasowe</h1>
<p class="muted">Przed każdą zmianą panel zapisuje poprzednią wersję pliku (20 ostatnich na plik). Przywrócenie też tworzy kopię obecnej wersji – nic nie ginie.</p>
<?= flash($ok, $err) ?>
<?php if (!$groups): ?><p>Na razie brak kopii – pojawią się po pierwszej zmianie.</p><?php endif; ?>
<?php foreach ($groups as $dir => $files): ?>
<details class="card"><summary><strong><?= h(str_replace('__', '/', $dir)) ?></strong> <span class="muted">(<?= count($files) ?>)</span></summary>
  <table class="list"><?php foreach ($files as $f): ?>
    <tr><td><?= h(str_replace(['_', '.html'], [' ', ''], $f)) ?></td><td class="actions">
      <form method="post" onsubmit="return confirm('Przywrócić tę wersję?')"><?= csrf_field() ?><input type="hidden" name="dir" value="<?= h($dir) ?>"><input type="hidden" name="file" value="<?= h($f) ?>"><button class="link">Przywróć</button></form>
    </td></tr>
  <?php endforeach; ?></table>
</details>
<?php endforeach; ?>
<?php layout_end();
