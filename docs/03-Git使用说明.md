# Git 使用说明

本文说明如何在这个项目中用 Git 管理代码版本。这里以 PowerShell 为例，所有命令都在项目根目录 `phone-recommendation` 下执行。

## 1. 为什么要这样管理

项目目录现在分成了几类：

- `code/`：系统代码，是 Git 管理的核心
- `docs/`：需求拆解、学习路线、使用说明等文档
- `requirements.txt`：依赖清单
- `.venv/`：本地虚拟环境，不提交
- `__pycache__/`、`.pytest_cache/`：自动生成的缓存，不提交

这样分开后，代码改动不会和文档、临时文件混在一起，查看提交历史时也更清楚。

## 2. 第一次初始化仓库

进入项目根目录：

```powershell
Set-Location "D:\Administrator\Documents\新建文件夹\phone-recommendation"
git init
```

查看当前状态：

```powershell
git status
```

首次提交：

```powershell
git add .
git commit -m "chore: 初始化项目结构与阶段1最小可运行版本"
```

## 3. 常用日常命令

查看哪些文件被修改：

```powershell
git status
```

查看具体修改内容：

```powershell
git diff
```

只把代码目录加入暂存区：

```powershell
git add code/
```

把全部修改加入暂存区：

```powershell
git add .
```

提交一个版本：

```powershell
git commit -m "feat: 新增手机列表接口"
```

查看提交历史：

```powershell
git log --oneline --graph --all
```

## 4. 推荐的提交信息格式

每次提交只做一件清楚的事情，信息采用“类型 + 说明”的格式：

| 类型 | 用途 | 示例 |
| --- | --- | --- |
| feat | 新增功能 | feat: 新增推荐接口 |
| fix | 修复问题 | fix: 修复预算筛选错误 |
| refactor | 重构代码 | refactor: 调整推荐评分函数 |
| test | 测试相关 | test: 增加手机详情测试 |
| docs | 文档相关 | docs: 补充 Git 使用说明 |
| chore | 项目维护 | chore: 更新依赖清单 |

## 5. 分支工作流

建议不要在 `main` 分支上直接写新功能，而是每个阶段开一个分支。

创建并切换到新分支：

```powershell
git switch -c feature/stage2-database
```

完成一个阶段后，切回主分支：

```powershell
git switch main
```

合并功能分支：

```powershell
git merge feature/stage2-database
```

删除已经合并的分支：

```powershell
git branch -d feature/stage2-database
```

## 6. 每一阶段如何提交

以“阶段 2 数据库与数据层”为例，可以拆成多次小提交：

```powershell
git switch -c feature/stage2-database

git add code/data/schema.sql
git commit -m "feat: 新增手机表结构"

git add code/app.py
git commit -m "feat: 手机数据改为数据库读取"

git add code/tests/
git commit -m "test: 增加数据库相关测试"

git switch main
git merge feature/stage2-database
```

原则是：一次提交对应一个可理解的改动，不要等到全部写完才提交一次。

## 7. 连接远程仓库

如果你已经有 GitHub、Gitee 或 GitLab 账号，可以先创建一个空的私有仓库，然后执行：

```powershell
git remote add origin https://github.com/你的用户名/phone-recommendation.git
git push -u origin main
```

之后把本地提交推送到远程：

```powershell
git push
```

拉取远程最新代码：

```powershell
git pull
```

从远程克隆到新电脑：

```powershell
git clone https://github.com/你的用户名/phone-recommendation.git
```

## 8. 哪些内容不应该提交

`.gitignore` 已经排除了虚拟环境、缓存、数据库文件和本地配置。需要注意：

- 不要把密码、密钥、Token 写进代码
- 不要把大型数据集或安装包提交进 Git
- 不要把 `.venv/`、`__pycache__/`、`.pytest_cache/` 提交进去
- 如果以后使用 `.env` 保存数据库密码，它也应该被忽略

## 9. 常用检查命令汇总

```powershell
git status
git diff
git log --oneline --graph --all
git branch -a
git remote -v
```

## 10. 本项目当前阶段建议

代码已经统一放进 `code/`。建议现在先初始化仓库并完成第一次提交，之后每完成一个小步骤就提交一次，这样即使后面改错，也能随时回到之前的版本。
