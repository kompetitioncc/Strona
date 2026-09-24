<?php
require __DIR__ . '/lib.php';
require_login();

$path = (string)($_GET['path'] ?? '/');
$file = page_file($path);
if (!$file) { http_response_code(404); exit('Tej strony nie można edytować.'); }
$pages = editable_pages();
$ok = $err = null;

function split_main(string $html): array {
    if (!preg_match('~(<main id="tresc">)(.*)(</main>)~s', $html, $m, PREG_OFFSET_CAPTURE)) throw new RuntimeException('Nie znaleziono sekcji <main> w pliku strony.');
    return [$m[2][0], $m[2][1]];
}
function main_scripts(string $main): array { preg_match_all('~<script\b.*?</script>~s', $main, $m); return $m[0]; }
function with_placeholders(string $main): string { $i = 0; return preg_replace_callback('~<script\b.*?</script>~s', function () use (&$i) { return '<!--KOMSCRIPT:' . $i++ . '-->'; }, $main) ?? $main; }
function meta_content(string $html, string $attr, string $name): string {
    return preg_match('~<meta ' . $attr . '="' . preg_quote($name, '~') . '" content="([^"]*)"~', $html, $m) ? html_entity_decode($m[1], ENT_QUOTES, 'UTF-8') : '';
}
function set_meta(string $html, string $attr, string $name, string $value): string {
    return preg_replace('~(<meta ' . $attr . '="' . preg_quote($name, '~') . '" content=")[^"]*(")~', '${1}' . str_replace(['\\', '$'], ['\\\\', '\\$'], h($value)) . '${2}', $html, 1) ?? $html;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    try {
        $html = (string)file_get_contents($file);
        [$oldMain, $off] = split_main($html);
        $scripts = main_scripts($oldMain);
        $new = (string)($_POST['main_html'] ?? '');
        if (trim($new) === '') throw new RuntimeException('Pusta treść – nic nie zapisano.');
        // sprzątanie po edytorze
        $new = preg_replace(['~\s(contenteditable|spellcheck)="[^"]*"~', '~\sdata-kom-[a-z-]+="[^"]*"~', '~<div class="kom-tools".*?</div>~s'], '', $new) ?? $new;
        $new = preg_replace('~<script\b.*?</script>~s', '', $new) ?? $new;   // nowe skrypty nie są dozwolone
        $new = preg_replace_callback('~<!--KOMSCRIPT:(\d+)-->~', fn($m) => $scripts[(int)$m[1]] ?? '', $new) ?? $new;
        $html = substr($html, 0, $off) . "\n" . trim($new) . "\n" . substr($html, $off + strlen($oldMain));

        $title = trim((string)($_POST['seo_title'] ?? ''));
        $desc = trim(preg_replace('/\s+/', ' ', (string)($_POST['desc'] ?? '')) ?? '');
        if ($title !== '') {
            $html = preg_replace('~<title>.*?</title>~s', '<title>' . str_replace(['\\', '$'], ['\\\\', '\\$'], h($title)) . '</title>', $html, 1) ?? $html;
            $html = set_meta($html, 'property', 'og:title', $title);
            $html = set_meta($html, 'property', 'og:image:alt', $title);
        }
        if ($desc !== '') {
            $html = set_meta($html, 'name', 'description', $desc);
            $html = set_meta($html, 'property', 'og:description', $desc);
        }
        backup_file($file);
        write_file($file, $html);
        touch_page($path);
        $ok = 'Zapisano. Zmiany są już widoczne na stronie (odśwież ją z Ctrl/Cmd + Shift + R).';
    } catch (Throwable $e) { $err = $e->getMessage(); }
}

$html = (string)file_get_contents($file);
[$main] = split_main($html);
$title = preg_match('~<title>(.*?)</title>~s', $html, $m) ? html_entity_decode($m[1], ENT_QUOTES, 'UTF-8') : '';
$desc = meta_content($html, 'name', 'description');

