<?php
include __DIR__ . "/fileinfo.ini.php";

// zip files
$txt_zip = "$dir_root/ejdic-hand-txt.zip";
$sql_zip = "$dir_root/ejdic-hand-sqlite.zip";
$json_zip = "$dir_root/ejdic-hand-json.zip";

$files = [
    [
        "org" => "ejdict-hand-utf8.txt",
        "zip" => "ejdic-hand-txt.zip",
    ],
    [
        "org" => "ejdict.sqlite3",
        "zip" => "ejdic-hand-sqlite.zip",
    ],
    [
        "org" => "ejdict.json",
        "zip" => "ejdic-hand-json.zip",
    ],
];
// copy
system("cp '$dir_tools/README.md' '$readme'");

// execute zip
foreach ($files as $conf) {
    $org = $dir_out . "/" . $conf["org"];
    $zip = $dir_root . "/" . $conf["zip"];
    if (file_exists($zip)) {
        unlink($zip);
    }
    system("zip -j $zip '$dir_out/README.md' '$org'");
}
echo "ok\n";

