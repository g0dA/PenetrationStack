# 漏洞散记
##  Pronhub越权查看任意pic,gifs,video
> 对于Prohub来说，这个Bug真的是重要的很，因为这样的话你就真的在众多狼友面前一点隐私没有了，这个漏洞的越权有点迷，不怎么想得通为什么会在那儿出现越权，但后来仔细想想还真有可能的

> 漏洞价值:1500$

>源地址:[#148764](https://hackerone.com/reports/148764)

## 漏洞过程
不用说，都应该知道Pronhub是一个共享的网站，可以上传自己想上传的Video，pic或者是Gif，而且，Pronhub还提供了私密设置，简单的说就是你的上传只允许你的朋友观看

作者作为一个资深老司机，还详细介绍了如何这样设置

**Steps to reproduce :**

1. Create a profile with username Victim and go to his profile setting --> preferences --> stream preferences.

2. In stream preferences you will see the option of who can see your stream with two options everyone and only friends.

3. Set Only Friends option here. Now go to your profile and post on your stream(You can post photos ,videos etc.). Let's say your post id is = "12345" A simple post will a link something like : http://www.pornhub.com/users/victim/post/stream_posts_users/12345

Since you have set the privacy for your stream so only your friends can see this post.

按理来说这样设置，其余人是看不到你post的东西的，作者也做了实验，注册一个新账号去访问，只会得到显示：
```
You will see the message saying that stream is private.
```
总之，就是真的达成了私密设置的初衷，然而作者给绕了

## 利用
```
 http://www.pornhub.com/users/victim/post/stream_posts_users/12345
```
这个Url是你想看的人的Post，会显示的是你没有权限，但是你知道了该用户POST的id，也就是12345

接着访问如下
```
http://www.pornhub.com/users/Attacker/post/stream_posts_users/12345
```
成功访问到post的video(gif,pic)

那么利用的方式就是，先知道你想访问的**post_id**，或者任意爆破出**post_id**，然后改变访问link中的username，将其从**victim**改成**attacker**

接着就能访问到原本被私密保护的POST

## 结语

顺口一句，老司机想开车的话没有程序挡得住

这个漏洞看起来很简单，但一开始我在想，如果改变了username，不就会改变访问的用户区域吗？这样访问到的post还是想访问的post?后来仔细想一想，访问的关键应该是post_id而不是username

那么设置中的**privat**应该只是针对username区域进行了访问控制，而不是对区域中的**post_id**,当**post_id**在被限制的username区域中时，变不能被访问，不在则能被访问，而改变了username后，是通过一个完全没有限制的username区域去获取post_id，因为username整个区域都没有进行访问控制，那么则继而所有的post_id都能被访问到，因而产生一个越权，漏洞扩大的话应该可以对整个网站的所有资源进行盗爬
