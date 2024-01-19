---
title: Spring实战（第5版）
tags:
  - 计算机-编程设计
---

![](https://wfqqreader-1252317822.image.myqcloud.com/cover/559/29101559/t7_29101559.jpg)


#### 1.1 什么是Spring




!!! note "笔记"

	 Spring的核心是提供了一个容器（container），通常称为Spring应用上下文（Spring application context），它们会创建和管理应用组件。这些组件也可以称为bean，会在Spring应用上下文中装配在一起，从而形成一个完整的应用程序。这就像砖块、砂浆、木材、管道和电线组合在一起，形成一栋房子似的。 


!!! note "笔记"

	 将bean装配在一起的行为是通过一种基于依赖注入（dependency injection，DI）的模式实现的。 


#### 1.2 初始化Spring应用




!!! note "笔记"

	 TacoCloudApplication.java：这是Spring Boot主类，它会启动该项目。随后，我们会详细介绍这个类。 


!!! note "笔记"

	 RunWith是JUnit的注解，它会提供一个测试运行器（runner）来指导JUnit如何运行测试。可以将其想象为给JUnit应用一个插件，以提供自定义的测试行为。 


#### 1.3 编写Spring应用




!!! note "笔记"

	 Spring自带了一个强大的Web框架，名为Spring MVC。Spring MVC的核心是控制器（controller）的理念 


#### 2.3 校验表单输入




!!! note "笔记"

	 Spring支持Java的Bean校验API（Bean Validation API，也被称为JSR-303）。这样的话，我们能够更容易地声明检验规则，而不必在应用程序代码中显式编写声明逻辑。借助Spring Boot，要在项目中添加校验库，我们甚至不需要做任何特殊的操作，这是因为Validation API以及Validation API的Hibernate实现将会作为Spring Boot web starter的传递性依赖自动添加到项目中。 


#### 4.1 启用Spring Security




!!! note "笔记"

	 Spring Tool Suite 


!!! note "笔记"

	 。用户名为user 

