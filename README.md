# 基于数据驱动的个性化手机推荐平台（从零开始版）

本项目根据《基于数据驱动的个性化手机推荐平台设计与实现》开题报告，从头开始实现。

当前进度：阶段 0、阶段 1 已完成，数据采集已完成 1000 条手机原始数据。

## 分阶段实现思路

为了便于边学边做，先把系统拆成 10 个阶段：

1. 项目初始化与环境确认
2. 最小可运行闭环
3. 数据库与数据层
4. 用户与偏好采集
5. 数据采集与特征工程
6. 混合推荐算法
7. 行为反馈闭环
8. Web 前端完善
9. 系统集成、部署与测试
10. 毕业论文撰写与答辩准备

详细任务见 [docs/00-学习路线图.md](docs/00-学习路线图.md)。

## 技术路线

为了让系统能快速运行起来，前期采用：

- 后端：Python + Flask，提供 RESTful API
- 前端：HTML + CSS + JavaScript，浏览器直接访问
- 数据库：先使用 SQLite 跑通逻辑，再迁移到 MySQL
- 推荐算法：NumPy / scikit-learn 实现内容过滤、协同过滤与混合推荐
- 知识图谱：先用关系表模拟，再迁移到 Neo4j
- 爬虫：Requests + BeautifulSoup，后续再扩展为 Scrapy

后期会按开题报告补上 Spring Boot + Vue + MySQL + Redis + Neo4j 的正式技术方案。

## 项目结构

```text
phone-recommendation/
├── code/                 # 全部代码，按模块进一步拆分
│   ├── app.py            # 后端入口
│   ├── algorithms/       # 特征工程与推荐算法
│   ├── crawler/          # 手机数据爬虫
│   ├── data/             # 样本数据与数据库脚本
│   ├── static/           # 前端页面
│   └── tests/            # 测试用例
├── docs/                 # 学习路线与需求拆解
├── .venv/                # 本地虚拟环境，不提交到 Git
├── .gitignore
├── requirements.txt
└── README.md
```

## 快速启动

```powershell
.\.venv\Scripts\python.exe code\app.py
```

浏览器访问：<http://127.0.0.1:5000>

运行测试：

```powershell
Set-Location code
..\.venv\Scripts\python.exe -m pytest -q
Set-Location ..
```

## 当前已实现

- 健康检查接口：`GET /api/health`
- 手机列表接口：`GET /api/phones`
- 手机详情接口：`GET /api/phones/<id>`
- 简单推荐接口：`GET /api/recommendations`
- 10 款手机样本数据
- 基础前端页面
- 6 个阶段 1 接口测试
- 中关村在线手机爬虫：1845 条列表，1000 条已补全参数

## Git 版本管理

项目已经按“代码 / 文档 / 环境”分目录管理。详细的 Git 命令和提交规范见 [docs/03-Git使用说明.md](docs/03-Git使用说明.md)。

## 下一步

进入阶段 2：设计数据库和数据层，把写死在代码里的手机数据改成可持久化存储。

## 数据采集

爬虫位于 `code/crawler/zol_spider.py`，数据文件：

- `code/data/zol_phone_list.json`：1845 条手机列表
- `code/data/phones_raw.json`：1000 条手机参数数据

重新抓取列表：

```powershell
Set-Location code
..\.venv\Scripts\python.exe crawler\zol_spider.py list --max-pages 5 --brands 613,1795,1673,544,98,50840,55075,34645,35579,1434,55535,35005,55731,295,642
Set-Location ..
```
