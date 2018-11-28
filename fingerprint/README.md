# fingerprint
指纹识别

## Alpha版本

没有加入多线程，也无异步处理

## 规则

Name=>{rule1$rule2$rule3}=>Type=>VersipnRules

### Rules

**header**:
* path|header|header_point|rule

**content**:
* path|content|function|rule

### VersionRules

**type**:
* True
* content
* error
* index

type%rule%patch1,patch2

version = re.search.group()-patch1-patch2

## Result

![demo.png](demo.png)
