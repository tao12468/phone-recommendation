# 基于数据驱动的个性化手机推荐平台

一个基于 Web 的个性化手机推荐系统，实现从手机数据采集、清洗、特征工程到混合推荐、行为反馈闭环的完整流程。

## 项目简介

系统面向有购机需求的用户，通过采集用户偏好与用户行为，结合手机参数数据，为用户生成个性化手机推荐列表，并支持手机浏览、详情查看、收藏和机型对比。

主要能力：

- 用户注册、登录与 JWT 鉴权
- 手机数据采集、清洗与特征工程
- 基于内容过滤的推荐
- 基于用户的协同过滤推荐
- 内容过滤与协同过滤的混合推荐
- 用户行为采集与偏好动态更新
- 手机详情、收藏与机型横向对比

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript
- 数据库：MySQL
- 数据处理：Pandas、NumPy、scikit-learn
- 爬虫：Requests + BeautifulSoup

## 系统流程

```text
数据采集 -> 数据清洗 -> 特征工程 -> 混合推荐 -> 行为反馈 -> 偏好更新
```

## 目录结构

```text
phone-recommendation/
├── code/
│   ├── app.py                    # Flask 后端入口
│   ├── auth_utils.py             # JWT 令牌
│   ├── algorithms/               # 特征工程与推荐算法
│   ├── crawler/                  # 手机数据爬虫
│   ├── data/                     # 数据处理与数据库脚本
│   ├── static/                   # 前端页面
│   └── tests/                    # 自动化测试
├── docs/                         # 项目文档
├── requirements.txt
└── .gitignore
```

## 快速启动

### 1. 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 准备 MySQL

确保本机 MySQL 服务已启动，并创建数据库账号。后端通过以下环境变量连接数据库：

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "你的MySQL密码"
$env:MYSQL_DATABASE = "phone_recommender"
```

### 3. 启动后端

```powershell
Set-Location code
..\.venv\Scripts\python.exe app.py
```

浏览器访问：

```text
http://127.0.0.1:5000/app
```

## 数据流水线

### 采集手机数据

```powershell
Set-Location code
..\.venv\Scripts\python.exe crawler\zol_spider.py list --max-pages 5 --brands 613,1795,1673,544,98,50840,55075,34645,35579,1434,55535,35005,55731,295,642 --out data\zol_phone_list.json
..\.venv\Scripts\python.exe crawler\zol_spider.py details --list data\zol_phone_list.json --max-items 1000 --out data\phones_raw.json
```

### 清洗并写入 MySQL

```powershell
..\.venv\Scripts\python.exe -m data.run_pipeline --password 你的MySQL密码
```

### 生成特征

```powershell
..\.venv\Scripts\python.exe -m data.build_features --password 你的MySQL密码
```

### 生成示例交互数据

```powershell
..\.venv\Scripts\python.exe -m data.seed_interactions --password 你的MySQL密码
```

## 核心模块

| 模块 | 说明 |
| --- | --- |
| `crawler/zol_spider.py` | 手机数据爬虫 |
| `data/clean_rules.py` | 数据清洗规则 |
| `data/impute_missing.py` | 缺失值填充 |
| `data/mysql_writer.py` | MySQL 写入 |
| `data/run_pipeline.py` | 数据流水线入口 |
| `algorithms/feature_engineering.py` | 特征工程 |
| `algorithms/content_recommender.py` | 内容过滤推荐 |
| `algorithms/collaborative_recommender.py` | 协同过滤推荐 |
| `algorithms/hybrid_recommender.py` | 混合推荐 |
| `algorithms/feedback_engine.py` | 行为反馈与偏好更新 |
| `data/user_repository.py` | 用户注册登录 |

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户 |
| GET | `/api/phones/all` | 手机列表 |
| GET | `/api/phones/detail/<id>` | 手机详情 |
| GET | `/api/phones/compare?ids=1,2` | 机型对比 |
| GET | `/api/recommendations/hybrid` | 混合推荐 |
| GET | `/api/recommendations/content` | 内容过滤推荐 |
| GET | `/api/recommendations/collaborative` | 协同过滤推荐 |
| POST | `/api/behavior` | 行为上报 |
| GET | `/api/me/preferences` | 用户偏好 |
| GET | `/api/me/favorites` | 用户收藏 |
| DELETE | `/api/me/favorites/<id>` | 取消收藏 |

## 测试

```powershell
Set-Location code
..\.venv\Scripts\python.exe -m pytest -q
```

## 许可证

本项目仅用于课程学习与毕业设计。
