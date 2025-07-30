<?php
$root = dirname(__DIR__);
// check files
$files = glob("$root/src/*.txt");
// check lines
$flagError = FALSE;
foreach ($files as $file) {
    $fname = basename($file);
    echo "--- $fname ---\n";
    $txt = file_get_contents($file);
    $lines = explode("\n", $txt);
    $result = [];
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === "") {
            continue;
        }
        $cells = explode("\t", $line);
        $org_word = $word = $cells[0];
        $org_mean = $mean = $cells[1];
        # 「‘を'」を「を」に統一
        # $mean = preg_replace("/‘([あ-ん]{1,4})'/", "'$1'", $mean);
        $mean = preg_replace("#[‘\']([あ-ん]{1,2})[\'\']#u", "$1", $mean);
        # 全角記号を半角記号に揃える
        $mean = mb_convert_kana($mean, "rsKV", "UTF-8");
        # 再構築
        $result[] = "$word\t$mean";
        # report
        if ($mean != $org_mean) {
            echo "[FIX] $word\n";
            echo "    - $org_mean\n";
            echo "    + $mean\n";
        }
    }
    $txt = implode("\n", $result);
    file_put_contents($file, $txt);
}
echo "ok\n";
exit(0);
