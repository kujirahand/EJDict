<?php
include __DIR__.'/fileinfo.ini.php';

// mkdir
echo "--- mkdir ---: $dir_out\n";
mkdir($dir_out, 0755, true);

// release
$files = glob($dir_out."/*");
foreach ($files as $f) {
  echo "delete $f\n";
  unlink($f);
}

// root
$files = glob("$dir_root/*.zip");
foreach ($files as $f) {
  echo "delete $f\n";
  unlink($f);
}
echo "ok\n";
