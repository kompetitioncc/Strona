<?php
require __DIR__ . '/lib.php';
require_login();
$first = !empty(auth_data()['must_change']);
$ok = $err = null;
$sfile = CONTENT_DIR . '/settings.json';
$s = load_json($sfile, []) + ['email' => 'kontakt@kompetition.cc', 'contactEndpoint' => '/api/kontakt.php', 'newsletterEndpoint' => '/api/newsletter.php',
    'ga4Id' => '', 'relay' => true, 'paymentLinks' => []];
$shop = load_json(CONTENT_DIR . '/shop.json', ['plans' => []]);

function write_config(array $s): void {
    $cfg = ['contactEndpoint' => $s['contactEndpoint'], 'newsletterEndpoint' => $s['newsletterEndpoint'], 'email' => $s['email'], 'relay' => (bool)$s['relay'], 'ga4Id' => $s['ga4Id'],
        'paymentLinks' => (object)array_filter((array)$s['paymentLinks'])];
    $js = "/* Plik generowany przez panel /admin → Ustawienia. Zmiany wprowadzaj w panelu. */\nwindow.KOM_CONFIG = "
        . json_encode($cfg, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . ";\n";
    backup_file(ROOT . '/assets/js/config.js');
    write_file(ROOT . '/assets/js/config.js', $js);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    try {
        if (($_POST['action'] ?? '') === 'password') {
            $cur = (string)($_POST['current'] ?? ''); $n1 = (string)($_POST['new1'] ?? ''); $n2 = (string)($_POST['new2'] ?? '');
            if (!password_verify($cur, auth_data()['hash'] ?? '')) throw new RuntimeException('Obecne hasło jest nieprawidłowe.');
            if (mb_strlen($n1) < 10) throw new RuntimeException('Nowe hasło musi mieć co najmniej 10 znaków.');
            if ($n1 !== $n2) throw new RuntimeException('Nowe hasła nie są takie same.');
            set_password($n1);
            $first = false;
            $ok = 'Hasło zmienione.';
        } elseif (($_POST['action'] ?? '') === 'site') {
            foreach (['email', 'ga4Id', 'contactEndpoint', 'newsletterEndpoint'] as $k) $s[$k] = trim((string)($_POST[$k] ?? ''));
            $pl = [];
            foreach ((array)($_POST['pay'] ?? []) as $k => $v) {
                $k = preg_replace('/[^a-z0-9-]/', '', (string)$k); $v = trim((string)$v);
                if ($v !== '' && !preg_match('~^https://~', $v)) throw new RuntimeException("Link płatności ($k) musi zaczynać się od https://");
                if ($k !== '') $pl[$k] = $v;
            }
            $s['paymentLinks'] = $pl;
            unset($s['pay_ftp'], $s['pay_vo2max']);
            $s['relay'] = !empty($_POST['relay']);
            if (!filter_var($s['email'], FILTER_VALIDATE_EMAIL)) throw new RuntimeException('Podaj poprawny e-mail.');
            if ($s['ga4Id'] !== '' && !preg_match('/^G-[A-Z0-9]{4,}$/', $s['ga4Id'])) throw new RuntimeException('Identyfikator GA4 ma postać G-XXXXXXX.');
            save_json($sfile, $s);
            write_config($s);
            $ok = 'Ustawienia zapisane.';
        }
    } catch (Throwable $e) { $err = $e->getMessage(); }
}
layout_start('Ustawienia', 'settings.php');
?>
<h1>Ustawienia</h1>
<?= flash($ok, $err) ?>
<?php if ($first): ?><p class="msg err">Pierwsze logowanie: ustaw teraz własne hasło. Dopiero potem pozostałe części panelu będą dostępne.</p><?php endif; ?>
<div class="grid2">
  <form method="post" class="card">
    <?= csrf_field() ?><input type="hidden" name="action" value="password">
    <h2>Hasło</h2>
    <label>Obecne hasło<input type="password" name="current" autocomplete="current-password" required></label>
    <label>Nowe hasło (min. 10 znaków)<input type="password" name="new1" autocomplete="new-password" minlength="10" required></label>
    <label>Powtórz nowe hasło<input type="password" name="new2" autocomplete="new-password" minlength="10" required></label>
    <button class="btn">Zmień hasło</button>
  </form>
  <?php if (!$first): ?>
  <form method="post" class="card">
    <?= csrf_field() ?><input type="hidden" name="action" value="site">
    <h2>Strona</h2>
    <label>E-mail, na który trafiają wiadomości z formularzy<input type="email" name="email" value="<?= h($s['email']) ?>" required></label>
    <label class="check"><input type="checkbox" name="relay" value="1" <?= !empty($s['relay']) ? 'checked' : '' ?>> Zapasowa wysyłka przez FormSubmit, gdy PHP nie odpowie</label>
    <label>Google Analytics 4 – identyfikator <small>(puste = brak statystyk i baneru zgody)</small><input name="ga4Id" value="<?= h($s['ga4Id']) ?>" placeholder="G-XXXXXXXXXX"></label>
    <details<?= array_filter((array)$s['paymentLinks']) ? '' : ' open' ?>><summary>Linki płatności Stripe (<?= count(array_filter((array)$s['paymentLinks'])) ?> ustawionych)</summary>
      <p class="muted small">Najprościej wygenerować je skryptem <code>tools/stripe-setup.mjs</code> (instrukcja w README). Puste pole = przycisk „Kup” prowadzi do formularza kontaktowego.</p>
      <table class="list"><?php foreach ($shop['plans'] as $slug => $pl): foreach ($pl['weeks'] as $w): $k = "$slug-$w"; ?>
        <tr><td><?= h($pl['name']) ?><br><small class="muted"><?= (int)$w ?> tyg. · <?= (int)$pl['prices'][(string)$w] ?> zł</small></td>
        <td><input type="url" name="pay[<?= h($k) ?>]" value="<?= h($s['paymentLinks'][$k] ?? '') ?>" placeholder="https://buy.stripe.com/..." style="margin:0"></td></tr>
      <?php endforeach; endforeach; ?></table>
    </details>
    <details><summary>Zaawansowane: adresy formularzy</summary>
      <label>Formularz kontaktowy<input name="contactEndpoint" value="<?= h($s['contactEndpoint']) ?>"></label>
      <label>Newsletter<input name="newsletterEndpoint" value="<?= h($s['newsletterEndpoint']) ?>"></label>
    </details>
    <button class="btn">Zapisz ustawienia</button>
  </form>
  <?php endif; ?>
</div>
<?php if (!$first): ?>
<div class="card mt">
  <h2>Newsletter</h2>
  <?php $nl = ROOT . '/api/data/newsletter.csv'; $cnt = is_file($nl) ? max(0, count(file($nl)) - 1) : 0; ?>
  <p>Zapisanych osób: <strong><?= $cnt ?></strong>. <?= $cnt ? '<a href="download.php?f=newsletter">Pobierz listę (CSV)</a> – zaimportujesz ją do MailerLite, Brevo itp.' : '' ?></p>
</div>
<?php endif; ?>
<?php layout_end();
