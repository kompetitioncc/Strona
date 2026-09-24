<?php
require __DIR__ . '/lib.php';
require_login();
$p = post_find((string)($_GET['slug'] ?? ''));
if (!$p) { http_response_code(404); exit('Nie ma takiego wpisu.'); }
$pub = array_values(array_filter(posts_all(), fn($q) => empty($q['draft'])));
header('X-Robots-Tag: noindex');
$html = render_post($p, $pub, true);
$bar = '<div style="position:fixed;top:0;left:0;right:0;z-index:999;background:#ffd500;color:#0b0b0c;font:600 14px/1.4 system-ui;padding:8px 16px;text-align:center">PODGLĄD SZKICU – niewidoczny publicznie · <a href="post-edit.php?slug=' . urlencode($p['slug']) . '" style="color:inherit">wróć do edycji</a></div>';
echo str_replace('<body>', '<body>' . $bar, $html);
