<?php
include __DIR__ . "/fileinfo.ini.php";

$txt_zip = "ejdic-hand-txt.zip";
$sql_zip = "ejdic-hand-sqlite.zip";
chdir($dir_out);
system("zip -r $txt_zip README.txt ejdict-hand-utf8.txt");
system("zip -r $sql_zip README.txt ejdict.sqlite3");
