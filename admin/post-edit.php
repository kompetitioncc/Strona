<?php
require __DIR__ . '/lib.php';
require_login();

$slug = (string)($_GET['slug'] ?? '');
$post = $slug ? post_find($slug) : null;
if ($slug && !$post) { http_response_code(404); exit('Nie ma takiego wpisu.'); }
$isNew = !$post;
$post = $post ?? ['slug' => '', 'title' => '', 'seo_title' => '', 'desc' => '', 'short' => '', 'date' => date('Y-m-d\TH:i'),
    'updated' => date('Y-m-d\TH:i'), 'kompedium' => false, 'og' => '', 'cover_html' => '', 'card_img' => '', 'cover_main' => '', 'cover_alt' => '', 'draft' => true];
$body = $isNew ? '' : post_body($post['slug']);
$ok = $err = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    try {
        $title = trim((string)($_POST['title'] ?? ''));
        if ($title === '') throw new RuntimeException('Tytuł jest wymagany.');
        $newSlug = $isNew ? slugify(trim((string)($_POST['slug'] ?? '')) ?: $title) : $post['slug'];
        if ($newSlug === '') throw new RuntimeException('Nie udało się utworzyć adresu wpisu – zmień tytuł.');
        if ($isNew && (post_find($newSlug) || is_dir(ROOT . "/blog/$newSlug"))) throw new RuntimeException("Adres /blog/$newSlug/ jest już zajęty – zmień go.");

        $post['slug'] = $newSlug;
        $post['title'] = $title;
        $post['seo_title'] = trim((string)($_POST['seo_title'] ?? '')) ?: mb_substr($title, 0, 50) . ' | KOMpetition';
        $post['desc'] = trim(preg_replace('/\s+/', ' ', (string)($_POST['desc'] ?? '')) ?? '');
        if ($post['desc'] === '') throw new RuntimeException('Opis (meta description) jest wymagany – to tekst widoczny w Google.');
        $post['short'] = trim((string)($_POST['short'] ?? '')) ?: implode(' ', array_slice(explode(' ', $title), 0, 3));
        $post['date'] = date('Y-m-d\TH:i', strtotime((string)($_POST['date'] ?? 'now')) ?: time());
        $post['updated'] = date('Y-m-d\TH:i');
        $post['kompedium'] = !empty($_POST['kompedium']);
        $post['cover_alt'] = trim((string)($_POST['cover_alt'] ?? '')) ?: $title;
        $post['draft'] = ($_POST['action'] ?? '') !== 'publish';

        [$bodyClean] = process_body((string)($_POST['body'] ?? ''));
        write_file(CONTENT_DIR . "/posts/$newSlug.html", $bodyClean);
        $body = $bodyClean;

        if ($tmp = uploaded_tmp('cover')) {
            $post = array_merge($post, make_cover($tmp, $newSlug, $title, $post['cover_alt'], $post['kompedium']));
        } elseif (!empty($post['cover_html'])) {
            // aktualizacja opisu alternatywnego istniejącej okładki
            $post['cover_html'] = preg_replace('/ alt="[^"]*"/', ' alt="' . h($post['cover_alt']) . '"', $post['cover_html'], 1);
        }

        $all = array_filter(posts_all(), fn($p) => $p['slug'] !== $newSlug);
        $all[] = $post;
        posts_save($all);
        rebuild_all();
        if ($isNew) { header('Location: post-edit.php?slug=' . urlencode($newSlug) . '&saved=' . ($post['draft'] ? 'draft' : 'pub')); exit; }
        $ok = $post['draft'] ? 'Szkic zapisany. Nie jest widoczny publicznie.' : 'Opublikowano! Wpis jest już na stronie.';
    } catch (Throwable $e) { $err = $e->getMessage(); }
}
if (($_GET['saved'] ?? '') === 'draft') $ok = 'Szkic zapisany. Nie jest widoczny publicznie.';
if (($_GET['saved'] ?? '') === 'pub') $ok = 'Opublikowano! Wpis jest już na stronie.';

