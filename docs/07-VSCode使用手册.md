# VS Code 使用手册

这份手册帮助你从零学会用 VS Code 写代码、跑项目和用 Git。

## 1. VS Code 是什么

VS Code 是一个轻量级代码编辑器，支持 Python、Java、前端、Markdown 等语言。

下载地址：

```text
https://code.visualstudio.com/
```

## 2. 安装后先做的两件事

### 2.1 安装中文语言包

打开扩展面板，搜索：

```text
Chinese (Simplified) Language Pack
```

安装后重启 VS Code，界面变中文。

### 2.2 安装常用扩展

```text
Python
Extension Pack for Java
GitLens
Prettier
Live Server
```

## 3. 打开项目

方法一：菜单栏“文件 -> 打开文件夹”，选择项目目录。

方法二：命令行打开：

```powershell
code "D:\Administrator\Documents\新建文件夹\phone-recommendation"
```

打开后，左侧资源管理器会显示项目文件。

## 4. 界面区域

```text
左侧：资源管理器、搜索、源代码管理、扩展
中间：代码编辑区
底部：终端
右侧：代码大纲、预览
```

## 5. 终端使用

打开终端：

```text
菜单：终端 -> 新建终端
快捷键：Ctrl + `
```

终端里可以运行：

```powershell
python app.py
..\.venv\Scripts\python.exe -m pytest -q
git status
```

## 6. 文件操作

```text
新建文件：在资源管理器右键 -> 新建文件
新建文件夹：右键 -> 新建文件夹
重命名：选中文件按 F2
删除：选中文件按 Delete
```

## 7. 常用编辑快捷键

```text
Ctrl + S        保存
Ctrl + Z        撤销
Ctrl + Y        重做
Ctrl + C        复制
Ctrl + X        剪切
Ctrl + V        粘贴
Ctrl + F        查找
Ctrl + H        替换
Ctrl + /        注释当前行
Shift + Alt + F 格式化代码
Alt + 上下方向键 移动当前行
Ctrl + P        快速打开文件
```

## 8. 搜索文件

按 `Ctrl + P`，输入文件名可以快速打开。

按 `Ctrl + Shift + F`，可以搜索整个项目里的文字。

## 9. 运行 Python

先安装 Python 扩展，然后：

1. 打开 `.py` 文件
2. 点击右上角运行按钮
3. 或按 `F5` 调试

## 10. 运行 Java

先安装 Java 扩展，然后：

1. 安装 JDK
2. 打开 `.java` 文件
3. 点击右上角运行按钮
4. 或按 `F5` 调试

如果项目是 Maven 项目，VS Code 会自动识别 `pom.xml`。

## 11. 使用 Git

左侧栏点击“源代码管理”图标。

常用操作：

```text
查看修改文件
点 + 暂存文件
输入提交信息
点 ✓ 提交
点 ... 选择推送
```

也可以使用终端：

```powershell
git add .
git commit -m "说明"
git push
```

## 12. 调试

按 `F5` 开始调试：

```text
设置断点：点击行号左侧
单步执行：F10
进入函数：F11
继续运行：F5
停止调试：Shift + F5
```

断点就是让程序暂停在这一行，方便查看变量值。

## 13. 常用设置

按 `Ctrl + ,` 打开设置。

建议开启：

```text
自动保存：Auto Save
代码格式化：Format on Save
文件换行：自动换行
```

## 14. 项目推荐工作流

在这个手机推荐项目里，通常这样使用 VS Code：

```text
1. 打开项目文件夹
2. 在终端启动后端
3. 修改 app.py 或前端文件
4. 用源代码管理提交改动
5. 运行测试验证
6. 刷新浏览器看效果
```

## 15. 常见问题

### 终端打不开

检查 VS Code 是否被安全软件拦截，或重启 VS Code。

### Python 解释器不对

按 `Ctrl + Shift + P`，输入 `Python: Select Interpreter`，选择项目的 `.venv`。

### Java 不能运行

检查 JDK 是否安装：

```powershell
java -version
```

并确认已安装 Java 扩展。

### 中文乱码

文件右下角编码选择 `UTF-8`。

## 16. 学习建议

不要一次记住所有快捷键，先掌握：

```text
打开文件夹
新建和保存文件
打开终端
运行代码
Git 提交
```

熟练后再逐步学习调试和更多快捷键。
