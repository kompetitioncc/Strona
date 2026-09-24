<?php
/*
 * KOMpetition.cc — panel administracyjny: wspólna logika.
 * Renderowanie wpisów działa dokładnie tak samo jak generator strony (te same szablony w admin/templates).
 */
declare(strict_types=1);
mb_internal_encoding('UTF-8');
date_default_timezone_set('Europe/Warsaw');

define('ROOT', realpath(__DIR__ . '/..'));
define('ADMIN_DIR', __DIR__);
define('DATA_DIR', __DIR__ . '/data');
define('CONTENT_DIR', ROOT . '/content');
define('BASE_URL', 'https://kompetition.cc');
define('AUTH_FILE', DATA_DIR . '/auth.json');

/* ------------------------------------------------------------ sesja i logowanie */
function start_session(): void {
    if (session_status() === PHP_SESSION_ACTIVE) return;
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
    session_name('komadmin');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
    session_start();
}

function auth_data(): array {
    return is_file(AUTH_FILE) ? (json_decode((string)file_get_contents(AUTH_FILE), true) ?: []) : [];
}

function is_logged_in(): bool {
    start_session();
    return !empty($_SESSION['kom_admin']) && ($_SESSION['kom_ua'] ?? '') === ($_SERVER['HTTP_USER_AGENT'] ?? '');
}

function require_login(): void {
    if (!is_logged_in()) { header('Location: login.php'); exit; }
    $a = auth_data();
    if (!empty($a['must_change']) && basename($_SERVER['SCRIPT_NAME']) !== 'settings.php') {
        header('Location: settings.php?first=1'); exit;
    }
}

function client_ip(): string { return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0'; }

function login_blocked(): bool {
    $f = DATA_DIR . '/login_attempts.json';
    $all = is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : [];
    $recent = array_filter($all[client_ip()] ?? [], fn($t) => $t > time() - 900);
    return count($recent) >= 5;
}

function login_fail(): void {
    $f = DATA_DIR . '/login_attempts.json';
    $all = is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : [];
    foreach ($all as $ip => $ts) { $all[$ip] = array_values(array_filter($ts, fn($t) => $t > time() - 900)); if (!$all[$ip]) unset($all[$ip]); }
    $all[client_ip()][] = time();
    write_file($f, json_encode($all));
}

function login_attempt(string $password): bool {
    $a = auth_data();
    if (empty($a['hash']) || !password_verify($password, $a['hash'])) { login_fail(); return false; }
    start_session();
    session_regenerate_id(true);
    $_SESSION['kom_admin'] = true;
    $_SESSION['kom_ua'] = $_SERVER['HTTP_USER_AGENT'] ?? '';
    return true;
}

function set_password(string $password): void {
    write_file(AUTH_FILE, json_encode(['hash' => password_hash($password, PASSWORD_DEFAULT), 'must_change' => false, 'changed' => date('c')]));
}

function csrf_token(): string {
    start_session();
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(32));
    return $_SESSION['csrf'];
}
function csrf_field(): string { return '<input type="hidden" name="csrf" value="' . h(csrf_token()) . '">'; }
function check_csrf(): void {
    start_session();
    $t = $_POST['csrf'] ?? ($_SERVER['HTTP_X_CSRF'] ?? '');
    if (!is_string($t) || empty($_SESSION['csrf']) || !hash_equals($_SESSION['csrf'], $t)) {
        http_response_code(403); exit('Nieprawidłowy token bezpieczeństwa. Odśwież stronę i spróbuj ponownie.');
    }
}

/* ------------------------------------------------------------ pliki */
function h($s): string { return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

function write_file(string $path, string $data): void {
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0755, true) && !is_dir($dir)) throw new RuntimeException("Nie można utworzyć katalogu $dir");
    $tmp = $path . '.tmp' . bin2hex(random_bytes(4));
    if (file_put_contents($tmp, $data, LOCK_EX) === false) throw new RuntimeException("Nie można zapisać $path – sprawdź uprawnienia.");
    if (!rename($tmp, $path)) { @unlink($tmp); throw new RuntimeException("Nie można zapisać $path"); }
}

function backup_file(string $abs): void {
    if (!is_file($abs)) return;
    $rel = ltrim(str_replace(ROOT, '', $abs), '/');
    $dest = CONTENT_DIR . '/backups/' . str_replace('/', '__', $rel) . '/' . date('Y-m-d_H-i-s') . '.html';
    write_file($dest, (string)file_get_contents($abs));
    // zostaw 20 najnowszych kopii
    $all = glob(dirname($dest) . '/*.html') ?: [];
    rsort($all);
    foreach (array_slice($all, 20) as $old) @unlink($old);
}

