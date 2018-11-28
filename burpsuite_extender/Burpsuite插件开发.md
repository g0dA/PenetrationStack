# 基于Python的Burpsuite插件开发

> 记录下一段时间研究中所踩的坑，先是第一版本，因为目前我自己开发只用到这些，但这也是因为python太多第三方模块相比API更为便捷，[官方API地址](https://portswigger.net/burp/extender/api/index.html?)

## 开发目的

> 取舍监听器

首先确认自己想开发一个什么样的东西，这涉及到你初始设置的监听器，对于`HTTP`请求的手动处理，`Burpsuite`的`repeater`已经做的十分完美了，功能简洁，那么多数情况下的开发目的便是对于请求的自动化处理,至于还有更多的插件扩展，比如对于intruder的自定义payload这些，以后再记录，因为我用的很少，而且这些我更喜欢放到`repeater`中去解决。

自动化处理我个人而言分成两个方面：
* 对HTTP请求/响应的优化
* 测试用

优化很容易理解，就像是对于响应中的编码能够自动转换或是优化输出，因为请求我们可以任意控制，在此基础上理解就是需要处理所有的`HTTP响应包`，而测试用则又是一个方面，既然目的是自动化测试，在非凭空创造请求的基础上，那么基本需求就是插件本身能够对`HTTP`请求做自定义，反复使用一个`BaseRequest`，这儿开始就涉及到了监听器的取舍。

列出目前接触到的几个监听器:
* `IExtensionStateListener` 这个监听器在开发初期可以忽略，因为这个监听器的目的是通过对于插件状态的监听来善后，例如插件下线后关闭其所有的的调用，而我们开发初期主要是处理`HTTP`请求，因此不太用到这个

* `IHttpListener` 最常用监听器，可谓是所有监听器中的最上级，它的功能也十分简单，就是监听`Burpsuite`中所有的`HTTP请求/响应`，请记住，是所有
```
void	 processHttpMessage(int toolFlag, boolean messageIsRequest, IHttpRequestResponse messageInfo)
```
这是`IHttpListener`的官方接口实现方法，有三个参数会被传入进来，`toolFlag`代表了传入的`请求/响应`来自于哪一个扩展，官方给出列表如下
```
public static final int	TOOL_COMPARER	512  //compare
public static final int	TOOL_DECODER	256  //decoder
public static final int	TOOL_EXTENDER	1024 //extender
public static final int	TOOL_INTRUDER	32   //intruder
public static final int	TOOL_PROXY	4      //proxy
public static final int	TOOL_REPEATER	64   //repeater
public static final int	TOOL_SCANNER	16   //scanner
public static final int	TOOL_SEQUENCER	128  //sequencer
public static final int	TOOL_SPIDER	8      //spider
public static final int	TOOL_SUITE	1      //suite
public static final int	TOOL_TARGET	2      //target
```
开发过程中可以用如下代码来对`HTTP请求/响应`做行为取舍
```
if toolFlag == {int}:
  TODO
```
`messageIsRequest`通过布尔值判断传入的是否为一个`request`，这儿如果没什么需求，基本都忽略，因为我自己很少用到，最最重要的参数`messageInfo`，这儿说他重要是因为它的类型为`IHttpRequestResponse`，这也是我在开发过程中遇到最多的坑，后面准备拿专门的一个地方讲解这个类型，毫不客气地说，整个`Burpsuite插件`的开发都是围绕着这个类型的数据做修改，`IHttpListener`综合起来，很适用于`对HTTP请求/响应的优化`，因为他监听的覆盖面是`ALL`

* `IProxyListener` 如其名，这个监听器仅仅只处理通过`PROXY`扩展的数据，如官方所言
```
void	processProxyMessage(boolean messageIsRequest, IInterceptedProxyMessage message)
          //This method is invoked when an HTTP message is being processed by the Proxy.
```
可以看到和`IHttpListener`的传入基本相同，但是因为只针对单个扩展，因此就少了`toolFlag`来标注来源，其中这儿有一个`tips`需要知道，那就是当你开启`intercept`时，即使你`Drop`了`request`，依然会传入此监听器，因为`request`是优先进入的`PROXY`，此监听器可以用来开发`被动测试`类型的插件，可以达成对于任意传入`PROXY`的请求进行自定义测试，从而与手动部分如`repeater`的请求分开

* `IScannerCheck`这个可以说是另类监听器，也可以说是一个检查器，其实后者更为准确，在开发`被动扫描`插件时，我原先使用的是`IProxyListener`，后来发现`IScannerCheck`更为便捷，通过注册一个检查器，然后再利用`doPassiveScan`的实现来做到对于`PROXY`的请求的变相监听，这儿说是变相监听是因为官方文档的说明定义此处仅是对一个`baseRequestResponse`做被动检查，而非如上两个监听器的行为，但是其最终效果，却十分的出色，因此我在自己开发的`被动扫描框架`里，使用的就是这个API，而非`IProxyListener`，并且这儿在开发时候踩了好几个坑，这些放到后面实际开发用例时再讲解
```
java.util.List<IScanIssue>      doPassiveScan(IHttpRequestResponse baseRequestResponse)
The Scanner invokes this method for each base request / response that is passively scanned
```
后面还有一个注释
```
Note: Extensions should only analyze the HTTP messages provided during passive scanning, and should not make any new HTTP requests of their own.
```

上面三个就是我个人比较看好的API，不多做阐述，用后即知:)

