<?php
// FILE INFO
$dir_tools = dirname(__FILE__);
$dir_root = dirname($dir_tools);
$dir_src = "$dir_root/src";
$dir_out = "$dir_root/release";
$dir_template = "$dir_root/release-template";
//
$file_text_all = $dir_out."/ejdict-hand-utf8.txt";
$db_sqlite3 = $dir_out."/ejdict.sqlite3";
$db_schema = dirname(__FILE__)."/schema.sql";
$readme = $dir_out."/README.md";
$jsonfile = $dir_out."/ejdict.json";
