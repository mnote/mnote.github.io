---
layout: post
title: Spring Boot
category: spring
---

Spring Configuration
--------------------

While Spring was lightweight in terms of component code, it was heavyweight in terms of configuration. Component-scanning reduced configuration and Java configuration made it less awkward, but Spring still required a lot of configuration.

* Spring 1.0: dependency injection and declarative transactions
* Spring 2.0: custom XML namespaces for configuration
* Spring 2.5: annotation oriented dependency injection
* Spring 3.0: Java-based configuration
* Spring 4.0: conditional configuration
* Spring Boot: automatic configuration

Like any framework, Spring does a lot for you, but it demands that you do a lot for it in return. Moreover, project dependency management is a thankless task.


Spring Boot essentials
----------------------

### Automatic configuration

If Spring Boot detects that you have the H2 database library in your application’s class- path, it will automatically configure an embedded H2 database. If JdbcTemplate is in the classpath, then it will also configure a JdbcTemplate bean for you. There’s no need for you to worry about configuring those beans. They’ll be configured for you, ready to inject into any of the beans you write. 

### Starter dependencies

Starter dependencies are really just special Maven (and Gradle) dependencies that take advantage of transitive dependency resolution to aggregate commonly used libraries under a handful of feature defined dependencies.  
Also note that Spring Boot’s starter dependencies free you from worrying about which versions of these libraries you need. The versions of the libraries that the start- ers pull in have been tested together so that you can be confident that there will be no incompatibilities between them.

### Command line interface

Also note that Spring Boot’s starter dependencies free you from worrying about which versions of these libraries you need. The versions of the libraries that the starters pull in have been tested together so that you can be confident that there will be no incompatibilities between them.  
The CLI detected those types being used, and it knows which starter dependencies to add to the classpath to make it work.  
Spring Boot’s CLI is an optional piece of Spring Boot’s power. Although it provides tremendous power and simplicity for Spring development, it also introduces a rather unconventional development model.

### The Actuator

The Actuator instead offers the ability to inspect the internals of your application at runtime.  
The Actuator exposes this information in two ways: via web endpoints or via a shell interface. In the latter case, you can actually open a secure shell (SSH) into your application and issue commands to inspect your application as it runs.

* Spring Boot is not an application server.
* Spring Boot doesn’t implement any enterprise Java specifications such as JPA or JMS.
* Spring Boot doesn’t employ any form of code generation to accomplish its magic.
* Spring Boot project is just a regular Spring project that happens to leverage Spring Boot starters and auto configuration.


### spring-boot-cli

The Spring Boot CLI takes Spring Boot’s frictionless development model to a whole new level by enabling quick and easy development with Groovy from the command line.

* download: [spring-boot-cli]  
* set path:

```
vim ~/.bash_profile
export PATH=~/spring-boot-cli/bin:$PATH
source ~/.bash_profile
spring --version
```

* brew install

```
brew tap pivotal/tap
brew install springboot
spring --version
```


### Spring Initializr

Sometimes the hardest part of a project is getting started.

Up until recently, creating an application with Spring required you to do a lot of work for the framework. Sure, Spring has long had fantastic features for developing amazing applications. But it was up to you to add all of the library dependencies to the project’s build specification. And it was your job to write configuration to tell Spring what to do.

The Spring Initializr is ultimately a web application that can generate a Spring Boot project structure for you. It doesn’t generate any application code, but it will give you a basic project structure and either a Maven or a Gradle build specification to build your code with. All you need to do is write the application code.

Even the empty directories have significance in a Spring Boot application. The static directory is where you can put any static content (JavaScript, stylesheets, images, and so on) to be served from the web application. And, as you’ll see later, you can put tem- plates that render model data in the templates directory.


### @SpringBootApplication

@SpringBootApplication combines three other useful annotations:

#### Spring’s @Configuration

Designates a class as a configuration class using Spring’s Java-based configuration.

#### Spring’s @ComponentScan

Enables component-scanning so that the web con- troller classes and other components you write will be automatically discovered and registered as beans in the Spring application context.

#### Spring Boot’s @EnableAutoConfiguration

It’s the one line of configuration that enables the magic of Spring Boot auto-configuration. This one line keeps you from having to write the pages of configuration that would be required otherwise.

#### SpringApplication.run

You’ll almost never need to change ReadingListApplication.java. If your application requires any additional Spring configuration beyond what Spring Boot auto-configuration provides, it’s usually best to write it into separate @Configuration configured classes. (They’ll be picked up and used by component-scanning.)

#### application.properties

With this line, you’re configuring the embedded Tomcat server to listen on port 8000 instead of the default port 8080.

	server.port=8000

#### facet-based dependencies

A starter dependency is essentially a Maven POM that defines transitive dependencies on other libraries that together provide support for some functionality. Many of these starter dependencies are named to indicate the facet or kind of functionality they provide.

#### auto configuration

In a nutshell, Spring Boot auto-configuration is a runtime (more accurately, applica- tion startup-time) process that considers several factors to decide what Spring configu- ration should and should not be applied. T

* Is Spring’s JdbcTemplate available on the classpath? If so and if there is a Data- Source bean, then auto-configure a JdbcTemplate bean.
* Is Thymeleaf on the classpath? If so, then configure a Thymeleaf template resolver, view resolver, and template engine.
* Is Spring Security on the classpath? If so, then configure a very basic web secu- rity setup.

There are nearly 200 such decisions that Spring Boot makes with regard to auto- configuration every time an application starts up, covering such areas as security, integration, persistence, and web development. All of this auto-configuration serves to keep you from having to explicitly write configuration unless absolutely necessary.

#### conditional configuration

Configuration is a central element of the Spring Framework, and there must be something that tells Spring how to run your application.

When you add Spring Boot to your application, there’s a JAR file named __spring-boot-autoconfigure__ that contains several configuration classes. Every one of these configuration classes is available on the application’s classpath and has the opportunity to contribute to the configuration of your application.

What makes all of this configuration special, however, is that it leverages Spring’s support for conditional configuration, which was introduced in Spring 4.0.

```java
@Configuration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({ Registrar.class, DataSourcePoolMetadataProvidersConfiguration.class })
public class DataSourceAutoConfiguration {

		@Bean
		@ConditionalOnMissingBean(JdbcOperations.class)
		public JdbcTemplate jdbcTemplate() {
			return new JdbcTemplate(this.dataSource);
		}
		
}
```

Although auto-configuration is a convenient way to work with Spring, it also represents an opinionated approach to Spring development.


[start.spring.io](http://start.spring.io)

[spring-boot-cli]: http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#getting-started-installing-the-cli