## Burpsuite中的数据类型及处理

>认识数据类型，正确使用处理方式，这一段名字我想了半天，数据类型好说，但是这个处理我一直没想到什么好词去替代，那就只能将就看了，这一部分还是蛮重要的，因为这决定了你能写出多少BUG来

数据类型是我在开发过程中一个踩坑非常多的点，所以想的比较多，但这些非常庆幸官方提供的信息非常明确。

需要知道对于插件的开发都是基于一个`baseRequestResponse`，这个`baseRequestResponse`在实际情况中是如下这样的:

**request**:
```
GET / HTTP/1.1
Host: 127.0.0.1
User-Agent:  Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Connection: close
Content-Length: 2
```
**response**:
```
HTTP/1.1 200 OK
Date: Sat, 14 Apr 2018 06:48:16 GMT
Server: Apache/2.2.31 (Unix) mod_ssl/2.2.31 OpenSSL/1.0.1t DAV/2
Connection: close
Content-Type: text/html
Content-Length: 1090

body
```
那么这样的数据在`Burpsuite`中又是什么形式呢？

### `IHttpRequestResponse`

这是之前提到的最重要的类型，为什么说重要，因为此类型的数据在`burpsuite`中便代表着一个`RequestResponse`，包括`baseRequestResponse`也包括`editRequestResponse`,而上面说的`request`和`response`的信息也在此类型的数据中，这是一个完整的请求过程的记录，但是`Burpsuite`却也有一套自己的数据封装方式，这就是说，`IHttpRequestResponse`类型的数据你并非是可以直接拿来让其余语言使用的。

这样说也许不太理解，所以我展示一个`baseRequestResponse`，看看它的样子是什么样的。（为了方便，以后默认所有的`baseRequestResponse`为`IHttpRequestResponse`）
```
burp.x2e@48762ea6
```
实际如果是经常调试java的应该会觉得这个数据类型很眼熟，这儿不多加赘述，因为我没学过java :)

这一个`burp.x2e@48762ea6`就是一个`baseRequestResponse`，那么这个`burp.x2e@48762ea6`中有哪些信息呢
* request
* response
* httpservice
* ....(这部分数据不常用，可以自己了解)

前两个好说，后面的`httpservice`什么呢？这个可以直接理解为`host+port+ishttps`，是不是看着很熟悉，用肉眼可以看的就是在`repeater`模块右上角那个修改按钮中的东西