layout_start($isNew ? 'Nowy wpis' : 'Edycja wpisu', 'posts.php');
?>
<div class="head">
  <h1><?= $isNew ? 'Nowy wpis' : 'Edycja wpisu' ?></h1>
  <?php if (!$isNew): ?><div><?= empty($post['draft']) ? '<a class="btn btn--ghost" target="_blank" rel="noopener" href="/blog/' . h($post['slug']) . '/">Zobacz na stronie ↗</a>' : '<a class="btn btn--ghost" target="_blank" href="preview.php?slug=' . urlencode($post['slug']) . '">Podgląd szkicu ↗</a>' ?></div><?php endif; ?>
</div>
<?= flash($ok, $err) ?>
<form method="post" enctype="multipart/form-data" class="editor" id="post-form">
  <?= csrf_field() ?>
  <div class="editor__main">
    <label>Tytuł (nagłówek H1)<input name="title" value="<?= h($post['title']) ?>" required maxlength="140" data-count></label>
    <?php if ($isNew): ?>
    <label>Adres wpisu <small>(zostaw puste – utworzy się z tytułu)</small><span class="prefix">kompetition.cc/blog/<input name="slug" value="" pattern="[a-z0-9-]*" placeholder="np. trening-w-upale"></span></label>
    <?php else: ?>
    <p class="muted">Adres: <a href="/blog/<?= h($post['slug']) ?>/" target="_blank">/blog/<?= h($post['slug']) ?>/</a> (adresu opublikowanego wpisu nie zmieniamy – to chroni pozycje w Google)</p>
    <?php endif; ?>
    <label>Treść</label>
    <textarea name="body" id="body"><?= h($body) ?></textarea>
  </div>
  <aside class="editor__side">
    <div class="card">
      <h3>Publikacja</h3>
      <p>Status: <?= !empty($post['draft']) ? '<span class="pill">Szkic</span>' : '<span class="pill pill--ok">Opublikowany</span>' ?></p>
      <label>Data publikacji<input type="datetime-local" name="date" value="<?= h(substr($post['date'], 0, 16)) ?>"></label>
      <label class="check"><input type="checkbox" name="kompedium" value="1" <?= !empty($post['kompedium']) ? 'checked' : '' ?>> Seria „KOMpedium wiedzy”</label>
      <div class="btns">
        <?php if (!empty($post['draft'])): ?>
        <button class="btn btn--ghost" name="action" value="draft">Zapisz szkic</button>
        <button class="btn" name="action" value="publish">Opublikuj</button>
        <?php else: ?>
        <button class="btn" name="action" value="publish">Zapisz zmiany</button>
        <button class="link danger" name="action" value="draft" onclick="return confirm('Wycofać wpis ze strony (zmieni się w szkic)?')">Wycofaj publikację</button>
        <?php endif; ?>
      </div>
    </div>
    <div class="card">
      <h3>SEO</h3>
      <label>Tytuł w Google <small class="cnt" data-for="seo_title" data-max="65"></small><input name="seo_title" id="seo_title" value="<?= h($post['seo_title']) ?>" maxlength="70" placeholder="Temat – konkret | KOMpetition"></label>
      <label>Opis w Google <small class="cnt" data-for="desc" data-min="110" data-max="160"></small><textarea name="desc" id="desc" rows="4" maxlength="200" required><?= h($post['desc']) ?></textarea></label>
      <label>Krótka nazwa (okruszki)<input name="short" value="<?= h($post['short']) ?>" maxlength="40"></label>
      <div class="serp"><span class="serp__t" id="serp-t"></span><span class="serp__u">kompetition.cc › blog</span><span class="serp__d" id="serp-d"></span></div>
    </div>
    <div class="card">
      <h3>Okładka</h3>
      <?php if (!empty($post['cover_html'])): ?><div class="cover-prev"><?= $post['cover_html'] ?></div><?php endif; ?>
      <label>Wgraj <?= !empty($post['cover_html']) ? 'nową ' : '' ?>okładkę (JPG/PNG/WebP, poziomą)<input type="file" name="cover" accept="image/jpeg,image/png,image/webp"></label>
      <label>Opis zdjęcia (alt)<input name="cover_alt" value="<?= h($post['cover_alt']) ?>" maxlength="160"></label>
      <p class="muted small">Automatycznie powstaną wersje responsywne i grafika do udostępnień (OG) z tytułem.</p>
    </div>
  </aside>
