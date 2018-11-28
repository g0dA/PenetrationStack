# 漏洞散记
## HRS的运用
> 一个没给钱的漏洞，然而我觉的怎么也应该给点钱才对，而且普遍的价格应该在300$左右，但是不扯这个了，这个个漏洞是个CRLF的漏洞，测试的时候很少见到，但却又得去测看看，很麻烦但是却也是很典型的一个漏洞，所以在hackerone看到这个漏洞后，还是记下来，学习学习

> 漏洞价值:0$

> 源漏洞:[#171473](https://hackerone.com/reports/171473)


# 挖洞过程

仔细看了漏洞后，真的是不发钱确实感觉有点太坑了，GET型的HRS，很容易就能衍生出**XSS**，**Open redirect**，居然没钱，真的是我的天

Crlf挖掘的话其实大部分个人还是靠的扫描器，毕竟其产生的原因也是因为在开发过程中没有过滤**\r**,**\n**这类的换行符，导致输出污染了其他的HTTP头

不知道作者到底是手工测试还是扫描器挖掘的大致情况就是:

一个Get的请求后，添加了一个**payload**:
```
%0d%0a
```
然后后面添加了
```
Myheader:NewHeader
```
结果在response里面产生了新的http头参数，也就是说作者将想要的东西注入到了Http头里面去了，那么作者完全可以重写一个Http头，导致很多延伸漏洞的产生

可以看一下作者的实际情况：

![1](https://thumbnail0.baidupcs.com/thumbnail/7d8e6f85b591206c52797cfca7122a81?fid=473100949-250528-238899451705836&time=1483542000&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-3L1%2FL7vq61%2FXeArpVudv3vDoqnU%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=92607971937398352&dp-callid=0&size=c710_u400&quality=100)

# 结语

HRS实际上是个很厉害的漏洞，只要开发者一不注意就很容易导致严重的后果，所以将其添加到渗透测试中是一个必要的选项，而关于其资料，个人比较推荐推酷的这篇文章:[《CRLF Injection漏洞的利用与实例分析》](http://www.tuicool.com/articles/aaqAvuY)
