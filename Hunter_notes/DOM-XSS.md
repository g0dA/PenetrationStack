# 漏洞散记
##  DOM-xss
> 以前只是听说过，但确实从没实际挖掘过的一个漏洞，就挑出来分享一下，而且作者的利用也非常的简洁,和之前Uber的XSS一样，作者的只是储备很高，能靠一点关键的地方就找出最合理的处理方式

> 漏洞价值:1000$

> 源漏洞:[125386](https://hackerone.com/reports/125386)

# 挖洞过程
作者没有介绍自己是怎么挖洞的，而是直接放出了自己的POC去验证的这个漏洞

**POC**
```
<html>
<body>
<script>
window.open("https://www.mapbox.com/maki/", "<script>alert(document.cookie)<\/script>");
</script>
</body>
</html>
```
## 官方

对于这个漏洞，官方到时做了一些解释

```
The vulnerability used the JavaScript window.open() method to pass in arbitrary JavaScript to the second parameter (name). This JavaScript was then executed on https://www.mapbox.com/maki due to the underscore.js interpolating template <%=name %> in line 28 of index.html. This came from a template evaluated in line 68 of site.js. The context object that the template was evaluated on did not have a name property, so ordinarily <%=name %> would have evaluated to an empty string. Instead, due to _.template's use of with, the resolution of interpolated properties in the template proceeded up the JavaScript context chain, eventually looking for a name property on the window global context.
```
具体的能看出来，**maki**是开源的，作者应该是从[源代码](https://github.com/mapbox/maki/tree/b1b399eaac8263d1e0d7c6c206490fe70de1d82c)中审出的漏洞

## 结语
实际上就是一个很正常的DOM-BASE的XSS，但是由于很少见，而且作者提供了测试用POC，所以才分享出来

而DOM-xss的相关技术，我是很推荐知乎的这篇[文章](https://www.zhihu.com/question/26628342/answer/33504799)的
