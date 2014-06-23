<?php
$afspath = $_SERVER["AeroFSdir"];
$credsfile = $afspath . '.credentials/SQL/csaye';
$file = file_get_contents($credsfile);
echo $file;
?>