function load_json(string $file, $default = []) {
    return is_file($file) ? (json_decode((string)file_get_contents($file), true) ?? $default) : $default;
}
function save_json(string $file, $data): void {
    write_file($file, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT));
}

/* ------------------------------------------------------------ tekst */
function slugify(string $s): string {
    $map = ['ą'=>'a','ć'=>'c','ę'=>'e','ł'=>'l','ń'=>'n','ó'=>'o','ś'=>'s','ź'=>'z','ż'=>'z','Ą'=>'a','Ć'=>'c','Ę'=>'e','Ł'=>'l','Ń'=>'n','Ó'=>'o','Ś'=>'s','Ź'=>'z','Ż'=>'z'];
    $s = mb_strtolower(strtr($s, $map));
    $s = preg_replace('/[^a-z0-9]+/', '-', $s) ?? '';
    return trim(substr($s, 0, 70), '-');
}

const MONTHS = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
function human_date(string $iso): string { $t = strtotime($iso); return (int)date('j', $t) . ' ' . MONTHS[(int)date('n', $t) - 1] . ' ' . date('Y', $t); }
function iso_tz(string $iso): string { return date('Y-m-d\TH:i:sP', strtotime($iso)); }

/* ------------------------------------------------------------ szablony (ta sama semantyka co generator) */
function fill(string $tpl, array $v, array $raw = []): string {
    $parts = preg_split('~(<script type="application/ld\+json">.*?</script>)~s', $tpl, -1, PREG_SPLIT_DELIM_CAPTURE);
    $out = '';
    foreach ($parts as $i => $part) {
        if ($i % 2 === 1) {
            foreach ($v as $k => $val) {
                if (is_int($val)) $part = str_replace('"{{' . $k . '}}"', (string)$val, $part);
                $part = str_replace('{{' . $k . '}}', substr(json_encode((string)$val, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), 1, -1), $part);
            }
        } else {
            foreach ($raw as $k => $val) $part = str_replace('{{{' . $k . '}}}', $val, $part);
            foreach ($v as $k => $val) $part = str_replace('{{' . $k . '}}', h($val), $part);
        }
        $out .= $part;
    }
    return $out;
}

