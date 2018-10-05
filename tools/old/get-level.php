<?php
$pdo = new PDO("sqlite:ejdict.sqlite3");
$a = $pdo->prepare('SELECT * FROM items WHERE level>=1');
$a->execute();
$aa = $a->fetchAll();
foreach ($aa as $n) {
  echo $n['word']."=".$n['level']."\n";
}

