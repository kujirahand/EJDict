<?php
// Include GLOBAL info
include_once dirname(__FILE__)."/fileinfo.ini.php";
//
$fname = $file_text_all;
$outname = $db_sqlite3;
//
unlink($outname); // remove sqlite database
$pdo = new PDO("sqlite:$outname");
$pdo->exec(file_get_contents($db_schema));
$pdo->exec("begin");
// make levels
$level_txt = file_get_contents(dirname(__FILE__).'/level.txt');
$level = [];
$level_lines = explode("\n", $level_txt);
foreach($level_lines as $line) {
  $w = explode("=", $line."=");
  $we = $w[0]; $wl = $w[1];
  // echo "$we===$wl\n";
  $level[$we] = $wl;
}

// prepare
$tpl = $pdo->prepare("INSERT INTO items (word, mean, level) VALUES (?, ?, ?)");

// read text
$count = 0;
$txt = file_get_contents($fname);
$lines = explode("\n", $txt);
foreach ($lines as $line) {
  $w = explode("\t", $line."\t");
  $word = trim($w[0]);
  if ($word == '') continue;
  $mean = trim($w[1]);
  // 同音異義語が「,」で区切られている
  $words = explode(",", $word);
  foreach ($words as $w2) {
    $w2 = trim($w2);
    $lev = isset($level[$word]) ? intval($level[$word]) : 0;
    $tpl->execute([$w2, $mean, $lev]);
    echo "-$w2\n";
    $count++;
  }
  // echo $mean."\n";
}
$pdo->exec("commit;");
echo "ok, $count\n";
