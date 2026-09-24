<?php
require __DIR__ . '/lib.php';
start_session();
$_SESSION = [];
session_destroy();
header('Location: login.php');
