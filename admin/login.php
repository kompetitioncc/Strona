<?php
require __DIR__ . '/lib.php';
start_session();
if (is_logged_in()) { header('Location: index.php'); exit; }
$err = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    if (login_blocked()) $err = 'Za dużo nieudanych prób. Spróbuj ponownie za 15 minut.';
    elseif (login_attempt((string)($_POST['password'] ?? ''))) { header('Location: index.php'); exit; }
    else { usleep(800000); $err = 'Nieprawidłowe hasło.'; }
}
?><!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Logowanie · Panel KOMpetition</title><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="assets/admin.css"></head>
<body class="login">
<form method="post" class="card login-card">
  <img src="/assets/img/logo.webp" alt="KOMpetition.cc" height="56">
  <h1>Panel administracyjny</h1>
  <?= flash(null, $err) ?>
  <?= csrf_field() ?>
  <label>Hasło<input type="password" name="password" autocomplete="current-password" required autofocus></label>
  <button class="btn" type="submit">Zaloguj</button>
</form>
</body></html>
