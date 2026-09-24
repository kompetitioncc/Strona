<?php
require __DIR__ . '/lib.php';
require_login();
if (($_GET['f'] ?? '') !== 'newsletter') { http_response_code(404); exit; }
$file = ROOT . '/api/data/newsletter.csv';
if (!is_file($file)) { http_response_code(404); exit('Brak zapisów.'); }
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="newsletter-' . date('Y-m-d') . '.csv"');
echo "\xEF\xBB\xBF";   // BOM dla Excela
readfile($file);
