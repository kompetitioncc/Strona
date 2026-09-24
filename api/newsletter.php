<?php
/*
 * Zapis do newslettera KOMpetition.cc
 * Adresy trafiają do pliku api/data/newsletter.csv (katalog zablokowany w .htaccess)
 * oraz przychodzi powiadomienie e-mail. Plik CSV zaimportujesz do MailerLite / Brevo itp.
 */
declare(strict_types=1);
date_default_timezone_set('Europe/Warsaw');

const RECIPIENT = 'kontakt@kompetition.cc';
const FROM      = 'formularz@kompetition.cc';

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function out(bool $ok, string $error = '', int $code = 200): void {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(false, 'Niedozwolona metoda.', 405);
if (!empty($_POST['website'])) out(true);

$email = trim(mb_substr((string)($_POST['email'] ?? ''), 0, 160));
$name  = trim(mb_substr(preg_replace('/[\r\n,;"]+/', ' ', (string)($_POST['imie'] ?? '')), 0, 80));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) out(false, 'Podaj poprawny adres e-mail.', 422);

$dir = __DIR__ . '/data';
if (!is_dir($dir)) mkdir($dir, 0750, true);
$file = $dir . '/newsletter.csv';

$existing = is_file($file) ? file_get_contents($file) : '';
if (stripos($existing, ',' . $email . ',') === false) {
    $isNew = !is_file($file);
    $fh = fopen($file, 'a');
    if ($fh === false) out(false, 'Błąd zapisu na serwerze.', 500);
    flock($fh, LOCK_EX);
    if ($isNew) fwrite($fh, "data,email,imie\n");
    fwrite($fh, date('Y-m-d H:i') . ',' . $email . ',' . $name . "\n");
    flock($fh, LOCK_UN);
    fclose($fh);

    @mail(RECIPIENT, '=?UTF-8?B?' . base64_encode('Nowy zapis do newslettera') . '?=',
        "Nowy zapis: $email $name", 'From: KOMpetition.cc <' . FROM . ">\r\nContent-Type: text/plain; charset=UTF-8");
}
out(true);
