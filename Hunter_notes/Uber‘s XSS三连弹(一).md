# 漏洞散记
##  Uber的Xss第一弹
> 很有趣的XSS三连弹，作者分别在April，June,August提交了三次XSS，且完全利用在同一个地方，然而
就是通过了审查，并分别赚取了$3,000，$7,500，$5,000，简直无情，而且漏洞提交厂商是Uber，但实际影响最大
的却是另一个厂家:**readme.io**


> 漏洞价值:3000$

>源地址:[#125027](https://hackerone.com/reports/125027)

## 漏洞过程

### 直接就是关键
作者上来就提出了一个payload：
```
https://developer.uber.com/docs/deep-linking?q=wrtz{{7*7}}
```
这个是检测AngularJS存在的xss使用的方法(此处手动@长短短，感谢说明)

我们不管作者是通过(1)此种方法检测还是先是(2)发现了AngularJS的特征然后验证，总之就是作者的payload得到了
执行，页面源码中的路径是：**wrtz49**

借作者语:

**uses an Angular sandbox escape to obtain arbitrary JavaScript execution and execute alert(1). It's designed to work in Internet Explorer 11, but the technique could probably be used to target other browsers**

总是就是你如果不是IE11，那么就乖乖弹窗吧

接着作者便提供了完整的payload:

**https://developer.uber.com/docs/deep-linking?q=wrtz{{(_="".sub).call.call({}[$="constructor"].getOwnPropertyDescriptor(_.__proto__,$).value,0,"alert(1)")()}}zzzz**

成功弹窗:

![xss](https://hackerone-attachments.s3.amazonaws.com/production/000/080/391/2b7e7114b53c85300ad7415e7c194467ba9747cf/Screen_Shot_2016-03-22_at_16.51.13.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJFXIS7KJADBA4QQA%2F20161209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20161209T045219Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=945189f7cdb5fec3750ff00261e7cd20e0fb0cdfb0d3cacb69b1f5636e71b0dc)

## 干货（加精）

对我来说，如上利用了一个新颖的攻击技术，此种技术对照的的是新颖的JS技术，此次漏洞挖掘的突破口在于，作者
的知识储备十分惊人，也许也可以说是非常关注新兴技术，并将其带入漏洞挖掘之中,漏洞的利用很简单，就是对照payload
但是却在挖掘处此种漏洞的地方展示了高超的实力，能多方面尝试，并定位到漏洞应该使用的攻击技术

贴上这种**Client-side xss**的攻击技术报告:

[ XSS without HTML: Client-Side Template Injection with AngularJS
](https://hackerone.com/redirect?signature=49c7114e65f27ab7700511ac15aaa633cf22a68b&url=http%3A%2F%2Fblog.portswigger.net%2F2016%2F01%2Fxss-without-html-client-side-template.html)

## 后续
Uber处理了这个Bug，方法是找到了**readme.io**处理了**Angular templates**，接着Uber请求作者能
否进行深入测试，以探求发现薄弱之处，由此引出三连弹的第二弹

#### 原文:

**readme.io just released a fix for this, and I can verify that user input is no longer reflected on the page and your PoC no longer reproduces. Can you verify that it's no longer vulnerable?**