</form>

<script src="https://cdn.jsdelivr.net/npm/tinymce@7/tinymce.min.js" referrerpolicy="origin"></script>
<script>
const CSRF = <?= json_encode(csrf_token()) ?>;
tinymce.init({
  selector: '#body', license_key: 'gpl', language: 'pl', language_url: 'https://cdn.jsdelivr.net/npm/tinymce-i18n@24/langs7/pl.js',
  height: 760, menubar: false, branding: false, promotion: false, convert_urls: false, relative_urls: false,
  plugins: 'lists link image table autolink code fullscreen wordcount searchreplace media',
  toolbar: 'blocks | bold italic | bullist numlist blockquote | link image media table | cta sources | removeformat code fullscreen',
  block_formats: 'Akapit=p; Nagłówek sekcji (H2)=h2; Podnagłówek (H3)=h3; Mały nagłówek (H4)=h4',
  content_css: '/assets/css/style.css', body_class: 'prose', content_style: 'body{padding:24px;max-width:760px;margin:auto}',
  image_caption: true, image_dimensions: false, object_resizing: false, table_default_attributes: {}, table_default_styles: {},
  images_upload_handler: (blob) => new Promise((resolve, reject) => {
    const fd = new FormData(); fd.append('file', blob.blob(), blob.filename()); fd.append('csrf', CSRF);
    fetch('upload.php', {method: 'POST', body: fd}).then(r => r.json()).then(j => j.location ? resolve(j.location) : reject(j.error || 'Błąd wgrywania')).catch(() => reject('Błąd połączenia'));
  }),
  setup: (ed) => {
    ed.ui.registry.addButton('cta', {text: 'Przycisk CTA', onAction: () => {
      const t = prompt('Tekst przycisku:', 'Umów darmową konsultację'); if (!t) return;
      const u = prompt('Link:', '/kontakt/#konsultacja'); if (!u) return;
      ed.insertContent('<p><a class="btn" href="' + u.replace(/"/g, '&quot;') + '">' + ed.dom.encode(t) + '</a></p>');
    }});
    ed.ui.registry.addButton('sources', {text: 'Źródła', onAction: () => ed.insertContent('<h2>Źródła Naukowe</h2><ul class="sources"><li><p>Autor A. i wsp. (rok). Tytuł. <em>Czasopismo</em>. <a href="https://doi.org/">doi:</a></p></li></ul>')});
  }
});
// liczniki i podgląd wyniku w Google
function upd() {
  document.querySelectorAll('.cnt').forEach(c => {
    const el = document.getElementById(c.dataset.for), n = el.value.length, min = +c.dataset.min || 0, max = +c.dataset.max;
    c.textContent = n + ' / ' + max; c.className = 'cnt ' + (n > max || n < min ? 'bad' : 'good');
  });
  const t = document.getElementById('seo_title').value || document.querySelector('[name=title]').value;
  document.getElementById('serp-t').textContent = t; document.getElementById('serp-d').textContent = document.getElementById('desc').value;
}
document.querySelectorAll('input,textarea').forEach(e => e.addEventListener('input', upd)); upd();
let dirty = false; document.getElementById('post-form').addEventListener('input', () => dirty = true);
window.addEventListener('beforeunload', e => { if (dirty || (tinymce.activeEditor && tinymce.activeEditor.isDirty())) { e.preventDefault(); e.returnValue = ''; } });
document.getElementById('post-form').addEventListener('submit', () => { dirty = false; tinymce.activeEditor && tinymce.activeEditor.setDirty(false); });
</script>
<?php layout_end();
