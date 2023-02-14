<?php
// Include GLOBAL info
include_once dirname(__FILE__)."/fileinfo.ini.php";

$files = glob($dir_src.'/*.txt');
$keys = [];
foreach ($files as $fname) {
    $txt = file_get_contents($fname);
    $a = explode("\n", $txt);
    foreach ($a as $line) {
        $line = trim($line);
        if ($line == '') { continue; }
        $line_a = explode("\t", $line);
        list($word, $mean) = $line_a;
        $word_a = explode(',', $word);
        foreach ($word_a as $word) {
            $word = trim($word);
            if (empty($keys[$word])) {
                $keys[$word] = $mean;
            } else {
                echo "+ [ERROR] $word\n";
                echo "- $keys[$word]\n\n";
                $keys[$word] .= " / $mean";
            }
        }
    }
}
/*
// to text
$txt = '';
foreach ($keys as $word => $mean) {
    $txt .= "$word\t$mean\n";
}
*/
// to json
$dic_json = json_encode($keys, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
file_put_contents($jsonfile, $dic_json);
echo "ok.\n";
