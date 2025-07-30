<?php
//
// しっかりタブ区切りデータになっているか確認する
//
$root = dirname(__DIR__);
// check files
$files = glob("$root/src/*.txt");
for ($i = ord("a"); $i <= ord("z"); $i++) {
    $a = chr($i);
    $full = "$root/src/$a.txt";
    if (file_exists($full)) {
        continue;
    }
    echo "[ERROR] file not found: $full\n";
    exit(-1);
}
// check lines
$flagError = FALSE;
foreach ($files as $file) {
    $fname = basename($file);
    echo "--- $fname ---\n";
    $txt = file_get_contents($file);
    $lines = explode("\n", $txt);
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === "") {
            continue;
        }
        $cells = explode("\t", $line);
        if (count($cells) === 2) {
            continue;
        }
        echo "[ERROR]($fname) $line\n";
        $flagError = TRUE;
    }
}
if ($flagError) {
    echo "ng\n";
    exit(1);
}
echo "ok\n";
exit(0);
