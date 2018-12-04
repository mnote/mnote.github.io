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

[Annotations](https://docs.oracle.com/javase/tutorial/java/annotations/)

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
[ajc](http://www.eclipse.org/aspectj/doc/next/devguide/ajc-ref.html)
[aspectj-maven-plugin](https://www.mojohaus.org/aspectj-maven-plugin/compile-mojo.html)


### Validation

Constraints in Bean Validation are expressed via Java annotations. There are four types of bean constraints to enhance an object model:

field constraints

property constraints

container element constraints

class constraints

None of the default constraints defined by Bean Validation can be placed at class level.

When using field-level constraints field access strategy is used to access the value to be validated. This means the validation engine directly accesses the instance variable and does not invoke the property accessor method even if such an accessor exists.
Constraints can be applied to fields of any access type (public, private etc.). Constraints on static fields are not supported, though.

>When validating byte code enhanced objects, property level constraints should be used, because the byte code enhancing library won’t be able to determine a field access via reflection.
>When using property level constraints property access strategy is used to access the value to be validated, i.e. the validation engine accesses the state via the property accessor method.
>It is recommended to stick either to field or property annotations within one class. It is not recommended to annotate a field and the accompanying getter method as this would cause the field to be validated twice.
>When a class implements an interface or extends another class, all constraint annotations declared on the super-type apply in the same manner as the constraints specified on the class itself.
>The Bean Validation API does not only allow to validate single class instances but also complete object graphs (cascaded validation). To do so, just annotate a field or property representing a reference to another object with @Valid


As of Bean Validation 1.1, constraints can not only be applied to JavaBeans and their properties, but also to the parameters and return values of the methods and constructors of any Java type. That way Bean Validation constraints can be used to specify

the preconditions that must be satisfied by the caller before a method or constructor may be invoked (by applying constraints to the parameters of an executable)

the postconditions that are guaranteed to the caller after a method or constructor invocation returns (by applying constraints to the return value of an executable)

This approach has several advantages over traditional ways of checking the correctness of parameters and return values:

the checks don’t have to be performed manually (e.g. by throwing IllegalArgumentException or similar), resulting in less code to write and maintain

an executable’s pre- and postconditions don’t have to be expressed again in its documentation, since the constraint annotations will automatically be included in the generated JavaDoc. This avoids redundancies and reduces the chance of inconsistencies between implementation and documentation

>Note that declaring method or constructor constraints itself does not automatically cause their validation upon invocation of the executable. Instead, the ExecutableValidator API (see Section 3.2, “Validating method constraints”) must be used to perform the validation, which is often done using a method interception facility such as AOP, proxy objects etc.

Constraints may only be applied to instance methods, i.e. declaring constraints on static methods is not supported. Depending on the interception facility you use for triggering method validation, additional restrictions may apply, e.g. with respect to the visibility of methods supported as target of interception. 

>In addition to the built-in bean and property-level constraints discussed in Section 2.3, “Built-in constraints”, Hibernate Validator currently provides one method-level constraint, @ParameterScriptAssert. This is a generic cross-parameter constraint which allows to implement validation routines using any JSR 223 compatible ("Scripting for the JavaTM Platform") scripting language, provided an engine for this language is available on the classpath.



### Lombok

Lombok does indeed code against internal API, as Sean Patrick Floyd said. However, as lombok is ONLY involved in the compilation phase, its misleading to claim Lombok will only run on a sun VM. It'll only compile on ecj or sun's javac. However, the vast majority of VMs out there, if they ship a compiler at all, are one of those two. For example, the Apple VM ships with stock sun javac, and as such lombok works just fine on macs. Same goes for the soylatte VM, for example.

While for javac we really do have to stick with their updates, partly because of a lot of ongoing work on their compiler right now, we've had to make just 1 minor adjustment to our eclipse support over many many versions of eclipse. So, while we do code against internal API, they are relatively stable bits.

If what lombok does could be done without resorting to internal API, we'd have done something else, but it can't be done, so we resort to internal API usage.

NB: I'm one of the lead developers of lombok, so, I'm probably a little biased :P

http://notatube.blogspot.com/2010/11/project-lombok-trick-explained.html

https://stackoverflow.com/questions/6107197/how-does-lombok-work



[Java Compilation](http://openjdk.java.net/groups/compiler/doc/compilation-overview/index.html)



### Project Lombok - Trick Explained

[Trick Explained](http://notatube.blogspot.com/2010/11/project-lombok-trick-explained.html)
[Creating Custom Transformations](http://notatube.blogspot.com/2010/12/project-lombok-creating-custom.html)
[Don’t use Lombok](https://medium.com/@vgonzalo/dont-use-lombok-672418daa819)
[lombok intro](https://www.baeldung.com/intro-to-project-lombok)

#### Java Compilation

To understand how Project Lombok works, one must first understand how Java compilation works. OpenJDK provides an excellent overview of the compilation process. To paraphrase, compilation has 3 stages: 
1. Parse and Enter
2. Annotation Processing
3. Analyse and Generate

![javac-flow](../assets/image/javac-flow.png)

In the Parse and Enter phase, the compiler parses source files into an Abstract Syntax Tree (AST). Think of the AST as the DOM-equivalent for Java code. Parsing will only throw errors if the syntax is invalid. Compilation errors such as invalid class or method usage are checked in phase 3.

In the Annotation Processing phase, custom annotation processors are invoked. This is considered a pre-compilation phase. Annotation processors can do things like validate classes or generate new resources, including source files. Annotation processors can generate errors that will cause the compilation process to fail. If new source files are generated as a result of annotation processing, then compilation loops back to the Parse and Enter phase and the process is repeated until no new source files are generated.

In the last phase, Analyse and Generate, the compiler generates class files (byte code) from the Abstract Syntax Trees generated in phase 1. As part of this process, the AST is analyzed for broken references (e.g. class not found, method not found), valid flow is checked (e.g. no unreachable statements), type erasure is performed, syntactic sugar is desugared (e.g. enhanced for loops become iterator loops) and finally, if everything is successful, class files are written out.

#### Project Lombok and Compilation

Project Lombok hooks itself into the compilation process as an annotation processor. But Lombok is not your normal annotation processor. Normally, annotation processors only generate new source files whereas Lombok modifies existing classes. 

The trick is that Lombok modifies the AST. It turns out that changes made to the AST in the Annotation Processing phase will be visible to the Analyse and Generate phase. Thus, changing the AST will change the generated class file. For example, if a method node is added to the AST, then the class file will contain that new method. By modifying the AST, Lombok can do things like generate new methods (getter, setter, equals, etc) or inject code into an existing method (e.g. cleaning up resources). 

#### Trick or Hack?

Some people call Lombok's trick a hack, and I'd agree. But don't pass judgement yet. Like any hack, you should examine the risk/reward and alternatives before determining if you are comfortable with it.

The "hack" in Lombok is that, strictly speaking, the annotation processing spec doesn't allow you to modify existing classes. The annotation processing API doesn't provide a mechanism for changing the AST of a class. The clever people at Project Lombok got around this through some unpublished APIs of javac. Since Eclipse uses an internal compiler, Lombok also needs access to internal APIs of the Eclipse compiler.

If Java officially supported compile-time AST transformations then Lombok wouldn't need to rely on backdoor APIs. This makes Project Lombok vulnerable to future changes in the JDK. There is no guarantee the private APIs won't change in a later JDK and break Project Lombok. If that happens, then you're left hoping that the guys at Lombok will be responsive about patching their library to work with the new JDK. Same thing goes for the new Eclipse compilers. Given how often we get a new version of Java, this may not be that big of an issue.


#### Alternatives in Java

There are other alternatives for modifying the behavior of classes. One approach is to use byte-code manipulation at runtime via a library like CGLib or ASM. This is how Hibernate is able to do things like lazily initialize a persistent Collection the first time it is accessed. In general, this can be used to enhance the behavior of existing methods. This trick could possibly be used to implement the @Cleanup behavior in Lombok, so that a resource is closed when it goes out of scope. Runtime byte-code manipulation is no help for generating getters and setters which you intend to reference in source code.

Another approach is to use byte-code manipulation on the class files. For example, Kohsuke Kawaguchi of Hudson fame created a library called Bridge Method Injector, that helps perserve binary compatibility when changing a method's return type in a way that is source compatible but not binary compatible. Kohsuke implements this by using ASM to modify the byte-code in a class file after compilation. This trick could be used to mimic the behavior of the Getter/Setter/ToString/EqualsHashCode annotations of Lombok with one caveat: generated methods would only be visible to classes external to your library but not to classes within your library. In other words, projects that depended on classes in your library as a jar would see your getters and setters, but classes within your library would not see these getters and setters at compile time.

The trick that makes Lombok special is that the code it generates is weaved in before Analyze and Generate phase of compilation. This allows classes within the same compilation unit to have visibility to the generated methods. It appears another library called Juast may be using a similar trick (modifying the AST) to do things like operator overloading. For some developers, the immediate benefits of Lombok's approach may outweigh the potential risks.


#### Alternatives outside Java

If you're willing to switch to Scala, Lombok becomes a moot point. Scala has Case classes that eliminate the getter/setter/toString/hashCode/equals boiler-plate. Scala also has Automatic Resource Management that covers Lombok's @Cleanup behavior.

Another option is Groovy if you don't care about static typing. Groovy has similar support for Scala-like Case classes. Groovy also officially supports compile-time, AST transformations.

#### Final thoughts

Project Lombok can do tricks that are impossible via other dynamic code generation methods in Java but you should be aware the it uses some back-door APIs to accomplish it.





### Immutables

https://immutables.github.io/immutable.html


### AutoValue

https://www.baeldung.com/introduction-to-autovalue


Eclipse Compiler for Java (ECJ)