// dokument do edycji wizualnej: bez skryptów strony, ze skryptem edytora
$editDoc = substr_replace($html, "\n" . with_placeholders($main) . "\n", strpos($html, $main), strlen($main));
$editDoc = preg_replace('~<script\b.*?</script>~s', '', $editDoc) ?? $editDoc;
$editDoc = str_replace('</head>', '<link rel="stylesheet" href="assets/page-editor.css"></head>', $editDoc);
$editDoc = str_replace('</body>', '<script src="assets/page-editor.js"></script></body>', $editDoc);

layout_start('Edycja: ' . ($pages[$path]['name'] ?? $path), 'pages.php');
?>
<div class="head">
  <h1><?= h($pages[$path]['name'] ?? $path) ?></h1>
  <a class="btn btn--ghost" href="<?= h($path) ?>" target="_blank" rel="noopener">Zobacz stronę ↗</a>
</div>
<?= flash($ok, $err) ?>
<form method="post" id="page-form" class="page-editor">
  <?= csrf_field() ?>
  <input type="hidden" name="main_html" id="main_html">
  <div class="card seo-row">
    <label>Tytuł w Google <small class="cnt" data-for="seo_title" data-max="65"></small><input name="seo_title" id="seo_title" value="<?= h($title) ?>" maxlength="80"></label>
    <label>Opis w Google <small class="cnt" data-for="desc" data-min="110" data-max="160"></small><textarea name="desc" id="desc" rows="2" maxlength="220"><?= h($desc) ?></textarea></label>
  </div>
  <div class="toolbar">
    <div class="tabs"><button type="button" class="tab on" data-mode="visual">Edycja wizualna</button><button type="button" class="tab" data-mode="html">HTML (zaawansowane)</button></div>
    <span class="muted small" id="hint">Kliknij tekst, aby go zmienić · kliknij zdjęcie, aby je podmienić · dwuklik w link zmienia adres</span>
    <button class="btn" type="submit">Zapisz stronę</button>
  </div>
  <iframe id="frame" class="page-frame" title="Podgląd edytowanej strony" srcdoc="<?= h($editDoc) ?>"></iframe>
  <textarea id="html-src" class="html-src" hidden spellcheck="false"><?= h(with_placeholders($main)) ?></textarea>
  <p class="muted small">Komentarze &lt;!--KOMSCRIPT:n--&gt; w trybie HTML to miejsca skryptów (np. kalkulatora) – nie usuwaj ich. Przed każdym zapisem powstaje kopia zapasowa. Zmiany cen pamiętaj też wprowadzić w danych strukturalnych (poproś mnie o to przy okazji).</p>
</form>
<script>
const CSRF = <?= json_encode(csrf_token()) ?>;
window.KOM_UPLOAD = (file) => { const fd = new FormData(); fd.append('file', file); fd.append('csrf', CSRF); return fetch('upload.php', {method: 'POST', body: fd}).then(r => r.json()); };
const frame = document.getElementById('frame'), src = document.getElementById('html-src');
let mode = 'visual', dirty = false;
frame.addEventListener('load', () => { const d = frame.contentDocument; d.addEventListener('input', () => dirty = true); frame.style.height = Math.max(900, d.documentElement.scrollHeight) + 'px'; });
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  if (t.dataset.mode === mode) return;
  if (t.dataset.mode === 'html') { src.value = frame.contentWindow.KOM_getMain(); src.hidden = false; frame.hidden = true; }
  else { frame.contentWindow.KOM_setMain(src.value); src.hidden = true; frame.hidden = false; }
  mode = t.dataset.mode; document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x === t));
}));
src.addEventListener('input', () => dirty = true);
document.getElementById('page-form').addEventListener('submit', () => {
  document.getElementById('main_html').value = mode === 'html' ? src.value : frame.contentWindow.KOM_getMain();
  dirty = false;
});
window.addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
function upd() {
  document.querySelectorAll('.cnt').forEach(c => { const n = document.getElementById(c.dataset.for).value.length, min = +c.dataset.min || 0, max = +c.dataset.max;
    c.textContent = n + ' / ' + max; c.className = 'cnt ' + (n > max || n < min ? 'bad' : 'good'); });
}
document.querySelectorAll('#seo_title,#desc').forEach(e => e.addEventListener('input', () => { dirty = true; upd(); })); upd();
</script>
<?php layout_end();
