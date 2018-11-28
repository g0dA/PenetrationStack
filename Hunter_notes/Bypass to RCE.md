# 漏洞散记
##  Bypass to RCE
> 整个漏洞挖掘的思路很直白，但却也很精彩，简单来说就是作者想要做，所以作者就往自己想好的方向疯狂测试，最后终于发掘出了一个严重的RCE，甚至我觉的2000$有点太少了

> 漏洞价值:2000$

> 源漏洞:[hackerone地址关了，所以换成作者博客的](https://www.secgeek.net/bookfresh-vulnerability/)

# 挖洞过程
```
i saw that Bookfresh became a part of Square bug bounty program at Hackerone.
```
起因很简单，就是作者发现Bookfresh上线hackerone了，就想去捞钱，最开始的测试中，发现了大量的XSS(不知道赚了多少)，然后就觉得应该存在更严重的漏洞，比如sql或者RCE之类的，所以作者就从**profile**开始测试，刚开始就发现了一个上传点，是用来上传**profile photo**的，漏洞挖掘由此开始

## 逐步测试
作者上传图片，经过测试发现能够上传php的文件，但是上传了包含了**<?phpinfo()?>**代码的PHP文件发现并不能执行成功
作者将上传的图片下载到本地，然后查看其中的内容
![1](http://www.secgeek.net/wp-content/uploads/2014/11/bookfresh1.png)

其中的php代码已经没有了，作者发现，这是经过了GD库的渲染，应该是存在**imagecreatefromjpeg()**

作者一开始觉的有可能是因为上传的文件本身就不是一个完整的图片文件，所以就将PHP代码写入了完整图片文件的最后
![2](https://www.secgeek.net/wp-content/uploads/2014/11/bookfresh2.png)
作者再去上传，直接就返回了**error**

```
File must be a valid image (.gif, .jpg, .jpeg, or .png)
```
## 开始思索
为什么这儿就能直接判定文件不是**image**呢？作者经过多次上传测试
```
it turned out that modifying a single character in any of those jpg images won’t be accepted by php-gd library as a valid image and will not be uploaded .
```
这个结果还是原汁原味的好一点

然后作者就换一下，改成上传gif后缀的文件，发现上传成功了，但是php代码还是没有被执行，依然被GD库给覆盖掉了，由此陷入了一个僵局

## 突破
问题所在：
```
i tried again to inject the php code into other gif images and in different places in the image but the php code was getting removed after uploading it .
```
现在作者面临的问题就是上传的文件会经过**imagecreatefromjpeg()**，这样原本写入其中的php代码就会被覆盖掉

作者也不知到GD库是如何运行的，所以并不能从白盒上面寻找漏洞，那么就继续黑盒

## 亮点
作者想到，GD库渲染也许并不是完全重写，那么总能存在不变的部分，这就是说，如果将**php code**写入这部分区域，那么是不是就能留下自己的php代码，并使其执行

作者上传一个正常的图片，然后再将图片下载下来，这次使用16进制模式打开对比，这儿我们可以使用Burpsuite的compare模块，对比之后发现真的具有相同的部分
```
so i opened the original image file using a hex editor and searched for a one of those matched values “3b45d00ceade0c1a3f0e18aff1” and modified it to “<?phpinfo()?>
```
将其改为php上传，最终发现成功执行代码
![3](http://www.secgeek.net/wp-content/uploads/2014/11/phpinfo.jpg)

# 结语

这个漏洞挖掘让我想到了国内乌云上的一个过二次渲染的上传bypass，作者思路很直白却也很有效，我想到了，那么就去尝试，正如作者说的
```
i decided to give it a try maybe i could be lucky.
```
这次漏洞挖掘的最关键的部分就是如何绕过渲染，而作者最关键的思路就是渲染的方式是否是对文件进行完全重写，而RCE的基础又是始于能够上传php文件，一环套一环，最终形成一个完整的漏洞，虽然我觉的这个漏洞更大的原因是**Any file upload**
