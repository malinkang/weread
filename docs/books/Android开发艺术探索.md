---
title: Android开发艺术探索
tags:
  - 计算机-编程设计
---

![](https://wfqqreader-1252317822.image.myqcloud.com/cover/61/23735061/t7_23735061.jpg)


### 3.4 View的事件分发机制




!!! note "笔记"

	 所谓点击事件的事件分发，其实就是对MotionEvent事件的分发过程，即当一个MotionEvent产生了以后，系统需要把这个事件传递给一个具体的View，而这个传递的过程就是分发过程。点击事件的分发过程由三个很重要的方法来共同完成： 


### 4.2 理解MeasureSpec




!!! note "笔记"

	 MeasureSpec在很大程度上决定了一个View的尺寸规格，之所以说是很大程度上是因为这个过程还受父容器的影响，因为父容器影响View的MeasureSpec的创建过程 


!!! note "笔记"

	 高2位代表SpecMode 


!!! note "笔记"

	 对于DecorView，其MeasureSpec由窗口的尺寸和其自身的LayoutParams来共同确定 


!!! note "笔记"

	 对于普通View，其MeasureSpec由父容器的MeasureSpec和自身的LayoutParams来共同决定，MeasureSpec一旦确定后，onMeasure中就可以确定View的测量宽/高。 


### 4.3 View的工作流程




!!! note "笔记"

	 这里给出四种方法来解决这个问题 

