---
title: Android插件化开发指南
tags:
  - 计算机-计算机综合
---

![](https://cdn.weread.qq.com/weread/cover/46/YueWen_22917911/t7_YueWen_22917911.jpg)


### 致谢




!!! note "笔记"

	 张勇、任玉刚、罗迪、黄剑、林光亮、邓凡平、王尧波、田维术 


### 第2章 Android底层知识




!!! note "笔记"

	 AIDL是Binder的延伸 


!!! note "笔记"

	 "Calling startActivity() from outside of an Activity "￼                     + " context requires the FLAG_ACTIVITY_NEW_TASK flag."￼                     + " Is this really what you want? ");￼             }￼             mMainThread.getInstrumentation().execStartActivity(￼                     getOuterContext(), mMainThread.getApplicationThread(), null,￼                     (Activity) null, intent, -1, options);￼         }￼     }
2.8 Service工作原理
众所周知，Service有两套流程，一套是启动流程，另一套是绑定流程，如图2-15所示。 


!!! note "笔记"

	 2.9 BroadcastReceiver工作原理
BroadcastReceiver就是广播，简称Receiver。
很多App开发人员表示，从来没用过Receiver。其实，对于音乐播放类App, Service和Receiver用的还是很多的，如果你用过QQ音乐，App退到后台，音乐照样播放不会停止，这就是Service在后台起的作用。
在前台的Activity，点击“停止”按钮，就会给后台Service发送一个Receiver，通知它停止播放音乐；点击“播放”按钮，仍然发送这个Receiver，只是携带的值变了，所以Service收到请求后播放音乐。 


!!! note "笔记"

	 至此，关于广播的所有概念就全都介绍完了，虽然本节列出的代码很少，但我希望上述文字能引导App开发人员进入一个神奇的世界。
2.10 ContentProvider工作原理
ContentProvider，简称CP。App开发人员，尤其是电商类App开发人员，对ContentProvider并不熟悉，对这个概念的最大程度的了解，也仅仅是建立在书本上，它是Android四大组件中的一个。开发系统管理类App，比如手机助手，则有机会频繁使用ContentProvider。 


!!! note "笔记"

	 至此，关于ContentProvider的介绍就结束了。下一小节，我们讨论App的安装流程，也就PMS。
2.11 PMS及App安装过程
2.11.1 PMS简介
PackageManagerService（PMS）是用来获取apk包的信息的。
在前面分析四大组件与AMS通信的时候，我们介绍过，AMS总是会使用PMS加载包的信息，将其封装在LoadedApk这个类对象中，然后我们就可以从中取出在AndroidManifest声明的四大组件信息了。 


!!! note "笔记"

	 所以当你在程序中看到上述这些语句时，它们都是PMS在App进程的代理对象，都能获得当前Apk包的信息，尤其是我们感兴趣的四大组件信息。在插件化编程中，我们反射ActivityThread获取Apk包的信息，一般用于当前的宿主Apk，而不是插件Apk。
ApplicationPackageManager实现了IPackageManager.Stub。
2.12 ClassLoader家族史
Android插件化能从外部下载一个apk插件，就在于ClassLoader。ClassLoader是一个家族。ClassLoader是老祖先，它有很多儿孙，ClassLoader家族如图2-31所示。 


!!! note "笔记"

	 我们不打算深究更底层的代码，只需要知道，optimizedDirectory是用来缓存我们需要加载的dex文件的，并创建一个DexFile对象，如果它为null，那么会直接使用dex文件原有的路径来创建DexFile对象。 


!!! note "笔记"

	 2.14 MultiDex 


!!! note "笔记"

	 这部分基本是废话可以略过 
	> 2.14 MultiDex




### 第3章 反射




!!! note "笔记"

	 jOOR这个开源反射封装库 


!!! note "笔记"

	 写错了吧
 
	> 只想获取类的所有public构造函数，就不能再使用Class的getConstructors方法了，而要使用getDeclaredConstructors方法。




## 第二部分 解决方案




!!! note "笔记"

	 创建一个类库MyPluginLibrary，设置HostApp和Plugin1这两个项目都依赖于MyPluginLibrary。 

