#!/usr/bin/env php
<?php
if ($argc != 2) {
  echo '[USAGE] cli_split_text.php (input-text)'."\n";
  exit;
}

$inputfile = $argv[1];
if (!file_exists($inputfile)) {
  echo "file not found: $inputfile\n";
  exit;
}
echo "[INPUT FILE] $inputfile\n";

// Include GLOBAL info
include_once dirname(__FILE__)."/fileinfo.ini.php";
// split
$result = [];
$text = file_get_contents($inputfile);
$text_a = explode("\n", $text);
$cnt2 = 0;
foreach ($text_a as $line) {
    if (trim($line) === '') continue;
    $line_a = explode("\t", $line);
    $word = trim(array_shift($line_a));
    $desc = trim(join("  ", $line_a));
    $ch = strtolower(substr($word, 0, 1));
    if (!preg_match('/^[a-zA-Z]/', $ch)) $ch = 'a';
    if (empty($result[$ch])) $result[$ch] = [];
    $result[$ch][] = [$word, $desc];
    $cnt2++;
    /*
    if (strpos($word, ',') !== FALSE) {
      echo "[warning] ".$word."\n";
    }
    */
}
// save
$cnt = 0;
foreach ($result as $key => $words) {
  echo $key."\n";
  $file = $dir_src."/{$key}.txt";
  $text = '';
  foreach ($words as $a) {
    $word = trim($a[0]);
    if ($word == '') continue;
    $desc = $a[1];
    $text .= "{$word}\t{$desc}\n";
    $cnt++;
  }
  file_put_contents($file, $text);
}
echo "words=$cnt ($cnt2)\n";
