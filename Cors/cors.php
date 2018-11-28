<?php
header('Access-Control-Allow-Origin: '.$_SERVER['HTTP_ORIGIN']);
header("Access-Control-Allow-Credentials: true");
$cookie = $_COOKIE['sessionid'];
if($cookie == 'corstest'){
$a = $_GET['a'];
 
if($a == 'getUserInfo') {
    echo json_encode(array(
        'uid' => 1,
        'name' => 'test',
    ));
} else {
    echo '';
}}
?>
