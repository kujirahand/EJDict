<?php
include __DIR__.'/fileinfo.ini.php';

$text = "";
$files = glob($dir_src."/*.txt");
sort($files);
foreach ($files as $f) {
  echo "$f\n";
  $s = file_get_contents($f);
  $s = str_replace("\r\n", "\n", $s);
  $text .= trim($s). "\n";
}
file_put_contents($file_text_all, $text);
echo "ok\n";

// count
$a = explode("\n", $text);
echo count($a)." lines\n";
