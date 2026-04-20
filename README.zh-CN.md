<div align="center">

# MCC-GCN

### 基于图卷积网络的多组分晶体（共晶）预测平台

*Multi-Component Crystal prediction with Graph Convolutional Network*

一个面向药物共晶研究的全栈式 AI 平台：从单分子对预测、批量虚拟筛选，到模型微调与版本管理，提供端到端的 Web 化解决方案。

[English](./README.md) · [简体中文](./README.zh-CN.md)

[![CI](https://img.shields.io/badge/CI-passing-success?style=flat-square&logo=githubactions&logoColor=white)](./.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](#-许可证)

</div>

---

## 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [技术栈](#-技术栈)
- [系统架构](#-系统架构)
- [项目结构](#-项目结构)
- [快速开始（Docker 一键部署）](#-快速开始docker-一键部署)
- [本地开发](#-本地开发)
- [环境变量](#-环境变量)
- [API 一览](#-api-一览)
- [数据格式说明](#-数据格式说明)
- [模型说明](#-模型说明)
- [常用运维命令](#-常用运维命令)
- [国际化与 UI](#-国际化与-ui)
- [CI / CD](#-ci--cd)
- [常见问题](#-常见问题)
- [许可证](#-许可证)

---

## 项目简介

**MCC-GCN** 是一个面向药物共晶（Cocrystal）筛选与多组分晶体研究的现代化 Web 平台。它将 **图卷积网络（GCN）** 推理服务、**异步任务编排**、**模型管理与微调** 以及一套精心打磨的 **Vue 3 用户界面** 整合在一起，让研究者能够：

- 输入两个分子的 SMILES，**秒级获得共晶可能性预测**；
- 上传大批量分子对，**进行虚拟筛选**，结果异步推送；
- 上传自有数据集，**一键微调** 出领域专属模型；
- 像管理 SaaS 一样管理自己的模型版本，并在团队内发布共享。

模型基于在 CSD 剑桥晶体结构数据库上预训练的 GCN 架构，可对分子对进行 **4 分类**：

| 标签 | 含义 |
| --- | --- |
| `Negative` | 不形成多组分晶体 |
| `Salt` | 形成盐 |
| `Cocrystal` | 形成共晶 |
| `Solvate` | 形成溶剂化物 |

---

## 核心特性

### AI 推理与训练
- **单次预测**：输入 API + Coformer SMILES，自动双向推理求平均，输出 4 分类概率；
- **批量筛选**：基于 Celery + Redis 的后台任务队列，支持成千上万条分子对异步处理；
- **在线微调**：上传 CSV 训练集即可对预训练模型进行迁移学习，可配置 epoch / batch / lr；
- **自动权重管理**：以 `val_balanced_accuracy` 为指标自动保存最佳权重；
- **模型缓存**：推理服务带线程安全的模型缓存，避免重复加载。

### 模型管理
- **内置模型**：CSD 预训练模型 + 已微调模型，开箱即用；
- **用户模型**：支持上传自定义 `.pth` 权重，支持发布 / 私有；
- **可见性控制**：用户只能看到自己的模型 + 内置模型 + 已发布模型。

### 工程化
- **Docker Compose 一键部署**：5 个服务（Postgres / Redis / Backend / Celery / Frontend / Nginx）；
- **Nginx 反向代理**：统一前后端入口，规范 `/api`、`/admin`、`/static`、`/media` 路由；
- **Token 鉴权 + 路由守卫**：前端 Pinia 状态管理 + Axios 拦截器自动续期；
- **国际化**：内置中文 / English 双语，运行时一键切换；
- **现代化 UI**：基于 Element Plus，深色侧边栏 + 卡片式布局，配色与交互精心打磨；
- **CI 自动化**：GitHub Actions 同时跑后端 lint / migrate、前端 build、镜像构建。

---

## 技术栈

<table>
<tr>
<td valign="top" width="50%">

#### 后端
- **Django 6** + **Django REST Framework**
- **Celery 5** + **Redis 7** 任务队列
- **PostgreSQL 16** 关系型数据库
- **Gunicorn** WSGI 服务器
- **PyTorch (CPU)** + **PyTorch Geometric**
- **RDKit** 分子图特征化
- **NumPy / SciPy / scikit-learn**

</td>
<td valign="top" width="50%">

#### 前端
- **Vue 3** + **Vite 8** + ESM
- **Element Plus** 组件库
- **Pinia** 状态管理
- **Vue Router 4** + **vue-i18n 11**
- **Axios** HTTP 客户端

#### 基础设施
- **Docker Compose** 编排
- **Nginx (Alpine)** 反向代理
- **GitHub Actions** CI 流水线

</td>
</tr>
</table>

---

## 系统架构

```
                      ┌────────────────────────────┐
                      │         Browser            │
                      └──────────────┬─────────────┘
                                     │  HTTP :8880
                                     ▼
                      ┌────────────────────────────┐
                      │         Nginx (80)         │
                      │  / → frontend  /api → api  │
                      └──────┬──────────────┬──────┘
                             │              │
                ┌────────────▼──┐      ┌────▼─────────────┐
                │ Frontend (SPA)│      │  Backend (Django) │
                │   Vue 3 +     │      │   DRF + Gunicorn  │
                │ Element Plus  │      │   :8000           │
                └───────────────┘      └─────┬─────┬───────┘
                                             │     │
                                  ┌──────────┘     └──────────┐
                                  ▼                            ▼
                          ┌──────────────┐            ┌────────────────┐
                          │  PostgreSQL  │            │  Redis (Broker)│
                          │     :5432    │            │     :6379      │
                          └──────────────┘            └────────┬───────┘
                                                               │
                                                               ▼
                                                      ┌────────────────┐
                                                      │ Celery Worker  │
                                                      │  PyTorch + RDKit│
                                                      └────────────────┘
```

---

## 项目结构

```
MCC-GCN-App/
├── backend/                    # Django + Celery 后端
│   ├── config/                 # Django 配置（settings / urls / wsgi / celery）
│   ├── users/                  # 用户与认证（自定义 User，Token 登录）
│   ├── ml_models/              # 模型管理（MLModel CRUD / publish / 内置模型）
│   │   └── management/commands/seed_builtin_model.py
│   ├── tasks/                  # 预测 / 批量 / 微调任务
│   │   ├── celery_tasks.py     # Celery 任务定义
│   │   └── services/           # 推理与训练服务（predict.py / finetune.py）
│   ├── mcc_gcn/                # 核心算法库
│   │   ├── models/             # GCN 网络结构 + 评估指标
│   │   └── featurize/          # RDKit 分子图特征化
│   ├── fixtures/               # 内置预训练 / 微调权重 (.pth)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 7 个页面：Predict / Batch / Finetune / History / Models / Login / Register
│   │   ├── api/                # Axios 实例与各模块 API
│   │   ├── stores/             # Pinia stores
│   │   ├── router/             # 路由 + 鉴权守卫
│   │   ├── i18n/               # 中英文翻译
│   │   └── App.vue             # 现代化侧边栏布局
│   ├── nginx.conf              # 前端容器 Nginx（SPA history 模式）
│   ├── vite.config.js
│   └── Dockerfile              # 多阶段构建（node build → nginx serve）
├── nginx/
│   └── nginx.conf              # 前置反向代理（统一入口 :80）
├── .github/workflows/ci.yml    # CI：lint / migrate / build / docker
├── docker-compose.yml          # 一键编排
├── .env.example                # 环境变量模板
└── README.md
```

---

## 快速开始（Docker 一键部署）

> 适用：服务器交付、客户演示、生产部署。
> 仅需 Docker 与 Docker Compose v2，无需安装 Python / Node / PyTorch。

#### 1. 克隆并准备环境变量

```bash
git clone https://github.com/<your-org>/MCC-GCN-App.git
cd MCC-GCN-App
cp .env.example .env
# 按需编辑 .env：APP_PORT、SECRET_KEY、DB_PASSWORD、CORS_ALLOWED_ORIGINS …
```

#### 2. 构建并启动

```bash
docker compose up -d --build
```

#### 3. 初始化数据库与内置模型

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_builtin_model
docker compose exec backend python manage.py createsuperuser   # 可选：创建管理员
```

#### 4. 访问

| 入口 | 地址 |
| --- | --- |
| Web 应用 | <http://localhost:8880/> |
| Django Admin | <http://localhost:8880/admin/> |
| REST API | <http://localhost:8880/api/> |

> 部署到服务器时把 `localhost` 替换为公网 IP / 域名，并通过 `.env` 中的 `APP_PORT` 修改对外端口。

---

## 本地开发

需要本地运行三个服务：Django、Celery Worker、Vite Dev Server，外加 Postgres 与 Redis（推荐用 Docker 起）。

#### 1. 启动依赖中间件

```bash
docker run -d --name mcc-pg    -p 5432:5432 \
  -e POSTGRES_DB=mcc_gcn -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  postgres:16-alpine

docker run -d --name mcc-redis -p 6379:6379 redis:7-alpine
```

#### 2. 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install torch_geometric rdkit
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_builtin_model
python manage.py runserver 0.0.0.0:8000
```

另开一个终端启动 Celery Worker：

```bash
cd backend && source .venv/bin/activate
celery -A config worker -l info
```

#### 3. 前端

```bash
cd frontend
npm install
npm run dev          # 默认 http://localhost:5173 ，会自动代理 /api → :8000
```

---

## 环境变量

所有环境变量通过项目根目录的 `.env` 文件注入到 `docker-compose`。完整模板见 [`.env.example`](./.env.example)。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_PORT` | `8880` | Nginx 对外暴露的端口 |
| `DEBUG` | `False` | Django 调试模式（生产请关闭） |
| `SECRET_KEY` | `change-me-...` | Django 密钥，**生产务必修改** |
| `DB_NAME` | `mcc_gcn` | 数据库名 |
| `DB_USER` | `postgres` | 数据库用户名 |
| `DB_PASSWORD` | `change-me` | 数据库密码 |
| `DB_HOST` | `db` (容器内) / `localhost` (本地) | 数据库地址 |
| `DB_PORT` | `5432` | 数据库端口 |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery 消息代理 |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Celery 结果后端 |
| `CORS_ALLOWED_ORIGINS` | `http://localhost` | 允许跨域的源（逗号分隔） |
| `ALLOWED_HOSTS` | `*` | Django 允许的 Host |

---

## API 一览

所有 `/api/**` 接口（除 `register/`、`login/` 外）均需在请求头携带：

```
Authorization: Token <your-token>
```

#### 用户

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/users/register/` | 注册 |
| `POST` | `/api/users/login/` | 登录，返回 `token` |
| `POST` | `/api/users/logout/` | 登出 |
| `GET` | `/api/users/me/` | 当前用户信息 |

#### 模型

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/models/` | 列出模型（自有 + 内置 + 已发布） |
| `POST` | `/api/models/` | 上传新模型（`multipart/form-data`） |
| `DELETE` | `/api/models/{id}/` | 删除（内置模型不可删） |
| `POST` | `/api/models/{id}/publish/` | 发布模型 |

#### 任务

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/tasks/predict/` | 单次预测（同步返回结果） |
| `POST` | `/api/tasks/batch/` | 批量预测（异步，返回 `task_id`） |
| `POST` | `/api/tasks/finetune/` | 提交微调任务（异步） |
| `GET` | `/api/tasks/` | 我的预测历史，可用 `?type=single|batch` 过滤 |
| `GET` | `/api/tasks/{id}/` | 预测任务详情 |
| `GET` | `/api/tasks/finetune/list/` | 我的微调任务列表 |
| `GET` | `/api/tasks/finetune/{id}/` | 微调任务详情（含训练日志） |

---

## 数据格式说明

#### 单次预测请求

```json
POST /api/tasks/predict/
{
  "model_id": 1,
  "api_smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "coformer_smiles": "OC(=O)C=Cc1ccc(O)cc1"
}
```

返回：

```json
{
  "task": { "...": "PredictionTask 对象" },
  "result": {
    "prediction": 2,
    "label": "Cocrystal",
    "probabilities": [0.0421, 0.0337, 0.8915, 0.0327],
    "api_smiles": "...",
    "coformer_smiles": "..."
  }
}
```

#### 批量预测请求

```json
POST /api/tasks/batch/
{
  "model_id": 1,
  "pairs": [
    { "api_smiles": "...", "coformer_smiles": "..." },
    { "api_smiles": "...", "coformer_smiles": "..." }
  ]
}
```

#### 微调训练 CSV 格式

```csv
api_smiles,coformer_smiles,label
CC(=O)Oc1ccccc1C(=O)O,OC(=O)C=Cc1ccc(O)cc1,2
...
```

`label` 取值：`0=Negative, 1=Salt, 2=Cocrystal, 3=Solvate`

---

## 模型说明

#### 网络结构（`backend/mcc_gcn/models/gcn.py`）

3 层 `GCNConv` + BatchNorm + 全局平均池化 + 2 层 MLP：

```
input(34) → GCNConv→256 → GCNConv→256 → GCNConv→128
          → global_mean_pool → FC(128) → FC(64) → FC(num_classes)
```

#### 双向推理

由于分子对 `(A, B)` 与 `(B, A)` 在图结构上不严格对称，推理时对两种顺序分别求 softmax 后取平均，提升预测稳定性。

#### 微调策略

支持只解冻最后 N 层稠密层（`train_layers ∈ {1, 2, 3, all}`），降低小样本场景下的过拟合风险。优化器为 Adam + ReduceLROnPlateau，损失为带类别权重的交叉熵。

#### 内置模型

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `MCC-GCN Pretrained v1` | `pretrained` | CSD 预训练基座，适合作为微调起点 |
| `MCC-GCN v1` | `finetuned` | 经过领域微调的最终模型，开箱可用 |

---

## 常用运维命令

```bash
# 查看服务状态
docker compose ps

# 实时日志
docker compose logs -f backend
docker compose logs -f celery

# 进入容器排错
docker compose exec backend bash

# 重启某个服务
docker compose restart backend

# 数据迁移 / 创建超级用户 / 重新初始化内置模型
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_builtin_model

# 备份数据库
docker compose exec db pg_dump -U postgres mcc_gcn > backup_$(date +%F).sql

# 清理停止
docker compose down              # 保留数据
docker compose down -v           # 同时删除数据卷（慎用）
```

#### 忘记管理员密码？

```bash
# 列出所有用户（顺便看谁是 superuser）
docker compose exec backend python manage.py shell -c \
  "from users.models import User; [print(u.username, u.is_superuser) for u in User.objects.all()]"

# 已知用户名时直接重置密码
docker compose exec backend python manage.py changepassword <username>

# 或者直接新建一个超级管理员
docker compose exec backend python manage.py createsuperuser
```

---

## 国际化与 UI

- 内置 **中文 / English** 双语，所有页面文本走 `vue-i18n`，运行时一键切换；
- 翻译文件位于 [`frontend/src/i18n/`](./frontend/src/i18n)，新增语言只需添加一份 `xx.js`；
- UI 设计语言：**深色侧边栏 + 浅色主内容区 + 卡片式信息层级**，配色基于 Tailwind Slate / Blue 调色盘；
- 组件库：**Element Plus**，全局微调了 `border-radius` / `shadow` / 表头样式，更贴近 SaaS 产品观感。

---

## CI / CD

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) 提供三段流水线：

1. **backend** — `ruff` 静态检查 + Django `check` & `migrate`（基于 SQLite 内存库快速验证）；
2. **frontend** — `npm ci` + `npm run build`；
3. **docker** — 分别构建后端与前端镜像，确保 `Dockerfile` 始终可用。

---

## 常见问题

<details>
<summary><b>1. 部署后访问 8880 端口空白？</b></summary>

检查 `docker compose ps` 中 `nginx`、`frontend`、`backend` 是否都为 `running`；
然后 `docker compose logs -f frontend` 查看是否有构建失败。

</details>

<details>
<summary><b>2. /admin 页面能打开但样式全部丢失？</b></summary>

本项目已使用 **WhiteNoise** 在生产环境下为 Django 静态文件提供服务，admin 样式应当开箱可用。如果你是从旧版升级上来，请重建后端镜像：

```bash
docker compose build --no-cache backend
docker compose up -d backend
```

</details>

<details>
<summary><b>3. RDKit / PyG 安装慢或失败？</b></summary>

后端镜像在 `Dockerfile` 中已固定使用官方 CPU 版 PyTorch wheel + `torch_geometric` + `rdkit`。本地开发若安装失败，可参考 Dockerfile 顺序，或直接使用 Docker 部署。

</details>

<details>
<summary><b>4. 批量任务一直 pending？</b></summary>

确认 Celery Worker 已启动：`docker compose logs -f celery`；
确认 Redis 可达：`docker compose exec redis redis-cli ping` 应返回 `PONG`。

</details>

<details>
<summary><b>5. 想换默认端口？</b></summary>

修改根目录 `.env` 中 `APP_PORT=xxxx`，然后 `docker compose up -d` 重新创建即可。

</details>

<details>
<summary><b>6. 如何上传自己的预训练权重？</b></summary>

进入「模型管理」页面 → 上传 `.pth` 文件 → 选择 `num_classes`（默认 4）。也可直接通过 `POST /api/models/` 接口上传。

</details>

---

## 许可证

本项目采用 **MIT License** 发布。详见 [`LICENSE`](./LICENSE)。

---

<div align="center">

**MCC-GCN** · Built with Django, Vue 3 & PyTorch Geometric

如果这个项目对你有帮助，欢迎 Star 支持

</div>