下面说说对于一个`baseRequestResponse`的处理，这个也是开发中踩坑最多的地方

说了是基于python的开发，那么真正去处理的应该是一个字符串，而非这种封装数据，以获取一个`request`为例子，可以用到的东西是什么

* baseRequestResponse.getRequest()
* self._helpers.analyzeRequest(baseRequestResponse)

上面两种方式分别都获取到了`request`的`message`，但是第一种方式返回的类型是`byte[]`，第二种方式返回的类型是`IRequestInfo`

分别输出看看：
```
array('b', [71, 69, 84, 32, 47, 99, 103, 105, 45, 98, 105, 110, 47, 112, 111, 99, 46, 99, 103, 105, 32, 72, 84, 84, 80, 47, 49, 46, 49, 13, 10, 72, 111, 115, 116, 58, 32, 49, 50, 55, 46, 48, 46, 48, 46, 49, 13, 10, 85, 115, 101, 114, 45, 65, 103, 101, 110, 116, 58, 32, 77, 111, 122, 105, 108, 108, 97, 47, 53, 46, 48, 32, 40, 88, 49, 49, 59, 32, 76, 105, 110, 117, 120, 32, 120, 56, 54, 95, 54, 52, 59, 32, 114, 118, 58, 53, 57, 46, 48, 41, 32, 71, 101, 99, 107, 111, 47, 50, 48, 49, 48, 48, 49, 48, 49, 32, 70, 105, 114, 101, 102, 111, 120, 47, 53, 57, 46, 48, 13, 10, 65, 99, 99, 101, 112, 116, 58, 32, 116, 101, 120, 116, 47, 104, 116, 109, 108, 44, 97, 112, 112, 108, 105, 99, 97, 116, 105, 111, 110, 47, 120, 104, 116, 109, 108, 43, 120, 109, 108, 44, 97, 112, 112, 108, 105, 99, 97, 116, 105, 111, 110, 47, 120, 109, 108, 59, 113, 61, 48, 46, 57, 44, 42, 47, 42, 59, 113, 61, 48, 46, 56, 13, 10, 65, 99, 99, 101, 112, 116, 45, 76, 97, 110, 103, 117, 97, 103, 101, 58, 32, 122, 104, 45, 67, 78, 44, 122, 104, 59, 113, 61, 48, 46, 56, 44, 122, 104, 45, 84, 87, 59, 113, 61, 48, 46, 55, 44, 122, 104, 45, 72, 75, 59, 113, 61, 48, 46, 53, 44, 101, 110, 45, 85, 83, 59, 113, 61, 48, 46, 51, 44, 101, 110, 59, 113, 61, 48, 46, 50, 13, 10, 82, 101, 102, 101, 114, 101, 114, 58, 32, 104, 116, 116, 112, 58, 47, 47, 49, 50, 55, 46, 48, 46, 48, 46, 49, 47, 13, 10, 67, 111, 111, 107, 105, 101, 58, 32, 119, 112, 45, 115, 101, 116, 116, 105, 110, 103, 115, 45, 116, 105, 109, 101, 45, 49, 61, 49, 53, 49, 52, 52, 54, 55, 50, 53, 52, 59, 32, 72, 109, 95, 108, 118, 116, 95, 102, 54, 50, 56, 100, 56, 54, 50, 52, 51, 100, 97, 102, 48, 53, 99, 53, 54, 52, 97, 97, 49, 55, 102, 53, 53, 101, 50, 55, 98, 48, 50, 61, 49, 53, 49, 54, 49, 55, 51, 50, 56, 56, 59, 32, 80, 72, 80, 83, 69, 83, 83, 73, 68, 61, 101, 52, 97, 55, 100, 56, 102, 49, 101, 51, 55, 100, 49, 97, 99, 99, 51, 50, 102, 101, 99, 49, 100, 97, 98, 101, 97, 53, 51, 99, 99, 50, 59, 32, 80, 76, 61, 114, 97, 110, 99, 104, 101, 114, 59, 32, 67, 83, 82, 70, 61, 51, 70, 53, 68, 54, 51, 52, 54, 52, 69, 59, 32, 119, 111, 114, 100, 112, 114, 101, 115, 115, 95, 116, 101, 115, 116, 95, 99, 111, 111, 107, 105, 101, 61, 87, 80, 43, 67, 111, 111, 107, 105, 101, 43, 99, 104, 101, 99, 107, 59, 32, 119, 111, 114, 100, 112, 114, 101, 115, 115, 95, 108, 111, 103, 103, 101, 100, 95, 105, 110, 95, 53, 99, 48, 49, 54, 101, 56, 102, 48, 102, 57, 53, 102, 48, 51, 57, 49, 48, 50, 99, 98, 101, 56, 51, 54, 54, 99, 53, 99, 55, 102, 51, 61, 97, 100, 109, 105, 110, 37, 55, 67, 49, 53, 49, 52, 54, 51, 55, 48, 53, 48, 37, 55, 67, 57, 51, 50, 110, 75, 97, 111, 104, 105, 122, 110, 118, 106, 89, 66, 54, 112, 74, 115, 51, 70, 113, 85, 103, 74, 99, 57, 110, 65, 79, 117, 67, 111, 88, 56, 102, 106, 67, 97, 76, 122, 98, 75, 37, 55, 67, 100, 54, 50, 51, 51, 51, 101, 50, 52, 97, 100, 54, 53, 99, 99, 102, 102, 54, 56, 50, 50, 100, 102, 48, 101, 52, 48, 51, 57, 101, 51, 57, 99, 52, 57, 57, 52, 52, 97, 50, 102, 56, 49, 102, 54, 56, 51, 51, 97, 48, 51, 48, 100, 48, 99, 55, 50, 100, 51, 101, 51, 51, 56, 55, 59, 32, 72, 109, 95, 108, 112, 118, 116, 95, 102, 54, 50, 56, 100, 56, 54, 50, 52, 51, 100, 97, 102, 48, 53, 99, 53, 54, 52, 97, 97, 49, 55, 102, 53, 53, 101, 50, 55, 98, 48, 50, 61, 49, 53, 49, 54, 51, 52, 57, 51, 50, 48, 59, 32, 79, 83, 69, 83, 83, 73, 79, 78, 73, 68, 61, 45, 59, 32, 74, 83, 69, 83, 83, 73, 79, 78, 73, 68, 46, 55, 56, 48, 102, 57, 54, 48, 56, 61, 49, 116, 110, 107, 103, 112, 52, 121, 49, 52, 98, 110, 121, 49, 51, 104, 113, 117, 111, 116, 52, 48, 99, 111, 112, 99, 59, 32, 115, 99, 114, 101, 101, 110, 82, 101, 115, 111, 108, 117, 116, 105, 111, 110, 61, 49, 57, 50, 48, 120, 49, 48, 56, 48, 59, 32, 74, 83, 69, 83, 83, 73, 79, 78, 73, 68, 46, 57, 49, 51, 48, 53, 102, 55, 102, 61, 49, 57, 107, 116, 112, 114, 50, 55, 99, 104, 104, 53, 113, 54, 119, 52, 106, 100, 97, 55, 122, 102, 100, 106, 117, 59, 32, 95, 120, 115, 114, 102, 61, 50, 124, 52, 53, 100, 53, 97, 102, 52, 54, 124, 53, 101, 100, 102, 49, 52, 52, 54, 98, 51, 98, 49, 56, 53, 99, 51, 56, 102, 53, 53, 56, 54, 54, 49, 54, 56, 98, 49, 53, 100, 99, 53, 124, 49, 53, 49, 54, 54, 57, 56, 56, 52, 49, 59, 32, 57, 100, 52, 98, 98, 52, 97, 48, 57, 102, 53, 49, 49, 54, 56, 49, 51, 54, 57, 54, 55, 49, 97, 48, 56, 98, 101, 102, 102, 50, 50, 56, 61, 53, 100, 56, 101, 97, 99, 52, 50, 102, 100, 55, 100, 49, 102, 48, 56, 100, 50, 102, 53, 99, 52, 49, 55, 97, 53, 48, 50, 52, 48, 99, 55, 59, 32, 101, 52, 100, 56, 54, 57, 57, 55, 48, 98, 50, 97, 53, 55, 101, 101, 102, 51, 100, 55, 51, 101, 101, 99, 55, 57, 101, 52, 57, 48, 101, 50, 61, 49, 52, 51, 102, 98, 56, 97, 101, 101, 97, 51, 55, 52, 98, 53, 49, 52, 54, 55, 100, 97, 54, 100, 54, 49, 54, 51, 52, 101, 98, 102, 57, 59, 32, 101, 100, 100, 55, 50, 102, 51, 55, 50, 102, 48, 100, 48, 101, 100, 49, 99, 101, 48, 56, 55, 101, 49, 55, 100, 98, 48, 101, 102, 54, 100, 99, 61, 54, 49, 52, 53, 97, 98, 50, 52, 51, 99, 101, 56, 48, 98, 50, 55, 48, 51, 51, 102, 100, 50, 53, 56, 56, 48, 51, 57, 56, 100, 98, 57, 59, 32, 74, 83, 69, 83, 83, 73, 79, 78, 73, 68, 61, 52, 68, 68, 67, 48, 53, 51, 69, 54, 52, 51, 51, 53, 50, 54, 70, 67, 49, 55, 66, 50, 51, 55, 55, 49, 68, 67, 67, 65, 68, 56, 65, 13, 10, 67, 111, 110, 110, 101, 99, 116, 105, 111, 110, 58, 32, 99, 108, 111, 115, 101, 13, 10, 85, 112, 103, 114, 97, 100, 101, 45, 73, 110, 115, 101, 99, 117, 114, 101, 45, 82, 101, 113, 117, 101, 115, 116, 115, 58, 32, 49, 13, 10, 88, 45, 70, 111, 114, 119, 97, 114, 100, 101, 100, 45, 70, 111, 114, 58, 32, 49, 50, 55, 46, 48, 46, 48, 46, 49, 39, 13, 10, 67, 97, 99, 104, 101, 45, 67, 111, 110, 116, 114, 111, 108, 58, 32, 109, 97, 120, 45, 97, 103, 101, 61, 48, 13, 10, 13, 10])
===============================================================================
burp.luf@67534b99
```
两者存储的信息是相同的，只有类型结构的区别，那为什么要这样做呢？

