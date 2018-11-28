# 漏洞散记
##  hackerone的子域劫持
> 作者能够劫持操作用户的过期域，在上面写自己喜欢的东西，而漏洞的关键则是instapage

> 漏洞价值:100$

借作者语：
> Instapage is a service that lets you build landing pages for your online marketing and promotion campaigns with ease. It offers features such as A/B Testing, multiple campaign management, easy page building, and a lot more!

而hackerone平台则是使用了这个service，让用户可以在他们自己的domain/subdomains上部署template

# 挖洞过程

hackerone鼓励世界各地的hacker去寻找Bug，并会给予勋章以证明，而作者想获得的是**Hacking Hackers**这个勋章，
所以才针对hackerone平台进行了一次渗透

在hackerone发布的**inscope domain list**中，存在一个**hacker.one**(现在已经访问不了了)吸引了作者的注意力，

然后就引发了**一个关键点**，作者打开网址后看见页面上输出了错误，而这错误作者辨识发现，此错误只能发生于以下情况：

![error](http://www.geekboy.ninja/blog/wp-content/uploads/2016/09/BxwVteM-768x339.jpg)

```
I come to know it was Instapage error which occurs when service get expired or domain or subdoamin not linked properly

```
作者想到，他自己可以发布一个template给instapage的过期用户域或者错误配置显示，而hackerone是instapage的用户
，那么进行自定义页面

作者到instapage上自己写了一个template，然后publish时更改参数，将提交的URL改变，改成www.hacker.one
则改变了页面

![success](http://www.geekboy.ninja/blog/wp-content/uploads/2016/09/insta-0day-768x258.jpg)

## POC:
```
POST /ajax/builder2/publish/2340488 HTTP/1.1
Host: app.instapage.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Referer: http://app.instapage.com/builder2?id=2340488
Content-Length: 31
Cookie: cookie_value
Connection: close

version=1&url=www.hacker.one
```

## 结语

其实总的来说，这并不算是hackerone的漏洞，而是instapage的漏洞，而hackerone很不幸是其用户，所以才导致
作者成功篡改了页面内容，从而拿到勋章，严格的讲，此漏洞应该属于instapage的越权，正因为如此，此漏洞才会被
hackerone平台定义为**100$**，github也是instapage的用户哦
