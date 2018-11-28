# php_rand_crack

> 引言

> 并没有深入的讲解到`php_rand_crack`的具体内容，而此次`crack`的手法也是很单纯的爆破，只从最基础的层面上认识一下`rand_crack`

## php_rand

先认识一下`php`中的`rand`

看一看`rand.c`
```c
PHP_FUNCTION(rand)
{
	long min;
	long max;
	long number;
	int  argc = ZEND_NUM_ARGS();

	if (argc != 0 && zend_parse_parameters(argc TSRMLS_CC, "ll", &min, &max) == FAILURE)
		return;

	number = php_rand(TSRMLS_C);
	if (argc == 2) {
		RAND_RANGE(number, min, max, PHP_RAND_MAX);
	}

	RETURN_LONG(number);
}
```

`php`中，`rand()`函数创建了一个伪随机数，因为这个函数需要`srand()`函数设置`seed`的初始状态，这样的意思就是，当`php`中的`seed`固定，则`rand`固定

![1](http://i4.buimg.com/567571/6dfc1a37d00b273b.png)

因此问题就很简单了，破解一个`rand`，就需要获取其`seed`

这儿还涉及到一个问题就是，不同的进程使用不同的`seed`，也就是系统的不同会导致结果不同，因为`win`中的`seed`是32位的，而`lin`中的`seed`是1024位的，所以结果会有很大差异，同时经过我的后续测试，发现`php`的版本也会影响到结果，但这个可能是因为`rand.c`的函数实现的问题

我们看下对比：

首先是`w7`下不同版本的`php`:

![2](http://i2.muimg.com/567571/f2532d8cec085b5f.png)

接着我们看`w7`和`xp`下相同版本的`php`:

![3](http://i4.buimg.com/567571/1d66649b143938ff.png)

`w7`和`linux`下相同版本`php`:

![4](http://i2.muimg.com/567571/bbcab32bdbad8e20.png)
![5](http://i2.muimg.com/567571/33986f69a5300f2f.png)

不同`linux`下相同版本:

![6](http://i2.muimg.com/567571/b5d7bfdcb2af0f78.png)
![7](http://i2.muimg.com/567571/6f8229450fa38263.png)

发现结果存在着差异

## rand_crack

我们采用的是爆破的手法获取`seed`，那么就存在一个问题，`win`下的`seed`更容易获取，因为其只有32位，同时在`linux`中`Glibc rand()`改变了调用状态

```
state[i] = state[i-3] + state[i-31]
return state[i] >> 1
```
这是说下一次的输出结果是第3和第31次调用后效果的重叠

可以通过实验证明:

```
6ZF5kNgonV
9h3byovpGR
gGt0A94U92
Now, the next rand will be determining whether it will be an uppercase letter, lowercase letter or number. This is determined by the outcomes of rand 3 and 31 calls ago. That’s the last 9 in gGt0A94U92 and the y in 9h3byovpGR. So we expect the next output of rand(0, 2) to be approximately ⌊10/10 + 25/26 × 3⌋ = 2 mod 3, so that means we get a number. Let’s see if we can predict that number. The next calls to rand that determines the number is determined by the rand from 3 calls ago, a number, and the rand of 31 calls ago, a lowercase letter. The number will thus be between ⌊2/3 + 1/3 × 10⌋ = 0 mod 10 and ⌊3/3 + 2/3 × 10⌋ = 6 mod 10. We thus expect the number to be between 0 and 6. It turns out to be 4:

43J2d2ew31
```
简单来讲，就是`linux`下我们并不能准确的破解出`rand`，而`win`下可以，因为其每次调用的`seed`状态固定

##　实验

准备三份代码：

`rand.php`,`crack.php`,`demo.php`

`rand.php`:
```
<?php
function gen($len)
{
    $token = '';
    while($len--){
        $choose = rand(0, 2);
        if ($choose === 0)
            $token .= chr(rand(ord('A'), ord('Z')));
        else if($choose === 1)
            $token .= chr(rand(ord('a'), ord('z')));
        else
            $token .= chr(rand(ord('0'), ord('9')));
    }
    return $token;
}



echo gen(4)."<br />";

?>
```

`crack.php`:
```
<?php
function gen($len)
{

    $token = '';
    while($len--){

		$choose = rand(0, 2);
        if ($choose === 0)
            $token .= chr(rand(ord('A'), ord('Z')));
        else if($choose === 1)
            $token .= chr(rand(ord('a'), ord('z')));
        else
            $token .= chr(rand(ord('0'), ord('9')));
    }
    return $token;
}
for ($i = 0; $i < PHP_INT_MAX; $i++) {
    srand($i);
    if (gen(4) == "") {
        die("Found: $i \n");
    }
}
?>
```

`demo.php`:
```
<?php

function gen($len)
{

    $token = '';
    while($len--){

		$choose = rand(0, 2);
        if ($choose === 0)
            $token .= chr(rand(ord('A'), ord('Z')));
        else if($choose === 1)
            $token .= chr(rand(ord('a'), ord('z')));
        else
            $token .= chr(rand(ord('0'), ord('9')));
    }
    return $token;
}
srand();
for($i=0;$i<100;$i++){

echo gen(4)."<br />";
}
?>
```
我们查看下运行结果:

![rand](http://i1.piimg.com/567571/857eed93695da229.png)
![crack](http://i1.piimg.com/567571/03fb68c6cdc56931.png)
![demo](http://i4.buimg.com/567571/9ad467b55e7b1b0a.png)

可以看到，我们预测出了后来的`rand`

## 作用

`php_rand_crack`主要作用在哪儿呢？我们上面提供的代码经常使用于`token`的生成

还有一种情况就是随机密码的破解

## 参考

[Cracking PHP rand()](https://www.sjoerdlangkemper.nl/2016/02/11/cracking-php-rand/)

[Hacking crappy password resets](https://blog.skullsecurity.org/2011/hacking-crappy-password-resets-part-1)

[译-Cracking PHP rand()-token 能破解吗？](http://www.cnblogs.com/QQisadog/p/5499816.html)
