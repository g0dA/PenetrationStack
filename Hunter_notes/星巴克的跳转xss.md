# 漏洞散记
## 漏掉的奖金
> 我曾在这个点发现过星巴克的任意重定向漏洞，但是也想过进行`xss`弹窗却失败了，这次看到别人的`payload`非常的有意思，因此记录一下。

> 漏洞价值:375$

> 源漏洞:[#438240](https://hackerone.com/reports/438240)


# 挖洞过程

漏洞的挖掘并不是非常的费神，就是非常简单的一个`反射型xss`，但是呢作者提出了一个非常有意思的`payload`
```
https://www.starbucks.com/account/signin?ReturnUrl=%19Jav%09asc%09ript%3ahttps%20%3a%2f%2fwww%2estarbucks%2ecom%2f%250Aalert%2528document.domain%2529
```
其中有针对`javascript`这种黑名单的绕过，也有针对`https://`这种正则的绕过，同样的添加了域名满足了跳转的目标检测，认为是一个合法的跳转目标，然后通过`%0A`的方式继续绕过，导致`alert`逃逸出来，非常的有趣。

# 结语

思路非常的随和，基本属于是服务端防御了什么，就选择性地绕过什么，有意思。