`baseRequestResponse.getRequest()`所获取的是个整体的东西，最后经过处理就是一个完整的`request`的字符串，他不会去管那部分是`head`，那部分是`method`，你后面怎么操作，就不管你了。

`self._helpers.analyzeRequest(baseRequestResponse)`则返回一个依旧封装的东西，但是你可以继续对这个封装的数据进行处理，比如从中单独提取出`url`，或者提取出参数，两种方式各有优劣。

对于一个`baseRequestResponse`，官方还提供了其余的处理方式，这儿建议直接去看官方的，后面就跟着实例一起说明。

### `IRequestInfo` AND `IResponseInfo`

很重要的两个类型，一个代表了`request`一个代表了`response`，对于这两个类型，官方还提供了很多功能强大的处理方式

以`被动扫描`来说，需要明白到底要对数据做哪些处理，比如针对一个漏洞，需要对`request`进行识别，判断是否存在可疑点，接着就是针对这个`request`进行修改甚至是重构，然后再根据重构后的`response`进行判断。

按照如上的逻辑，需求可以简单划分为对`request`的读写和对`response`的读，而写又分为`edit/update(编辑)`和`build(重构)`

查看一下官方的文档，列出一个`IRequestInfo`的可用函数：
* getBodyOffset()
* getContentType()
* getHeaders()
* getMethod()
* getParameters()
* getUrl()

