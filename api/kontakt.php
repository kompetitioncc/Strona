<?php
/*
 * Obsługa formularza kontaktowego KOMpetition.cc
 * Wymaga hostingu z PHP i działającą funkcją mail() (standard na większości polskich hostingów).
 */
declare(strict_types=1);
date_default_timezone_set('Europe/Warsaw');

const RECIPIENT = 'kontakt@kompetition.cc';
const FROM      = 'formularz@kompetition.cc'; // adres w Twojej domenie (lepsza dostarczalność)

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function out(bool $ok, string $error = '', int $code = 200): void {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(false, 'Niedozwolona metoda.', 405);

// pułapka na boty
if (!empty($_POST['website'])) out(true);

// prosty limit: 1 wiadomość na 30 s z jednej sesji
session_start();
if (isset($_SESSION['last_send']) && time() - $_SESSION['last_send'] < 30) out(false, 'Odczekaj chwilę przed ponownym wysłaniem.', 429);

$clean = fn(string $k, int $max) => trim(mb_substr(str_replace(["\r", "\0"], '', (string)($_POST[$k] ?? '')), 0, $max));
$imie     = $clean('imie', 80);
$nazwisko = $clean('nazwisko', 80);
$email    = $clean('email', 160);
$msg      = $clean('wiadomosc', 5000);
$page     = $clean('page', 200);

if ($imie === '' || $nazwisko === '' || $msg === '') out(false, 'Uzupełnij wszystkie wymagane pola.', 422);
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) out(false, 'Podaj poprawny adres e-mail.', 422);
if (empty($_POST['zgoda'])) out(false, 'Zaznacz zgodę na przetwarzanie danych.', 422);

$oneLine = fn(string $s) => preg_replace('/[\n\r]+/', ' ', $s);
$subject = '=?UTF-8?B?' . base64_encode('Nowa wiadomość ze strony: ' . $oneLine("$imie $nazwisko")) . '?=';
$body = "Imię i nazwisko: $imie $nazwisko\nE-mail: $email\nStrona: $page\nData: " . date('Y-m-d H:i') . "\n\n$msg\n";
$headers = implode("\r\n", [
    'From: KOMpetition.cc <' . FROM . '>',
    'Reply-To: ' . $oneLine($email),
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

if (!mail(RECIPIENT, $subject, $body, $headers, '-f' . FROM)) out(false, 'Serwer nie mógł wysłać wiadomości.', 500);

$_SESSION['last_send'] = time();
out(true);
