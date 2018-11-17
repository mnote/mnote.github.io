---
layout: default
title: Annotation
category: aspectj
---

### 代码与配置同步

跟踪代码依赖性，实现替代配置文件功能

原则

>与具体场景相关的配置应该使用注解的方式与数据关联，与具体场景无关的配置放于配置文件中。
>通过设置注解的@Retention级别在运行时使用反射对不同的注解进行处理

>生成文档

>编译时格式检查

Annotation其实是一种接口。通过Java的反射机制相关的API来访问Annotation信息

###元注解
元注解的作用就是负责注解其他注解。Java5.0定义了4个标准的meta-annotation类型，它们被用来提供对其它 annotation类型作说明。

* @Target
* @Retention
* @Documented
* @Inherited

@Documented 表示含有该注解类型的元素(带有注释的)会通过javadoc或类似工具进行文档化,类型声明是用@Documented 来注解的，这种类型的注解被作为被标注的程序成员的公共API

###自定义注解
使用@interface自定义注解时，自动继承了java.lang.annotation.Annotation接口，由编译程序自动完成其他细节。@interface用来声明一个注解，其中的每一个方法实际上是声明了一个配置参数。方法的名称就是参数的名称，返回值类型就是参数的类型（返回值类型只能是基本类型、Class、String、enum）。可以通过default来声明参数的默认值。

注解在只有一个元素且该元素的名称是`value`的情况下，在使用注解的时候可以省略“value=”，直接写需要的值即可。

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface FruitColor {
    public enum Color{ BULE,RED,GREEN};
    Color value() default Color.GREEN;
}
```

###注解处理

如果没有用来读取注解的方法和工作，那么注解也就不会比注释更有用处了。Java SE 5扩展了反射机制的API，使用`java.lang.reflect.AnnotatedElement`快速的构造自定义注解处理器。

```java
Field[] fields = clazz.getDeclaredFields();
for(Field field :fields){
	if(field.isAnnotationPresent(FruitColor.class)){ 
		FruitColor fruitColor= (FruitColor) field.getAnnotation(FruitColor.class);           
	}
}
```

###APT
APT（Annotation Processing Tool）是一个命令行工具，它对源代码文件进行检测找出其中的annotation后，使用annotation processors来处理annotation。

在程序中添加的注解，可以在编译时刻或是运行时刻来进行处理。在编译时刻处理的时候，是分成多趟来进行的。如果在某趟处理中产生了新的Java源文件，那么就需要另外一趟处理来处理新生成的源文件。如此往复，直到没有新文件被生成为止。在完成处理之后，再对Java代码进行编译。

编写注解处理器的核心是AnnotationProcessorFactory和AnnotationProcessor两个接口。后者表示的是注解处理器，而前者则是为某些注解类型创建注解处理器的工厂。

使用APT主要目的是简化开发者的工作量，因为APT可以在编译程序源代码的同时，生成一些附属文件（比如源文件、类文件、程序发布描述文字等），这些附属文件的内容也都是与源代码相关的。换句话说，使用APT就是代替了传统的对代码信息和附属文件的维护工作。

命令的运行格式是apt -classpath bin -factory annotation.apt.AssignmentApf src/annotation/work/*.java，即通过-factory来指定注解处理器工厂类的名称。实际上，apt工具在完成处理之后，会自动调用javac来编译处理完成后的源代码。

在JDK 6中，通过JSR 269把自定义注解处理器这一功能进行了规范化，有了新的javax.annotation.processing这个新的API。对Mirror API也进行了更新，形成了新的javax.lang.model包。注解处理器的使用也进行了简化，不需要再单独运行apt这样的命令行工具，Java编译器本身就可以完成对注解的处理。

JDK 6中通过元注解@SupportedAnnotationTypes来声明所支持的注解类型。另外描述程序静态结构的javax.lang.model包使用了不同的类型名称。使用的时候也更加简单，只需要通过javac -processor annotation.pap.AssignmentProcess Demo1.java这样的方式即可。

从原理上讲，注解处理器就是通过反射机制获取被检查方法上的注解信息，然后根据注解元素的值进行特定的处理。

[Getting Started with the Annotation Processing Tool](https://docs.oracle.com/javase/7/docs/technotes/guides/apt/GettingStarted.html)

### annotation process cycle

The way the annotation processor API design solves this problem is that the flow should be either:

1. javac parses
1. javac fires a round
1. lombok gets to go first and adds some accessor methods
1. MapStruct gets to go second and sees them, and generates some stuff.
1. javac is done with the round, but because lombok said stuff changed, another round starts.
1. lombok fires again but doesn't change anything as everything available has already been inspected.
1. MapStruct should draw the same conclusion.
1. javac is done with the round, notices nothing changed, and fires a final no-changes round.
1. lombok picks this up, does nothing.
1. MapStruct picks this up, dos nothing.
1. the final round is done without error and thus javac moves on to bytecode generation.

Or, alternatively, if the order is reversed:

1. javac parses
1. javac fires a round
1. MapStruct gets to go first and doesn't see the accessor methods yet.
1. lombok goes second and adds them. Also marks to javac that more rounds are needed.
1. javac is done with the round, but because lombok said stuff changed, another round starts.
1. MapStruct gets to go again and should pick up on the changes here, modifying what it has done so far / doing more.
1. lombok fires again but doesn't change anything as everything available has already been inspected.
1. javac is done with the round, notices nothing changed, and fires a final no-changes round.
1. MapStruct picks this up, dos nothing.
1. lombok picks this up, does nothing.
1. the final round is done without error and thus javac moves on to bytecode generation.

[annotation process loop](https://github.com/mapstruct/mapstruct/issues/510)