函数名都很简洁易懂，清晰的展示了自己的功能，这些都属于读取，那写(更新/重构)的函数有哪些
* setRequest(byte[] message)
* makeHttpRequest(IHttpService httpService, byte[] request)
* buildHttpRequest(java.net.URL url)
* buildHttpMessage(java.util.List<java.lang.String> headers, byte[] body)

就以读来说，知道上面的几个函数就完成了吗？不是，这单元着重讲解的是类型，那么这儿怎么可能没有类型导致的坑呢。上面说了，`python`是不能直接处理`Burpsuite`所特有的类型的，那么按照顺序来，光是读的那部分，函数返回的类型是如下：
* int
* byte
* list[string]
* String
* list[IParameter]
* url

这些类型里`int`，`list[string]`，`string`可以直接被`python`使用，而`url`经过`str()`函数强转也可以被`python`使用，而其余的则需要经过官方提供的函数继续处理

## 工具函数/扩展函数

> 想半天还是起了这么个名字，因为官方为了方便开发者，提供了很多处理函数用于处理不同的数据类型已经对于不同类型的数据进行操作，这些在我看来都是依托存在，也就是属于工具类

两个工具大类：

* `IExtensionHelpers`
* `IBurpExtenderCallbacks`

这两个大类下提供了大量的工具函数，基本涉及到插件的开发都无法绕过，在开发初期，我就在想`Burpsuite`作为一个十分成熟的框架，API也应该会非常成熟，能够便于开发者快速开发，这些方便性应当体现如下：
* 不同类型的转换
* 常见操作的封装

