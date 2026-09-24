<?php
/* Wgrywanie zdjęć z edytora: tworzy wersje 480/800/1200 px (WebP) i zwraca adres. */
require __DIR__ . '/lib.php';
header('Content-Type: application/json; charset=utf-8');
if (!is_logged_in()) { http_response_code(401); echo json_encode(['error' => 'Sesja wygasła – zaloguj się ponownie.']); exit; }
check_csrf();
try {
    if (!gd_ok()) throw new RuntimeException('Serwer nie ma biblioteki GD.');
    $tmp = uploaded_tmp('file');
    if (!$tmp) throw new RuntimeException('Nie wybrano pliku.');
    $name = slugify(pathinfo((string)($_FILES['file']['name'] ?? 'zdjecie'), PATHINFO_FILENAME)) ?: 'zdjecie';
    $im = gd_open($tmp);
    $v = save_variants($im, '/assets/uploads/' . date('Y/m') . '/' . $name . '-' . substr(bin2hex(random_bytes(3)), 0, 6), [480, 800, 1200]);
    gd_free($im);
    $sizes = [];
    foreach ($v['set'] as [$src, $w]) $sizes[] = ['src' => $src, 'w' => $w];
    echo json_encode(['location' => end($v['set'])[0], 'srcset' => implode(', ', array_map(fn($x) => $x[0] . ' ' . $x[1] . 'w', $v['set'])), 'width' => $v['w'], 'height' => $v['h']]);
} catch (Throwable $e) {
    http_response_code(400);
    echo json_encode(['error' => $e->getMessage()]);
}
