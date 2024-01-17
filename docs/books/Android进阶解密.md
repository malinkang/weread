---
title: Android进阶解密
tags:
  - 计算机-编程设计
---

![](https://cdn.weread.qq.com/weread/cover/72/YueWen_31186331/s_YueWen_31186331.jpg)


### 15.2 插件化的产生




!!! note "笔记"

	 插件化的客户端由宿主和插件两个部分组成，宿主就是指先被安装到手机中的APK，就是平常我们加载的普通APK。插件一般是指经过处理的APK、so和dex等文件，插件可以被宿主进行加载，有的插件也可以作为APK独立运行 


!!! note "笔记"

	 将一个应用按照插件的方式进行改造的过程就叫作插件化。 


### 15.4 Activity插件化




!!! note "笔记"

	 反射实现、接口实现和Hook技术实现 


!!! note "笔记"

	 一种是通过Hook IActivityManager来实现 


!!! note "笔记"

	 另一种是Hook Instrumentation实现 

