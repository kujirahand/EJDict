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
        # 表現の統一 (Issue #35)
        # 《俗語》(俗語) → 《俗》
        $mean = str_replace(['《俗語》', '(俗語)'], '《俗》', $mean);
        # 《英国》(英国)(英) → 《英》
        $mean = str_replace(['《英国》', '(英国)', '(英)'], '《英》', $mean);
        # 《米国》(米国)(米) → 《米》
        $mean = str_replace(['《米国》', '(米国)', '(米)'], '《米》', $mean);
        # 《文語》(文語) → 《文》
        $mean = str_replace(['《文語》', '(文語)'], '《文》', $mean);
        # 《口語》(口語)《口》 → 《話》
        $mean = str_replace(['《口語》', '(口語)', '《口》'], '《話》', $mean);
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
