<?php
    $afspath = $_SERVER["AeroFSdir"];
    $credsfile = $afspath . '.credentials/SQL/csaye';
    $file = file_get_contents($credsfile);
    //echo "The host is: ";
    //echo $file[0];
    //echo $file;

    $server = mysql_connect($host, $username, $password);
    $connection = mysql_select_db($database, $server);

    $myquery = "
    SELECT v.jd, v.mnvel FROM velocities v INNER JOIN observations o ON  o.observation_id=v.observation_id WHERE o.object='10700';
    ";
    /*
    $myquery = "
    SELECT  `date`, `close` FROM  `data2`
    ";
    */

    $query = mysql_query($myquery);
    
    if ( ! $query ) {
        echo mysql_error();
        die;
    }
    
    $data = array();
    
    for ($x = 0; $x < mysql_num_rows($query); $x++) {
        $data[] = mysql_fetch_assoc($query);
    }
    
    echo json_encode($data);     
     
    mysql_close($server);

?>