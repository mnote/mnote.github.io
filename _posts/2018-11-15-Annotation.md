---
layout: default
title: Annotation
category: aspectj
---

Annotation其实是一种接口。通过Java的反射机制相关的API来访问Annotation信息

>代码与配置同步，跟踪代码依赖性，实现替代配置文件功能

>与具体场景相关的配置应该使用注解的方式与数据关联，与具体场景无关的配置放于配置文件中。

>通过设置注解的@Retention级别在运行时使用反射对不同的注解进行处理

>编译时格式检查

>生成文档


### 元注解

元注解的作用就是负责注解其他注解。Java5.0定义了4个标准的meta-annotation类型，它们被用来提供对其它 annotation类型作说明。

* @Target
* @Retention
* @Documented
* @Inherited

@Documented 表示含有该注解类型的元素(带有注释的)会通过javadoc或类似工具进行文档化,类型声明是用@Documented 来注解的，这种类型的注解被作为被标注的程序成员的公共API

### 自定义注解

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

### 注解处理

如果没有用来读取注解的方法和工作，那么注解也就不会比注释更有用处了。Java SE 5扩展了反射机制的API，使用`java.lang.reflect.AnnotatedElement`快速的构造自定义注解处理器。

```java
Field[] fields = clazz.getDeclaredFields();
for(Field field :fields){
	if(field.isAnnotationPresent(FruitColor.class)){ 
		FruitColor fruitColor= (FruitColor) field.getAnnotation(FruitColor.class);           
	}
}
```

### APT
APT（Annotation Processing Tool）是一个命令行工具，它对源代码文件进行检测找出其中的annotation后，使用annotation processors来处理annotation。

在程序中添加的注解，可以在编译时刻或是运行时刻来进行处理。在编译时刻处理的时候，是分成多趟来进行的。如果在某趟处理中产生了新的Java源文件，那么就需要另外一趟处理来处理新生成的源文件。如此往复，直到没有新文件被生成为止。在完成处理之后，再对Java代码进行编译。

编写注解处理器的核心是AnnotationProcessorFactory和AnnotationProcessor两个接口。后者表示的是注解处理器，而前者则是为某些注解类型创建注解处理器的工厂。

使用APT主要目的是简化开发者的工作量，因为APT可以在编译程序源代码的同时，生成一些附属文件（比如源文件、类文件、程序发布描述文字等），这些附属文件的内容也都是与源代码相关的。换句话说，使用APT就是代替了传统的对代码信息和附属文件的维护工作。

命令的运行格式是apt -classpath bin -factory annotation.apt.AssignmentApf src/annotation/work/*.java，即通过-factory来指定注解处理器工厂类的名称。实际上，apt工具在完成处理之后，会自动调用javac来编译处理完成后的源代码。

在JDK 6中，通过JSR 269把自定义注解处理器这一功能进行了规范化，有了新的javax.annotation.processing这个新的API。对Mirror API也进行了更新，形成了新的javax.lang.model包。注解处理器的使用也进行了简化，不需要再单独运行apt这样的命令行工具，Java编译器本身就可以完成对注解的处理。

JDK 6中通过元注解@SupportedAnnotationTypes来声明所支持的注解类型。另外描述程序静态结构的javax.lang.model包使用了不同的类型名称。使用的时候也更加简单，只需要通过javac -processor annotation.pap.AssignmentProcess Demo1.java这样的方式即可。

从原理上讲，注解处理器就是通过反射机制获取被检查方法上的注解信息，然后根据注解元素的值进行特定的处理。

[Getting Started with the Annotation Processing Tool](https://docs.oracle.com/javase/7/docs/technotes/guides/apt/GettingStarted.html)

### Annotation Process Flow

The way the annotation processor API design flow should be either:

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

[Annotation Process Flow](https://github.com/mapstruct/mapstruct/issues/510)

### Java Proxy and CGLib

[Java Proxy 和 CGLIB 动态代理原理](http://www.importnew.com/27772.html)

### AOP

编织（Weaving）：将切面应用到目标对象从而创建一个新的代理对象的过程。这个过程可以发生在编译期、类装载期及运行期，当然不同的发生点有着不同的前提条件。譬如发生在编译期的话，就要求有一个支持这种AOP实现的特殊编译器（如AspectJ编译器）；发生在类装载期，就要求有一个支持AOP实现的特殊类装载器；只有发生在运行期，则可直接通过Java语言的反射机制与动态代理机制来动态实现（如Spring）。

AOP代理（AOP Proxy）：将通知（Advice）应用到目标对象（Target Object）之后被动态创建的对象。可以简单地理解为，代理对象的功能等于目标对象的核心业务逻辑功能加上共有功能。代理对象对于使用者而言是透明的，是程序运行过程中的产物。

引入（Introduction）：添加方法或字段到被通知的类。


#### Method Signature

> @注解 访问权限 返回值类型 包名.函数名(参数) 
> 
> * @注解和访问权限（public/private/protect，以及static/final）属于可选项。如果不设置它们，则默认都会选择。以访问权限为例，如果没有设置访问权限作为条件，那么public，private，protect及static、final的函数都会进行搜索。  
> 
> * 返回值类型就是函数的返回值类型。如果不限定类型的话，就用*通配符表示  
> * 包名.函数名用于查找匹配的函数。可以使用通配符，包括`*`和`..`以及`+`号。其中`*`号用于匹配除`.`号之外的任意字符，而`..`则表示任意子package，`+`号表示子类。比如：
> 	* java.*.Date：可以表示java.sql.Date，也可以表示java.util.Date  
>   * Test*：可以表示TestBase，也可以表示TestDervied  
>   * java..*：表示java任意子类  
>   * java..*Model+：表示Java任意package中名字以Model结尾的子类，比如TabelModel，TreeModel 等  
> * 最后来看函数的参数。参数匹配比较简单，主要是参数类型，比如：  
>     * (int, char)：表示参数只有两个，并且第一个参数类型是int，第二个参数类型是char  
>     * (String, ..)：表示至少有一个参数。并且第一个参数类型是String，后面参数类型不限。  
>     * `..`代表任意参数个数和类型  
>     * (Object ...)：表示不定个数的参数，且类型都是Object，这里的`...`不是通配符，而是Java中代表不定参数的意思  
> 

往advice传参数比较简单，就是利用前面提到的this(),target(),args()等方法


### jcabi-aspects

[Java Method Logging with AOP and Annotations](https://www.yegor256.com/2014/06/01/aop-aspectj-java-method-logging.html)

[AspectJ切入点匹配语法](https://github.com/doc-spring/AspectJ)
[AspectJ切入点语法详解](https://www.mekau.com/4880.html)