因为能够对于一个数据能够转换不同类型，才使得这个数据能够被不同语言或者工具使用，否则`python`如何去识别一个`burp.luf@67534b99`呢？

在这基础上，通过阅读API，分类挑选出开发中比较常用的几个函数。

### `IExtensionHelpers`

这个官方定义为辅助方法的接口，那么想要调用此接口，就需要在最初实现插件接口时就进行调用，也就是如下代码
```python
def registerExtenderCallbacks(self,callbacks):

    #keep a reference to our callbacks object
    self._callbacks = callbacks

    #helper methods
    self._helpers = callbacks.getHelpers()

    return
```
如此以后使用接口下的函数时，就可以直接用如下形式:
```python
self._helpers.bytesToString(byte)
```
接着直接说函数(仅说初期常用)，简洁点说，并不是难以理解:
* `analyzeRequest()` //最常用函数之一，返回一个`IRequestInfo`，至于传入，自己看文档，常用为`IHttpRequestResponse`

* `analyzeResponse()`  //同上，返回`IResponseInfo`,但是这儿有个坑，就是传入只能是`bytep[]`

* `buildHttpMessage()` //构造一个`byte`类型的请求，非常实用的一个函数，我自己开发时基本都是用这个函数重构的请求，传入为`(string headers,byte[] body)`

* `bytesToString()`  //还记得上面提到的大量的byte形式的数据吗，就是通过这个函数能够转成被`python`识别的`string`

* `stringToBytes()`  //上面反者理解，因为有很多函数处理的是数据类型就是`byte`而非`string`

### `IBurpExtenderCallbacks`

这个接口可以直接理解成`Burpsuite`中的万金油接口，其中包含了各种回调函数

直接说函数:
* `applyMarkers()` //高亮标记用，这个我也就在扫描器里用到了，为了高亮表示漏洞关键字

* `doPassiveScan`  //这个就是被动扫描，不过我更喜欢用`IScannerCheck`中的，因此在这就是提一下

* `makeHttpRequest()` //个人最推荐的函数，因为这个函数是构造一个`IHttpRequestResponse`的函数，可以想到有多么重要，有人会问和上面那个`buildHttpMessage()是什么关系呢。就简单写一个小例子:
```python
NewRequest = self._helpers.buildHttpMessage(new_headers, new_body)      
NewIHttpRequestResponse = self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(),NewRequest)
```
其余函数就得自己去理解了，都不是很难，多用几次就很方便知道了

