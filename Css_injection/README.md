# Css_injection

## 模拟真实案例

[CSS Injection on /embed/ via bgcolor parameter leaks user's CSRF token and allows for XSS](https://hackerone.com/reports/386334)

## 效果

通过CSS injection窃取页面的Csrf_token或者ticket

## 局限

Css可控，ticket写入到页面中

## 原理

Css属性选择器滥用
```
[attribute=value]   [foo=bar]     选择foo =“bar”的所有元素

[attribute~=value]  [foo~=bar]    选择所有包含单词“bar”的foo属性的元素

[attribute|=value]  [foo|=bar]    选择所有具有以“bar”开头的foo属性值的元素

[attribute^=value]  [foo^="bar"]  选择所有具有以“bar”开头的foo属性值的元素

[attribute$=value]  [foo$="bar"]  选择所有具有以“bar”结尾的foo属性值的元素

[attribute*=value]  [foo*="bar"]  选择所有包含子字符串“bar”的foo属性的元素
```
通过请求外部地址确认ticket值

## 测试中的问题

firefox下测试无效，Chrome成功，原因未调查
