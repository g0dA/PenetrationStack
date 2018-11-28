# Cors
关于Cors研究的基础脚本

## 权限
Server端的`Access-Control-Allow-Credentials`应当与下保持一致
```
    xmlHttp = new XMLHttpRequest();
    xmlHttp.withCredentials = true;
```
否则浏览器将会报错

## 错误
配置错误并非是`*`，因为当`Access-Control-Allow-Credentials`为`true`时，浏览器会拦截跨域请求的输出，可以说是最后防线，报错如下：
```
The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'
```
真正的错误配置情况如下：
```
header('Access-Control-Allow-Origin: '.$_SERVER['HTTP_ORIGIN']);
header("Access-Control-Allow-Credentials: true");
```
## 高级利用

利用上无非都是些针对`Origin`的绕过，且仅仅是用于`Safari`，原因是`Safari`不会校验域名的有效性，而是直接发送请求，这样我们可以来组合出一个逃逸规则的域名，比如`http://victim.com%60attacl.com`
