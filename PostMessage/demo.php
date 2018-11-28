<iframe id="frame" src="https://mail.qq.com/cgi-bin/loginpage" height="1000" width="1000" onload=data()></iframe>

<script>
function data(){
    document.getElementById("frame").contentWindow.postMessage('{"action":"resize","width":"300","height":400}', "*");
}
</script>