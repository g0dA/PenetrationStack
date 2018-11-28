# PostMessage
> 前言部分：

> 原本是没有接触过这个的，但是在挖洞的过程中，越来越多次的遇到跨域传输的问题，尤其在**Mapbox**的一次漏洞挖掘中，就卡在了窃取**token**上，而页面正好存在一个**message**的事件，这就让我想起**slack**的例子，所以就研究了一波，起码以后再遇到**PostMessage**能有办法测一测

正如所有的文章都会做的，先是介绍一下`PostMessage`

## 跨域方式
前端跨域方式很多，`PostMessage`就是其中一种，至于跨域是什么，建议参考文章[前端跨域的那些事](http://www.cnblogs.com/st-leslie/p/5958822.html)

`PostMessage`的跨域十分简单，分成发送端和接受端

发送端:
```
window.postMessage('test','*');
```
接收端:
```
window.addEventListener('message',function(event) {
	if(event.origin !== 'http://l-ang.com') return;
	console.log('message received:  ' + event.data,event);
},false);
```

## 在哪儿发送？在哪儿接收？
一般来说，发送端向着一个`frame`或者一个新的`window`中发送数据,而`frame`或者新的`window`中则是另一个域

`frame`:
```
<iframe id="to_fram" src="http://victim.com/server.php"></iframe>
```
假设我现在访问的是`attack.com`下面的页面，其中的`frame`就引用了另一个域的内容

那么我们发送端就可以这样发送数据
```
var to_hack = document.getElementById('to_fram');

to_hack.contentWindow.postMessage(""+document.getElementById('v').value,"*");
```
而`victim`中的接收端，则用来接受数据
```
<script type="text/javascript">

    window.addEventListener("message",receiveMessage, false);

    var debug = document.getElementById("debug");


    function receiveMessage(event){

        debug.innerHTML += "Data: " + event.data + "\n Orign: "+event.orign+"<br />";


    }           

</script>
```
## 安全性

这个就是涉及到一个问题，就是`PostMessage`和`addEventListener`的源，如果加验证的话，意思就是任何人构造一个新的`PostMessage`或者`addEventListener`然后引用的话，就可以任意发送或者传输东西？结果正是如此

所以`PostMessage`存在的最大的问题就在这，开发者往往贪图方便或者一时大意，便忘记了源或者验证不够准确，可以被轻易绕过

我们看下发送端
```
window.postMessage('test','*');
```
* test是传输的内容
* *则是传输的`targetOrigin`,这儿的*表示可以任意传输

再看下接收端:
```
    window.addEventListener("message",receiveMessage, false);

    var debug = document.getElementById("debug");

    function receiveMessage(event){

        debug.innerHTML += "Data: " + event.data + "\n Orign: "+event.orign+"<br />";
    }           

```
并没有对数据来源进行认证，我们看一份对来源进行了认证的代码:
```
window.addEventListener("message", function(message){
if(/^http://www.examplｅ.com$/.test(message.origin)){
console.log(message.data);
}
});
```
可以看到`origin`被正则所匹配，但是验证不够强，所以能被绕过

## 攻击结果
我个人的理解上，攻击方式分为两种，一种是伪造发送端，一种是伪造接收端

* 伪造发送端

向没有验证来源的`addEventListener`发送自定义的数据，当`addEventListener`存在以下两种条件时候，可进行跨域`xss`
1. `addEventListener`没有验证`origin`
2. 存在`innerHTML`输出


* 伪造接收端

`PostMessage`没有指定发送的`targetOrigin`，所以可以直接自写接收器，从而获取例如`token`之类的敏感信息

## 测试
个人觉得，在`PostMessage`这个检测上，`Chrom`比`Firefox`好点

`Chrom`:
![chrom](http://i1.piimg.com/567571/1fffb0f201995921.png)

`Firefox`:
![firefox](http://i1.piimg.com/567571/562a2eeeadd313f3.png)

`Chrom`能更快的定位到`message`

当发现存在`message`事件时，则尝试在`console`中运行`window.PostMessage("lang","*")`,然后调试出传输的值,这儿不建议测试发送数字

当调试出正确的值后，则自写页面挖掘漏洞

### 附注
写了一个`PostMessage`的环境，还有一个`demo`,其中`demo`是QQ邮箱的登录，这儿希望大家想一下，如果对方的接收端不仅仅是根据发送的数据调试，能够修改值，并写入属性中，是否就能产生一个`DOM XSS`

#### 参考
[*] [使用postMessage()和WebSocket重连来窃取你Slack的Token](http://www.tuicool.com/articles/AjYVnea)

[*] [使用window.postMessage实现跨域通信](http://blog.csdn.net/hr541659660/article/details/51778185)

[*] [前端跨域的那些事 ](http://www.cnblogs.com/st-leslie/p/5958822.html#document_domain)

[*] [PostMessage跨域漏洞分析](https://www.secpulse.com/archives/56637.html)
