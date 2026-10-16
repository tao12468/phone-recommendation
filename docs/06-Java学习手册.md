# Java 学习手册

这份手册面向有 Python 基础、准备学习 Java 和 Spring Boot 的人。目标是能看懂并写出后端项目代码。

## 1. Java 是什么

Java 是一门强类型、面向对象的编程语言，广泛用于后端开发。

和 Python 的主要区别：

| 对比项 | Python | Java |
| --- | --- | --- |
| 类型 | 动态类型 | 强静态类型 |
| 编译 | 解释执行 | 先编译再运行 |
| 语法 | 简洁 | 相对严格 |
| 面向对象 | 支持 | 强制面向对象 |
| 后端框架 | Flask、Django | Spring Boot |

## 2. 安装环境

需要安装：

```text
JDK：Java 开发工具包，建议 JDK 17 或 21
Maven：项目构建和依赖管理工具
IDE：IntelliJ IDEA
```

检查是否安装成功：

```powershell
java -version
mvn -version
```

## 3. 第一个 Java 程序

新建文件 `Hello.java`：

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello Java");
    }
}
```

运行：

```powershell
javac Hello.java
java Hello
```

要点：

- 文件名必须和类名相同
- `main` 是程序入口
- 每条语句以分号结尾

## 4. 变量和数据类型

Java 必须声明变量类型：

```java
int age = 20;
double price = 3999.0;
boolean isStudent = true;
String name = "陶华志";
```

常用类型：

```text
int      整数
long     大整数
double   小数
boolean  真或假
String   字符串
```

## 5. 条件判断

```java
int score = 85;

if (score >= 90) {
    System.out.println("优秀");
} else if (score >= 60) {
    System.out.println("及格");
} else {
    System.out.println("不及格");
}
```

## 6. 循环

```java
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}
```

## 7. 方法

方法相当于 Python 的函数：

```java
public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        int result = add(3, 5);
        System.out.println(result);
    }
}
```

## 8. 数组和集合

数组：

```java
int[] numbers = {1, 2, 3, 4};
```

常用集合：

```java
import java.util.ArrayList;
import java.util.HashMap;

ArrayList<String> list = new ArrayList<>();
list.add("华为");
list.add("小米");

HashMap<String, Integer> map = new HashMap<>();
map.put("预算", 4000);
```

## 9. 类和对象

Java 一切都是对象。

```java
public class Phone {
    private String name;
    private double price;

    public Phone(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public String getName() {
        return name;
    }
}
```

创建对象：

```java
Phone phone = new Phone("小米14", 3999);
System.out.println(phone.getName());
```

## 10. 面向对象三大特性

```text
封装：把数据和方法放在类里，用 private 和 public 控制访问
继承：子类继承父类的属性和方法
多态：同一个方法，不同对象表现不同
```

## 11. 异常处理

```java
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("不能除以 0");
} finally {
    System.out.println("一定会执行");
}
```

## 12. 文件读写

```java
import java.nio.file.Files;
import java.nio.file.Path;

String text = Files.readString(Path.of("data.txt"));
Files.writeString(Path.of("out.txt"), "内容");
```

## 13. 用 JDBC 操作 MySQL

JDBC 是 Java 连接数据库的方式。

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

String url = "jdbc:mysql://127.0.0.1:3306/phone_recommender";
Connection conn = DriverManager.getConnection(url, "root", "密码");

Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM phones_clean");

while (rs.next()) {
    System.out.println(rs.getString("name"));
}
```

## 14. Maven 是什么

Maven 用来管理项目依赖和构建。

项目里最重要的文件是 `pom.xml`，它声明了依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

## 15. Spring Boot 入门

Spring Boot 是 Java 后端最常用的框架。

一个接口：

```java
@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello Spring Boot";
    }
}
```

对应你现在的 Flask 接口：

```python
@app.get("/hello")
def hello():
    return "Hello Flask"
```

Spring Boot 项目通常分层：

```text
Controller  接收请求
Service     业务逻辑
DAO         数据访问
```

## 16. 建议学习顺序

```text
第一步：基础语法、变量、条件、循环
第二步：方法、数组、集合
第三步：类和对象、封装、继承、多态
第四步：异常、文件、JDBC
第五步：Maven
第六步：Spring Boot 基础
第七步：写一个完整的增删改查接口
```

## 17. 练习任务

学完基础后，试着完成：

```text
[ ] 写一个类 Phone，包含名称、价格、品牌
[ ] 用 ArrayList 保存 10 个 Phone
[ ] 按价格排序输出
[ ] 用 JDBC 从 MySQL 读取手机表
[ ] 用 Spring Boot 写一个 /api/phones 接口
```

## 18. 常见错误

```text
忘记分号
类名和文件名不一致
字符串用单引号
没有导入 import
NullPointerException：空对象调用了方法
```

把这些基础掌握后，就可以把手机推荐项目的 Flask 后端逐步迁移到 Spring Boot。
