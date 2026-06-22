<?php
//
// TSVの単語データ(src/*.txt)のWord(一番左)に重複がないかチェックする
//

$root = dirname(__DIR__);
$src_dir = "$root/src";
$files = glob("$src_dir/*.txt");
sort($files);

if (empty($files)) {
    echo "[ERROR] No text files found in $src_dir\n";
    exit(1);
}

$words = [];
$flagError = FALSE;

foreach ($files as $file) {
    $fname = basename($file);
    echo "--- $fname ---\n";
    $txt = file_get_contents($file);
    $lines = explode("\n", $txt);
    $lineNo = 0;
    
    foreach ($lines as $line) {
        $lineNo++;
        $line = trim($line);
        if ($line === "") {
            continue;
        }
        
        $cells = explode("\t", $line);
        $word = isset($cells[0]) ? trim($cells[0]) : '';
        if ($word === '') {
            continue;
        }
        
        // 重複チェック
        if (isset($words[$word])) {
            $prev = $words[$word];
            echo "[ERROR] Duplicate word '$word' found in $fname:$lineNo (previously defined in {$prev['file']}:{$prev['line']})\n";
            $flagError = TRUE;
        } else {
            $words[$word] = [
                'file' => $fname,
                'line' => $lineNo
            ];
        }
    }
}

if ($flagError) {
    echo "ng\n";
    exit(1);
}

echo "ok\n";
exit(0);
