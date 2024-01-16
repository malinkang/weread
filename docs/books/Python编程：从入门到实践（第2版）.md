---
title: Python编程：从入门到实践（第2版）
tags:
  - 计算机-编程设计
---

![](https://cdn.weread.qq.com/weread/cover/90/YueWen_34336681/s_YueWen_34336681.jpg)


### 第 9 章 类




!!! note "笔记"

	 形参self必不可少，而且必须位于其他形参的前面 


!!! note "笔记"

	 因为Python调用这个方法来创建Dog实例时，将自动传入实参self。每个与实例相关联的方法调用都自动传递实参self，它是一个指向实例本身的引用，让实例能够访问类中的属性和方法。创建Dog实例时，Python将调用Dog类的方法__init__()。我们将通过实参向Dog()传递名字和年龄，self会自动传递，因此不需要传递它。每当根据Dog类创建实例时，都只需给最后两个形参（name和age）提供值。 

