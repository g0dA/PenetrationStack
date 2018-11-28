

<html>

    <head>

        <title>Postmessage_server demo</title>

    </head>

    <body>

        <div id="debug"> Ready to receive data...</div>


        <script type="text/javascript">

            window.addEventListener("message",receiveMessage, false);

            var debug = document.getElementById("debug");


            function receiveMessage(event){

                debug.innerHTML += "Data: " + event.data + "\n Orign: "+event.orign+"<br />";


            }           

        </script>

    </body>

</html>