## 正式开发
所有的扩展都必须实现一个`IBurpExtender`接口,实现类名必须为`BurpExtender`，通俗点说，就是若你想要开发一个插件，`BurpExtender`大类就是你的插件大类，代表一个新插件，写法就是如下:
```
class BurpExtender(IBurpExtender):

    def registerExtenderCallbacks(self,callbacks):

      // TODO here
```
至于还想实现什么接口，就往里面填就行，后面就只需要尊崇核心代码写成`def`往`BurpExtender`里面添加，不是非常必要的可以写成新的`class`然后再去调用。

### registerExtenderCallbacks
这是一个核心`def`，效果就是注册接口用，包括上面提到的注册监听器，或者是调用接口，或者是注册插件名，相当于一个大菜单栏，后续的各种功能由此开始。

```python
def registerExtenderCallbacks(self,callbacks):

    #keep a reference to our callbacks object
    self._callbacks = callbacks

    #helper methods
    self._helpers = callbacks.getHelpers()

    #define name
    self._callbacks.setExtensionName("AnGScan")
    #register a scancheck
    callbacks.registerScannerCheck(self)

    return
```
比如上述代码，就是一个较为完整的写法

除了我自己项目里的代码，那些都太长了不好举例子，这儿就贴出一份[别人的代码](https://github.com/stayliv3/burpsuite-changeU)，比较间简短，而且功能简洁易懂，供大家学习:

```python
#!/usr/bin/env python2
#coding=utf8
from burp import IBurpExtender
from burp import IHttpListener
from burp import IHttpRequestResponse
from burp import IResponseInfo

import re
# Class BurpExtender (Required) contaning all functions used to interact with Burp Suite API

class BurpExtender(IBurpExtender, IHttpListener):

    # define registerExtenderCallbacks: From IBurpExtender Interface
    def registerExtenderCallbacks(self, callbacks):

        # keep a reference to our callbacks object (Burp Extensibility Feature)
        self._callbacks = callbacks
        # obtain an extension helpers object (Burp Extensibility Feature)
        # http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html
        self._helpers = callbacks.getHelpers()
        # set our extension name that will display in Extender Tab
        self._callbacks.setExtensionName("unicode decode")
        # register ourselves as an HTTP listener
        callbacks.registerHttpListener(self)


    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):

        if toolFlag == 64 or toolFlag == 16 or toolFlag == 32: #if tool is Proxy Tab or repeater

            if not messageIsRequest:#only handle responses
                response = messageInfo.getResponse()

                analyzedResponse = self._helpers.analyzeResponse(response) # returns IResponseInfo
                headers = analyzedResponse.getHeaders()

                new_headers = []
                for header in headers:

                    if header.startswith("Content-Type:"):

                        new_headers.append(header.replace('iso-8859-1', 'utf-8'))
                    else:
                        new_headers.append(header)

                body = response[analyzedResponse.getBodyOffset():]
                body_string = body.tostring()
                u_char_escape = re.search( r'(?:\\u[\d\w]{4})+', body_string)
                if u_char_escape:

                    u_char = u_char_escape.group().decode('unicode_escape').encode('utf8')
                    new_body_string = body_string.replace(u_char_escape.group(),'--u--'+u_char+'--u--')
                    new_body = self._helpers.bytesToString(new_body_string)

                    messageInfo.setRequest(self._helpers.buildHttpMessage(new_headers, new_body))
```
上面这个代码功能很简单，就是处理响应里的一些编码而已

如果我写的话，大概`class BurpExtender(IBurpExtender, IHttpListener):`我会写成`class BurpExtender(IBurpExtender, IHttpListener,IRequestInfo,IResponseInfo):`这样比较安心:)