/* ------------------------------------------------------------ HTML wpisu */
function dom_load(string $html): DOMDocument {
    $d = new DOMDocument('1.0', 'UTF-8');
    libxml_use_internal_errors(true);
    $d->loadHTML('<?xml encoding="UTF-8"><div id="__root">' . $html . '</div>', LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();
    return $d;
}
function dom_inner(DOMDocument $d): string {
    $root = $d->getElementById('__root');
    $out = '';
    foreach ($root->childNodes as $c) $out .= $d->saveHTML($c);
    return $out;
}

/** Czyści HTML z edytora, dodaje id nagłówków i responsywne obrazy. Zwraca [html, toc]. */
function process_body(string $html): array {
    $d = dom_load($html);
    $x = new DOMXPath($d);
    foreach ($x->query('//script|//style|//iframe[not(contains(@src,"youtube.com") or contains(@src,"youtube-nocookie.com") or contains(@src,"player.vimeo.com"))]|//object|//embed') as $n) $n->parentNode->removeChild($n);
    foreach ($x->query('//*') as $el) {
        /** @var DOMElement $el */
        foreach (iterator_to_array($el->attributes) as $a) {
            if (stripos($a->name, 'on') === 0 || in_array($a->name, ['data-mce-src', 'data-mce-href', 'data-mce-style', 'data-mce-selected', 'contenteditable'], true)) $el->removeAttribute($a->name);
            if (in_array($a->name, ['href', 'src'], true) && preg_match('~^\s*javascript:~i', $a->value)) $el->removeAttribute($a->name);
        }
    }
    // obrazy z /assets/uploads -> srcset
    foreach ($x->query('//img') as $img) {
        /** @var DOMElement $img */
        $src = $img->getAttribute('src');
        if (preg_match('~^/assets/uploads/(.+)-(\d+)\.(webp|jpg)$~', $src, $m)) {
            $set = [];
            foreach ([480, 800, 1200] as $w) {
                $f = "/assets/uploads/{$m[1]}-$w.{$m[3]}";
                if (is_file(ROOT . $f)) $set[] = "$f {$w}w";
            }
            if ($set) { $img->setAttribute('srcset', implode(', ', $set)); $img->setAttribute('sizes', '(min-width:1040px) 700px, 100vw'); }
            $info = @getimagesize(ROOT . $src);
            if ($info) { $img->setAttribute('width', (string)$info[0]); $img->setAttribute('height', (string)$info[1]); }
        }
        $img->removeAttribute('style');
        if (!$img->hasAttribute('alt')) $img->setAttribute('alt', '');
        $img->setAttribute('loading', 'lazy'); $img->setAttribute('decoding', 'async');
    }
    // tabele przewijane na telefonie, linki zewnętrzne
    foreach ($x->query('//a[@href]') as $a) {
        $href = $a->getAttribute('href');
        if (preg_match('~^https?://~', $href) && stripos($href, 'kompetition.cc') === false) $a->setAttribute('rel', 'noopener');
    }
    // id nagłówków + spis treści
    $toc = []; $used = [];
    foreach ($x->query('//h2|//h3') as $hd) {
        /** @var DOMElement $hd */
        $txt = rtrim(trim($hd->textContent), ':');
        $base = $hd->getAttribute('id') ?: (substr(slugify($txt), 0, 48) ?: 'sekcja');
        $sid = $base; $i = 2;
        while (isset($used[$sid])) $sid = $base . '-' . $i++;
        $used[$sid] = true;
        $hd->setAttribute('id', $sid);
        if ($hd->nodeName === 'h2') $toc[] = [$sid, $txt];
    }
    return [dom_inner($d), $toc];
}

function word_count(string $html): int {
    $t = trim(preg_replace('/\s+/u', ' ', html_entity_decode(strip_tags(str_replace('<', ' <', $html)), ENT_QUOTES, 'UTF-8')) ?? '');
    return $t === '' ? 0 : count(explode(' ', $t));
}

function toc_html(array $toc): string {
    if (count($toc) < 3) return '';
    $li = '';
    foreach ($toc as [$id, $t]) $li .= '<li><a href="#' . h($id) . '">' . h($t) . '</a></li>';
    return '<aside class="toc" aria-label="Spis treści"><details open><summary>Spis treści</summary><ol>' . $li . '</ol></details></aside>';
}

/* ------------------------------------------------------------ obrazy (GD) */
function gd_free($im): void { if (PHP_VERSION_ID < 80000) imagedestroy($im); }
function gd_ok(): bool { return function_exists('imagecreatetruecolor'); }
function webp_ok(): bool { return function_exists('imagewebp'); }
/* Atlas liter: fonty wyrenderowane do PNG + metryki w JSON (admin/fonts/og-*.png|json). */
function atlas_ok(): bool { return gd_ok() && function_exists('imagecreatefrompng') && is_file(ADMIN_DIR . '/fonts/og-title.png') && is_file(ADMIN_DIR . '/fonts/og-kicker.png'); }
function atlas_load(string $name): array {
    static $cache = [];
    if (!isset($cache[$name])) {
        $img = imagecreatefrompng(ADMIN_DIR . "/fonts/$name.png");
        imagealphablending($img, false); imagesavealpha($img, true);
        $cache[$name] = [$img, json_decode((string)file_get_contents(ADMIN_DIR . "/fonts/$name.json"), true)];
    }
    return $cache[$name];
}
function atlas_width(string $name, string $text): float {
    [, $m] = atlas_load($name); $w = 0.0;
    foreach (mb_str_split($text) as $ch) $w += $m['glyphs'][$ch][5] ?? $m['glyphs']['?'][5];
    return $w;
}
function atlas_text($im, string $name, string $text, int $x, int $y): void {
    [$src, $m] = atlas_load($name);
    imagealphablending($im, true);
    $cx = (float)$x;
    foreach (mb_str_split($text) as $ch) {
        $g = $m['glyphs'][$ch] ?? $m['glyphs']['?'];
        [$gx, $gy, $gw, $gh, $left, $adv] = $g;
        if ($ch !== ' ') imagecopy($im, $src, (int)round($cx + $left), $y, $gx, $gy, $gw, $gh);
        $cx += $adv;
    }
}

function gd_open(string $file) {
    $info = @getimagesize($file);
    if (!$info) throw new RuntimeException('To nie jest obsługiwany obraz.');
    switch ($info[2]) {
        case IMAGETYPE_JPEG: $im = imagecreatefromjpeg($file);
            if (function_exists('exif_read_data')) {
                $e = @exif_read_data($file);
                $o = $e['Orientation'] ?? 1;
                if ($o == 3) $im = imagerotate($im, 180, 0); elseif ($o == 6) $im = imagerotate($im, -90, 0); elseif ($o == 8) $im = imagerotate($im, 90, 0);
            }
            return $im;
        case IMAGETYPE_PNG: $im = imagecreatefrompng($file); imagepalettetotruecolor($im); imagealphablending($im, true); imagesavealpha($im, true); return $im;
        case IMAGETYPE_WEBP: if (function_exists('imagecreatefromwebp')) return imagecreatefromwebp($file); break;
        case IMAGETYPE_GIF: $im = imagecreatefromgif($file); imagepalettetotruecolor($im); return $im;
    }
    throw new RuntimeException('Nieobsługiwany format obrazu (użyj JPG, PNG lub WebP).');
}

/** Przycina do proporcji (0 = bez przycinania) i zapisuje zestaw szerokości. Zwraca [[ścieżka_www, szer], ...] + wysokość. */
function save_variants($im, string $baseRel, array $widths, float $ratio = 0, int $q = 78): array {
    $W = imagesx($im); $H = imagesy($im);
    $sx = 0; $sy = 0; $sw = $W; $sh = $H;
    if ($ratio > 0) {
        if ($W / $H > $ratio) { $sw = (int)round($H * $ratio); $sx = (int)(($W - $sw) / 2); }
        else { $sh = (int)round($W / $ratio); $sy = (int)(($H - $sh) / 3); }
    }
    $ext = webp_ok() ? 'webp' : 'jpg';
    $out = []; $lastH = 0;
    foreach (array_unique(array_map(fn($w) => min($w, $sw), $widths)) as $w) {
        $hgt = (int)round($sh * $w / $sw);
        $dst = imagecreatetruecolor($w, $hgt);
        imagealphablending($dst, false); imagesavealpha($dst, true);
        imagefill($dst, 0, 0, imagecolorallocatealpha($dst, 255, 255, 255, $ext === 'webp' ? 127 : 0));
        imagealphablending($dst, true);
        imagecopyresampled($dst, $im, 0, 0, $sx, $sy, $w, $hgt, $sw, $sh);
        $rel = "$baseRel-$w.$ext";
        @mkdir(dirname(ROOT . $rel), 0755, true);
        $ok = $ext === 'webp' ? imagewebp($dst, ROOT . $rel, $q) : imagejpeg($dst, ROOT . $rel, 82);
        gd_free($dst);
        if (!$ok) throw new RuntimeException('Nie udało się zapisać obrazu – sprawdź uprawnienia katalogu assets/uploads.');
        $out[] = [$rel, $w]; $lastH = $hgt;
    }
    return ['set' => $out, 'h' => $lastH, 'w' => end($out)[1]];
}

function img_tag(array $v, string $alt, string $sizes, bool $eager = false): string {
    $srcset = implode(', ', array_map(fn($x) => $x[0] . ' ' . $x[1] . 'w', $v['set']));
    $src = count($v['set']) >= 3 ? $v['set'][count($v['set']) - 2][0] : end($v['set'])[0];
    $load = $eager ? ' fetchpriority="high" decoding="async"' : ' loading="lazy" decoding="async"';
    return '<img src="' . h($src) . '" srcset="' . h($srcset) . '" sizes="' . h($sizes) . '" width="' . $v['w'] . '" height="' . $v['h'] . '" alt="' . h($alt) . '"' . $load . '>';
}

function uploaded_tmp(string $field): ?string {
    if (empty($_FILES[$field]) || ($_FILES[$field]['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_NO_FILE) return null;
    if ($_FILES[$field]['error'] !== UPLOAD_ERR_OK) throw new RuntimeException('Błąd wgrywania pliku (kod ' . $_FILES[$field]['error'] . '). Plik może być za duży.');
    if ($_FILES[$field]['size'] > 20 * 1024 * 1024) throw new RuntimeException('Plik jest większy niż 20 MB.');
    return $_FILES[$field]['tmp_name'];
}

/** Okładka wpisu: wersja 2:1 do artykułu, 16:10 do kart, grafika OG 1200×630. */
function make_cover(string $tmp, string $slug, string $title, string $alt, bool $kompedium): array {
    if (!gd_ok()) throw new RuntimeException('Serwer nie ma biblioteki GD – poproś hosting o jej włączenie.');
    $im = gd_open($tmp);
    $stamp = date('YmdHis');
    $main = save_variants($im, "/assets/uploads/covers/$slug-$stamp", [480, 800, 1200, 1600], 2.0);
    $card = save_variants($im, "/assets/uploads/covers/$slug-$stamp-karta", [480, 800], 1.6);
    $og = make_og($im, $slug, $title, $kompedium ? 'KOMpedium wiedzy · KOMpetition.cc' : 'Blog KOMpetition.cc');
    gd_free($im);
    return [
        'cover_html' => img_tag($main, $alt, '(min-width:1240px) 1130px, 100vw', true),
        'card_img' => img_tag($card, '', '(min-width:980px) 380px, (min-width:640px) 50vw, 100vw'),
        'cover_main' => end($main['set'])[0],
        'og' => $og,
    ];
}

function make_og($src, string $slug, string $title, string $kicker): string {
    $W = 1200; $H = 630;
    $im = imagecreatetruecolor($W, $H);
    $sw = imagesx($src); $sh = imagesy($src);
    if ($sw / $sh > $W / $H) { $cw = (int)($sh * $W / $H); $cx = (int)(($sw - $cw) / 2); $cy = 0; $ch = $sh; }
    else { $ch = (int)($sw * $H / $W); $cy = (int)(($sh - $ch) / 3); $cx = 0; $cw = $sw; }
    imagecopyresampled($im, $src, 0, 0, $cx, $cy, $W, $H, $cw, $ch);
    $black = imagecreatetruecolor(8, $H); imagefill($black, 0, 0, imagecolorallocate($black, 11, 11, 12));
    for ($x = 0; $x < $W; $x += 8) {   // gradient przyciemniający od lewej (bez kanału alfa – działa na każdym GD)
        imagecopymerge($im, $black, $x, 0, 0, 0, 8, $H, (int)round((235 - 150 * $x / $W) / 255 * 100));
    }
    gd_free($black);
    $yellow = imagecolorallocate($im, 255, 213, 0); $white = imagecolorallocate($im, 255, 255, 255); $grey = imagecolorallocate($im, 235, 235, 235);
    imagefilledrectangle($im, 64, 150, 134, 158, $yellow);
    // tekst z atlasu liter (PNG) – działa na każdym GD, także bez FreeType
    if (atlas_ok()) {
        atlas_text($im, 'og-kicker', mb_strtoupper($kicker), 64, 176);
        $words = preg_split('/\s+/u', mb_strtoupper(trim($title))) ?: []; $lines = []; $cur = '';
        foreach ($words as $w) {
            $t = trim("$cur $w");
            if (atlas_width('og-title', $t) > 900 && $cur !== '') { $lines[] = $cur; $cur = $w; } else $cur = $t;
        }
        $lines[] = $cur;
        $y = 230;
        foreach (array_slice($lines, 0, 4) as $ln) { atlas_text($im, 'og-title', $ln, 62, $y); $y += 86; }
    }
    $logo = ADMIN_DIR . '/assets/logo-white.png';
    if (is_file($logo)) {
        $lg = imagecreatefrompng($logo); $lw = 190; $lh = (int)(imagesy($lg) * $lw / imagesx($lg));
        imagecopyresampled($im, $lg, $W - $lw - 56, 48, 0, 0, $lw, $lh, imagesx($lg), imagesy($lg));
        gd_free($lg);
    }
    $rel = "/assets/og/blog-$slug.jpg";
    imagejpeg($im, ROOT . $rel, 84);
    gd_free($im);
    return $rel . '?v=' . date('YmdHis');
}

/* ------------------------------------------------------------ wpisy */
function posts_all(): array {
    $p = load_json(CONTENT_DIR . '/posts.json', []);
    usort($p, fn($a, $b) => strcmp($b['date'], $a['date']));
    return $p;
}
function posts_save(array $posts): void { save_json(CONTENT_DIR . '/posts.json', array_values($posts)); }
function post_find(string $slug): ?array { foreach (posts_all() as $p) if ($p['slug'] === $slug) return $p; return null; }
function post_body(string $slug): string { $f = CONTENT_DIR . "/posts/$slug.html"; return is_file($f) ? (string)file_get_contents($f) : ''; }

function post_vars(array $p, string $body, string $htag = 'h3'): array {
    $words = word_count($body);
    $mins = max(2, (int)ceil($words / 200));
    return ['SLUG' => $p['slug'], 'TITLE' => $p['title'], 'HEADLINE' => mb_substr($p['title'], 0, 110), 'SEO_TITLE' => $p['seo_title'],
        'DESC' => $p['desc'], 'SHORT' => $p['short'], 'DATE_DAY' => substr($p['date'], 0, 10), 'DATE_HUMAN' => human_date($p['date']),
        'DATE_ISO' => iso_tz($p['date']), 'UPDATED_ISO' => iso_tz($p['updated'] ?? $p['date']), 'MINS' => $mins, 'WORDS' => $words,
        'OG' => $p['og'] ?: '/assets/og/default.jpg', 'HTAG' => $htag];
}

function card_html(array $p, string $htag = 'h3'): string {
    static $tpl = null;
    $tpl = $tpl ?? (string)file_get_contents(ADMIN_DIR . '/templates/card.html');
    $body = post_body($p['slug']);
    return fill($tpl, post_vars($p, $body, $htag), ['CARD_IMG' => $p['card_img'] ?? '', 'BADGE' => !empty($p['kompedium']) ? '<span class="badge">KOMpedium</span>' : '']);
}

function render_post(array $p, array $published, bool $preview = false): string {
    $tpl = (string)file_get_contents(ADMIN_DIR . '/templates/post.html');
    $body = post_body($p['slug']);
    [, $toc] = process_body($body);
    $related = array_slice(array_values(array_filter($published, fn($q) => $q['slug'] !== $p['slug'])), 0, 3);
    $raw = [
        'EYEBROW' => !empty($p['kompedium']) ? '<p class="eyebrow">KOMpedium wiedzy</p>' : '',
        'COVER' => !empty($p['cover_html']) ? '<div class="post-cover">' . $p['cover_html'] . '</div>' : '',
        'BODY' => $body, 'TOC' => toc_html($toc),
        'RELATED' => implode('', array_map(fn($q) => card_html($q), $related)),
    ];
    $html = fill($tpl, post_vars($p, $body), $raw);
    if ($preview) $html = str_replace('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">', '<meta name="robots" content="noindex">', $html);
    return $html;
}

function replace_region(string $html, string $name, string $content): string {
    return preg_replace_callback('~<!--' . $name . '-->.*?<!--/' . $name . '-->~s', fn() => "<!--$name-->$content<!--/$name-->", $html) ?? $html;
}

/** Przebudowuje wszystkie wpisy, listę bloga, sekcję „najnowsze” na stronie głównej, RSS i sitemapę. */
function rebuild_all(): void {
    $all = posts_all();
    $pub = array_values(array_filter($all, fn($p) => empty($p['draft'])));
    foreach ($all as $p) {
        $file = ROOT . '/blog/' . $p['slug'] . '/index.html';
        if (!empty($p['draft'])) { if (is_file($file)) { backup_file($file); @unlink($file); @rmdir(dirname($file)); } continue; }
        write_file($file, render_post($p, $pub));
    }
    $blog = ROOT . '/blog/index.html';
    write_file($blog, replace_region((string)file_get_contents($blog), 'POSTS:ALL', implode('', array_map(fn($p) => card_html($p, 'h2'), $pub))));
    $home = ROOT . '/index.html';
    write_file($home, replace_region((string)file_get_contents($home), 'POSTS:LATEST', implode('', array_map(fn($p) => card_html($p), array_slice($pub, 0, 3)))));
    // RSS
    $items = '';
    foreach ($pub as $p) {
        $u = BASE_URL . '/blog/' . $p['slug'] . '/';
        $items .= '<item><title>' . h($p['title']) . '</title><link>' . $u . '</link><guid>' . $u . '</guid><pubDate>' . date('D, d M Y H:i:s O', strtotime($p['date'])) . '</pubDate><description>' . h($p['desc']) . '</description></item>';
    }
    write_file(ROOT . '/blog/feed.xml', '<?xml version="1.0" encoding="UTF-8"?>' . "\n" . '<rss version="2.0"><channel><title>Blog KOMpetition.cc</title><link>' . BASE_URL . '/blog/</link><description>Wiedza o treningu kolarskim – Jakub Obitko</description><language>pl</language>' . $items . "</channel></rss>\n");
    rebuild_sitemap($pub);
}

function rebuild_sitemap(?array $pub = null): void {
    $pub = $pub ?? array_values(array_filter(posts_all(), fn($p) => empty($p['draft'])));
    $pages = load_json(CONTENT_DIR . '/pages.json', []);
    $x = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'];
    $row = function (string $path, string $lastmod, array $imgs) {
        $im = '';
        foreach ($imgs as $i) if ($i) $im .= '<image:image><image:loc>' . h(BASE_URL . $i) . '</image:loc></image:image>';
        return '  <url><loc>' . h(BASE_URL . $path) . '</loc><lastmod>' . h(substr($lastmod, 0, 10)) . '</lastmod>' . $im . '</url>';
    };
    foreach ($pages as $pg) $x[] = $row($pg['path'], $pg['lastmod'], $pg['images'] ?? []);
    foreach ($pub as $p) $x[] = $row('/blog/' . $p['slug'] . '/', $p['updated'] ?? $p['date'], [$p['cover_main'] ?? '']);
    $x[] = '</urlset>';
    write_file(ROOT . '/sitemap.xml', implode("\n", $x) . "\n");
}

/* ------------------------------------------------------------ strony statyczne */
function editable_pages(): array {
    $names = ['/' => 'Strona główna', '/opieka-trenerska/' => 'Opieka trenerska', '/plany-treningowe/' => 'Plany treningowe',
        '/plany-treningowe/poprawa-ftp/' => 'Plan – poprawa FTP', '/plany-treningowe/poprawa-vo2max/' => 'Plan – poprawa VO2max',
        '/o-mnie/' => 'O mnie', '/kontakt/' => 'Kontakt', '/blog/' => 'Blog – nagłówek listy', '/cp-kalkulator/' => 'Kalkulator CP',
        '/kalkulator-ge/' => 'Kalkulator GE', '/regulamin/' => 'Regulamin', '/polityka-prywatnosci/' => 'Polityka prywatności',
        '/plany-treningowe/' => 'Sklep – plany treningowe'];
    foreach ((load_json(CONTENT_DIR . '/shop.json', ['plans' => []])['plans'] ?? []) as $slug => $pl) $names["/plany-treningowe/$slug/"] = 'Plan: ' . $pl['name'];
    $out = [];
    foreach (load_json(CONTENT_DIR . '/pages.json', []) as $pg) {
        $out[$pg['path']] = ['path' => $pg['path'], 'name' => $names[$pg['path']] ?? $pg['path'], 'lastmod' => $pg['lastmod']];
    }
    return $out;
}

function page_file(string $path): ?string {
    if (!isset(editable_pages()[$path])) return null;
    $f = $path === '/' ? ROOT . '/index.html' : ROOT . '/' . trim($path, '/') . '/index.html';
    $real = realpath($f);
    return ($real && str_starts_with($real, ROOT . '/')) ? $real : null;
}

function touch_page(string $path): void {
    $pages = load_json(CONTENT_DIR . '/pages.json', []);
    foreach ($pages as &$pg) if ($pg['path'] === $path) $pg['lastmod'] = date('Y-m-d');
    save_json(CONTENT_DIR . '/pages.json', $pages);
    rebuild_sitemap();
}

/* ------------------------------------------------------------ widok */
function layout_start(string $title, string $active = ''): void {
    $nav = ['index.php' => 'Pulpit', 'posts.php' => 'Blog', 'pages.php' => 'Strony', 'settings.php' => 'Ustawienia', 'backups.php' => 'Kopie zapasowe'];
    echo '<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">';
    echo '<title>' . h($title) . ' · Panel KOMpetition</title><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="assets/admin.css"></head><body>';
    echo '<header class="top"><a class="brand" href="index.php"><img src="/assets/img/logo-white.webp" alt="" height="30"> Panel</a><nav>';
    foreach ($nav as $f => $n) echo '<a href="' . $f . '"' . ($active === $f ? ' class="on"' : '') . '>' . $n . '</a>';
    echo '<a href="/" target="_blank" rel="noopener">Zobacz stronę ↗</a><a href="logout.php">Wyloguj</a></nav></header><main class="wrap">';
}
function layout_end(): void { echo '</main></body></html>'; }
function flash(?string $ok = null, ?string $err = null): string {
    return ($ok ? '<p class="msg ok">' . h($ok) . '</p>' : '') . ($err ? '<p class="msg err">' . h($err) . '</p>' : '');
}
