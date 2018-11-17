---
layout: default
title: Spring MVC
---

You are right - there are two different application contexts, the root application context loaded up by ContextLoaderListener (at the point the ServletContext gets initialized), and the Web Context (loaded up by DispatcherServlet), the root application context is the parent of the Web context.

Now, since these are two different application contexts, they get acted on differently - if you define component-scan for your services in application context, then all the beans for the services get created here.

When your Dispatcher servlet loads up it will start creating the Web Context, at some point(driven by <mvc:annotation-driven/> it will create a mapping for your uri's to handler methods, it will get the list of beans in the application context(which will be the web application context, not the Root application Context) and since you have not defined a component-scan here the controller related beans will not be found and the mappings will not get created, that is the reason why you have to define a component-scan in the dispatcher servlets context also.

A good practice is to exclude the Controller related beans in the Root Application Context:

    <context:component-scan base-package="package">
        <context:exclude-filter expression="org.springframework.stereotype.Controller" type="annotation"/>
    </context:component-scan>

and only controller related one's in Web Application Context:

    <context:component-scan base-package="package" use-default-filters="false">
        <context:include-filter expression="org.springframework.stereotype.Controller" type="annotation" />
    </context:component-scan>

[Dispatcher Servlet Config](http://stackoverflow.com/questions/11453530/applicationcontext-not-finding-controllers-for-servlet-context)

    <context:component-scan base-package="" /> 
tells Spring to scan those packages for Annotations.

    <mvc:annotation-driven> 
registers a RequestMappingHanderMapping, a RequestMappingHandlerAdapter, and an ExceptionHandlerExceptionResolver to support the annotated controller methods like @RequestMapping, @ExceptionHandler, etc. that come with MVC.
This also enables a ConversionService that supports Annotation driven formatting of outputs as well as Annotation driven validation for inputs. It also enables support for @ResponseBody which you can use to return JSON data.

[annotation](http://stackoverflow.com/questions/13661985/spring-mvc-difference-between-contextcomponent-scan-and-annotation-driven)
[interceptors](http://stackoverflow.com/questions/3230633/how-to-register-handler-interceptors-with-spring-mvc-3-0)

[Spring MVC](http://www.slideshare.net/ilio-catallo/spring-mvc-the-basics?qid=002fa7ce-c8fb-431f-bb6a-a3bb2a3f6f1d&v=default&b=&from_search=23)
[Srping MVC](http://www.slideshare.net/analizator/spring-framework-mvc?qid=002fa7ce-c8fb-431f-bb6a-a3bb2a3f6f1d&v=qf1&b=&from_search=1)
