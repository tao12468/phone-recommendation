# 代码目录说明

这个目录专门存放系统代码。文档和项目说明放在上层目录，避免代码与资料混在一起。

## 目录结构

```text
code/
├── app.py                 # Flask 后端入口
├── algorithms/            # 推荐算法与特征工程
├── crawler/               # 手机数据爬虫
├── data/                  # 手机样本、清洗、MySQL 与 Excel 脚本
├── static/                # 前端页面、脚本与样式
└── tests/                 # 自动化测试
```

## 启动方式

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe code\app.py
```

## 测试方式

在项目根目录执行：

```powershell
Set-Location code
..\.venv\Scripts\python.exe -m pytest -q
Set-Location ..
```

## 后续扩展

- 新算法放在 `algorithms/`
- 新数据文件或建表脚本放在 `data/`
- 新前端文件放在 `static/`
- 新接口测试放在 `tests/`
