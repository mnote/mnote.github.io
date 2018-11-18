---
layout: default
title: Reflection
---

### Reflect

> Reflection enables Java code to discover information about the fields, methods and constructors of loaded classes, and to use reflected fields, methods, and constructors to operate on their underlying counterparts, within security restrictions.
> The API accommodates applications that need access to either the public members of a target object (based on its runtime class) or the members declared by a given class. It also allows programs to suppress default reflective access control.

Java 反射类

```java
java.lang.Class; //类对象
java.lang.reflect.Constructor; //构造器对象
java.lang.reflect.Field; //属性对象
java.lang.reflect.Method; //方法对象
java.lang.reflect.Modifier; //修饰符对象

//获得指定参数类型params的public构造函数
Constructor getConstructor(Class[] params);
//获得类的所有public构造函数
Constructor[] getConstructors(); 
//获得使用指定参数类型params的构造函数
Constructor getDeclaredConstructor(Class[] params);
//获得类的所有的构造函数
Constructor[] getDeclaredConstructors();

//获得类中命名为name的public字段
Field getField(String name);
//获得类的所有public字段
Field[] getFields();
//获得类中命名为name的字段
Field getDeclaredField(String name);
//获得类中的所有的字段
Field[] getDeclaredFields();

//使用指定参数类型params，获得名称为name的public方法
Method getMethod(String name, Class[] params);
//获得类中所有的public方法
Method[] getMethods();
//使用指定参数类型params，获得命名为name的方法
Method getDeclaredMethod(String name, Class[] params);
//获取类中的所有方法
Method[] getDeclaredMethods();

Class<?> c = Class.forName("com.internal.R$Dim");
Object obj = c.newInstance();
Field field = c.getField("f"); 
field.setAccessible(true);
String val = field.get(obj).toString(); 

```

### jOOR

>jOOR - Fluent Reflection in Java jOOR is a very simple fluent API that gives access to your Java Class structures in a more intuitive way. The JDK’s reflection APIs are hard and verbose to use. Other languages have much simpler constructs to access type meta information at runtime.

[jOOR](https://github.com/jOOQ/jOOR)

```java

int statusHeightId = Reflect.on("com.internal.R$Dim")
							 .create()
							 .field("f")
							 .get();
            
```


### Proxy


```java
// Java Proxy
// 1. 首先实现一个InvocationHandler，方法调用会被转发到该类的invoke()方法。
class LogInvocationHandler implements InvocationHandler{
    private Hello hello;
    public LogInvocationHandler(Hello hello) {
        this.hello = hello;
    }
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        if("sayHello".equals(method.getName())) {
            logger.info("You said: " + Arrays.toString(args));
        }
        return method.invoke(hello, args);
    }
}
// 2. 然后在需要使用Hello的时候，通过JDK动态代理获取Hello的代理对象。
Hello hello = (Hello)Proxy.newProxyInstance(
    getClass().getClassLoader(), // 1. 类加载器
    new Class<?>[] {Hello.class}, // 2. 代理需要实现的接口，可以有多个
    new LogInvocationHandler(new HelloImp()));// 3. 方法调用的实际处理者
    
System.out.println(hello.sayHello("I love you!"));

```

```java
// JDK代理类具体实现
public final class $Proxy0 extends Proxy implements Hello
{
  ...
  public $Proxy0(InvocationHandler invocationhandler)
  {
    super(invocationhandler);
  }
  ...
  @Override
  public final String sayHello(String str){
    ...
    return super.h.invoke(this, m3, new Object[] {str});// 将方法调用转发给invocationhandler
    ...
  }
  ...
}
```

[Java Proxy 和 CGLIB 动态代理原理](http://www.importnew.com/27772.html)
[Java静态代理&动态代理笔记](https://www.jianshu.com/p/e2917b0b9614)
[Java Proxy](https://docs.oracle.com/javase/7/docs/api/java/lang/reflect/Proxy.html)


CGLIB(Code Generation Library)是一个基于ASM的字节码生成库，它允许我们在运行时对字节码进行修改和动态生成。CGLIB通过继承方式实现代理。

```java
// CGLIB动态代理
// 1. 首先实现一个MethodInterceptor，方法调用会被转发到该类的intercept()方法。
class MyMethodInterceptor implements MethodInterceptor{
  ...
    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) throws Throwable {
        logger.info("You said: " + Arrays.toString(args));
        return proxy.invokeSuper(obj, args);
    }
}
// 2. 然后在需要使用HelloConcrete的时候，通过CGLIB动态代理获取代理对象。
Enhancer enhancer = new Enhancer();
enhancer.setSuperclass(HelloConcrete.class);
enhancer.setCallback(new MyMethodInterceptor());
 
HelloConcrete hello = (HelloConcrete)enhancer.create();
System.out.println(hello.sayHello("I love you!"));

```

```java
// CGLIB代理类具体实现
public class HelloConcrete$$EnhancerByCGLIB$$e3734e52 
		extends HelloConcrete 
		implements Factory
{
  ...
  private MethodInterceptor CGLIB$CALLBACK_0; // ~~
  ...
 
  public final String sayHello(String paramString)
  {
    ...
    MethodInterceptor tmp17_14 = CGLIB$CALLBACK_0;
    if (tmp17_14 != null) {
      // 将请求转发给MethodInterceptor.intercept()方法。
      return (String)tmp17_14.intercept(this, 
              CGLIB$sayHello$0$Method, 
              new Object[] { paramString }, 
              CGLIB$sayHello$0$Proxy);
    }
    return super.sayHello(paramString);
  }
  ...
}
```
注意：对于从Object中继承的方法，CGLIB代理也会进行代理，如hashCode()、equals()、toString()等，但是getClass()、wait()等方法不会，因为它是final方法，CGLIB无法代理。