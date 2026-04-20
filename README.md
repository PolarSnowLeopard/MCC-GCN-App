<div align="center">

# MCC-GCN

### A Web Platform for Multi-Component Crystal Prediction with Graph Convolutional Networks

A full-stack AI platform for cocrystal research — from single-pair prediction and high-throughput virtual screening, to model fine-tuning and version management, all delivered through a polished web UI.

[English](./README.md) · [简体中文](./README.zh-CN.md)

[![CI](https://img.shields.io/badge/CI-passing-success?style=flat-square&logo=githubactions&logoColor=white)](./.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](#-license)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Highlights](#-highlights)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Layout](#-project-layout)
- [Quick Start (Docker)](#-quick-start-docker)
- [Local Development](#-local-development)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Data Formats](#-data-formats)
- [Model Details](#-model-details)
- [Operations Cheatsheet](#-operations-cheatsheet)
- [Internationalization & UI](#-internationalization--ui)
- [CI / CD](#-ci--cd)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## Overview

**MCC-GCN** is a modern web platform for **cocrystal screening** and **multi-component crystal research**. It bundles a **Graph Convolutional Network (GCN)** inference service, an **asynchronous task pipeline**, **model management & fine-tuning**, and a carefully crafted **Vue 3 user interface** into a single deployable application. Researchers can:

- Submit two SMILES strings and **get cocrystal predictions in seconds**;
- Upload large molecule-pair libraries for **asynchronous virtual screening**;
- Bring their own datasets and **fine-tune domain-specific models** in a few clicks;
- Manage model versions and publish them to teammates, just like a SaaS product.

The model is a GCN pretrained on the Cambridge Structural Database (CSD), producing a **4-class** prediction over each molecule pair:

| Label | Meaning |
| --- | --- |
| `Negative` | No multi-component crystal forms |
| `Salt` | Forms a salt |
| `Cocrystal` | Forms a cocrystal |
| `Solvate` | Forms a solvate |

---

## Highlights

### AI Inference & Training
- **Single prediction** — feed API + Coformer SMILES, run bidirectional inference, return averaged class probabilities;
- **Batch screening** — Celery + Redis powered queue for thousands of pairs;
- **Online fine-tuning** — upload a CSV and transfer-learn from the pretrained backbone with configurable epochs / batch size / learning rate;
- **Best-checkpoint persistence** — automatically saves the weights with the best validation balanced accuracy;
- **Thread-safe model cache** — avoids repeated weight loading at runtime.

### Model Management
- **Built-in models** — CSD-pretrained backbone + a fine-tuned production model, ready out of the box;
- **User models** — upload custom `.pth` weights, keep them private or publish to the team;
- **Visibility rules** — every user sees their own models + built-in models + all published models.

### Engineering
- **One-command Docker deploy** — Postgres / Redis / Backend / Celery / Frontend / Nginx orchestrated via `docker compose`;
- **Unified Nginx gateway** — clean routing for `/`, `/api`, `/admin`, `/static`, `/media`;
- **Token auth + route guard** — Pinia state + Axios interceptors handle authentication transparently;
- **i18n** — built-in English / 简体中文, switchable at runtime;
- **Modern UI** — Element Plus with a custom dark sidebar, card-based layout, and refined typography;
- **CI pipeline** — GitHub Actions runs backend lint / migrate, frontend build, and Docker image builds on every push.

---

## Tech Stack

<table>
<tr>
<td valign="top" width="50%">

#### Backend
- **Django 6** + **Django REST Framework**
- **Celery 5** + **Redis 7** task queue
- **PostgreSQL 16** relational database
- **Gunicorn** + **WhiteNoise**
- **PyTorch (CPU)** + **PyTorch Geometric**
- **RDKit** for molecular featurization
- **NumPy / SciPy / scikit-learn**

</td>
<td valign="top" width="50%">

#### Frontend
- **Vue 3** + **Vite 8** (ESM)
- **Element Plus** component library
- **Pinia** state management
- **Vue Router 4** + **vue-i18n 11**
- **Axios** HTTP client

#### Infrastructure
- **Docker Compose** orchestration
- **Nginx (Alpine)** reverse proxy
- **GitHub Actions** CI

</td>
</tr>
</table>

---

## Architecture

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
                                                      │ PyTorch + RDKit│
                                                      └────────────────┘
```

---

## Project Layout

```
MCC-GCN-App/
├── backend/                    # Django + Celery backend
│   ├── config/                 # Django settings / urls / wsgi / celery
│   ├── users/                  # Custom user model + Token auth
│   ├── ml_models/              # MLModel CRUD / publish / built-in seeding
│   │   └── management/commands/seed_builtin_model.py
│   ├── tasks/                  # Predict / batch / fine-tune endpoints
│   │   ├── celery_tasks.py     # Celery task definitions
│   │   └── services/           # Inference & training services
│   ├── mcc_gcn/                # Core algorithm package
│   │   ├── models/             # GCN architecture + metrics
│   │   └── featurize/          # RDKit-based graph featurization
│   ├── fixtures/               # Built-in pretrained / fine-tuned weights
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── views/              # 7 pages: Predict / Batch / Finetune / History / Models / Login / Register
│   │   ├── api/                # Axios instance & module APIs
│   │   ├── stores/             # Pinia stores
│   │   ├── router/             # Routes + auth guard
│   │   ├── i18n/               # English / Chinese translations
│   │   └── App.vue             # Modern sidebar layout
│   ├── nginx.conf              # SPA history-mode Nginx (in-container)
│   ├── vite.config.js
│   └── Dockerfile              # Multi-stage: node build → nginx serve
├── nginx/
│   └── nginx.conf              # Front-facing reverse proxy (entry point :80)
├── .github/workflows/ci.yml    # CI: lint / migrate / build / docker
├── docker-compose.yml          # One-shot orchestration
├── .env.example                # Env template
└── README.md
```

---

## Quick Start (Docker)

> Best for: server delivery, customer demos, production deployment.
> Requires only Docker and Docker Compose v2 — no need to install Python / Node / PyTorch on the host.

#### 1. Clone & prepare environment

```bash
git clone https://github.com/<your-org>/MCC-GCN-App.git
cd MCC-GCN-App
cp .env.example .env
# Edit .env: APP_PORT, SECRET_KEY, DB_PASSWORD, CORS_ALLOWED_ORIGINS, ...
```

#### 2. Build & start

```bash
docker compose up -d --build
```

#### 3. Initialize the database & seed built-in models

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_builtin_model
docker compose exec backend python manage.py createsuperuser   # optional
```

#### 4. Access

| Entry | URL |
| --- | --- |
| Web app | <http://localhost:8880/> |
| Django admin | <http://localhost:8880/admin/> |
| REST API | <http://localhost:8880/api/> |

> When deploying to a server, replace `localhost` with the server IP / domain. Change the public port via `APP_PORT` in `.env`.

---

## Local Development

You'll typically run three processes locally — Django, the Celery worker, and the Vite dev server — backed by Postgres and Redis (Docker is the easiest way to get them).

#### 1. Run middleware

```bash
docker run -d --name mcc-pg    -p 5432:5432 \
  -e POSTGRES_DB=mcc_gcn -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  postgres:16-alpine

docker run -d --name mcc-redis -p 6379:6379 redis:7-alpine
```

#### 2. Backend

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

In a second terminal start the Celery worker:

```bash
cd backend && source .venv/bin/activate
celery -A config worker -l info
```

#### 3. Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173 — proxies /api to :8000
```

---

## Environment Variables

All variables are loaded from a root-level `.env` file by `docker compose`. See [`.env.example`](./.env.example) for a template.

| Variable | Default | Description |
| --- | --- | --- |
| `APP_PORT` | `8880` | Public port exposed by Nginx |
| `DEBUG` | `False` | Django debug mode (turn off in production) |
| `SECRET_KEY` | `change-me-...` | Django secret key — **must be changed in production** |
| `DB_NAME` | `mcc_gcn` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `change-me` | Database password |
| `DB_HOST` | `db` (in container) / `localhost` (local) | Database host |
| `DB_PORT` | `5432` | Database port |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Celery result backend |
| `CORS_ALLOWED_ORIGINS` | `http://localhost` | Allowed CORS origins (comma-separated) |
| `ALLOWED_HOSTS` | `*` | Django allowed hosts |

---

## API Reference

All `/api/**` endpoints (except `register/` and `login/`) require:

```
Authorization: Token <your-token>
```

#### Users

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/users/register/` | Register |
| `POST` | `/api/users/login/` | Log in, returns `token` |
| `POST` | `/api/users/logout/` | Log out |
| `GET` | `/api/users/me/` | Current user info |

#### Models

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/models/` | List models (own + built-in + published) |
| `POST` | `/api/models/` | Upload a new model (`multipart/form-data`) |
| `DELETE` | `/api/models/{id}/` | Delete (built-in models cannot be deleted) |
| `POST` | `/api/models/{id}/publish/` | Publish a model |

#### Tasks

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/tasks/predict/` | Single prediction (synchronous) |
| `POST` | `/api/tasks/batch/` | Batch prediction (async, returns `task_id`) |
| `POST` | `/api/tasks/finetune/` | Submit a fine-tuning job (async) |
| `GET` | `/api/tasks/` | My prediction history (filter via `?type=single|batch`) |
| `GET` | `/api/tasks/{id}/` | Prediction task detail |
| `GET` | `/api/tasks/finetune/list/` | My fine-tuning jobs |
| `GET` | `/api/tasks/finetune/{id}/` | Fine-tuning job detail (with training log) |

---

## Data Formats

#### Single prediction request

```json
POST /api/tasks/predict/
{
  "model_id": 1,
  "api_smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "coformer_smiles": "OC(=O)C=Cc1ccc(O)cc1"
}
```

Response:

```json
{
  "task": { "...": "PredictionTask object" },
  "result": {
    "prediction": 2,
    "label": "Cocrystal",
    "probabilities": [0.0421, 0.0337, 0.8915, 0.0327],
    "api_smiles": "...",
    "coformer_smiles": "..."
  }
}
```

#### Batch prediction request

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

#### Fine-tuning CSV format

```csv
api_smiles,coformer_smiles,label
CC(=O)Oc1ccccc1C(=O)O,OC(=O)C=Cc1ccc(O)cc1,2
...
```

`label` values: `0=Negative, 1=Salt, 2=Cocrystal, 3=Solvate`

---

## Model Details

#### Network (`backend/mcc_gcn/models/gcn.py`)

3 × `GCNConv` + BatchNorm + global mean pooling + 2 × FC head:

```
input(34) → GCNConv→256 → GCNConv→256 → GCNConv→128
          → global_mean_pool → FC(128) → FC(64) → FC(num_classes)
```

#### Bidirectional inference

Because the molecule pair `(A, B)` is not strictly graph-symmetric to `(B, A)`, inference is performed on both orderings and the softmax outputs are averaged. This noticeably stabilizes predictions.

#### Fine-tuning strategy

You can unfreeze only the last N dense layers (`train_layers ∈ {1, 2, 3, all}`) to reduce overfitting in low-data regimes. Optimizer is Adam with `ReduceLROnPlateau`, loss is class-weighted cross-entropy.

#### Built-in models

| Name | Type | Notes |
| --- | --- | --- |
| `MCC-GCN Pretrained v1` | `pretrained` | CSD-pretrained backbone, ideal as a fine-tuning starting point |
| `MCC-GCN v1` | `finetuned` | Domain-fine-tuned production model, ready to use |

---

## Operations Cheatsheet

```bash
# Service status
docker compose ps

# Tail logs
docker compose logs -f backend
docker compose logs -f celery

# Shell into a container
docker compose exec backend bash

# Restart a service
docker compose restart backend

# Migrations / superuser / re-seed built-in models
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_builtin_model

# Database backup
docker compose exec db pg_dump -U postgres mcc_gcn > backup_$(date +%F).sql

# Stop
docker compose down              # keep data
docker compose down -v           # also drop volumes (DESTRUCTIVE)
```

#### Forgot the admin password?

```bash
# List all users (and which ones are superusers)
docker compose exec backend python manage.py shell -c \
  "from users.models import User; [print(u.username, u.is_superuser) for u in User.objects.all()]"

# Reset password for a known username
docker compose exec backend python manage.py changepassword <username>

# Or just create a new superuser
docker compose exec backend python manage.py createsuperuser
```

---

## Internationalization & UI

- Built-in **English / 简体中文**, all UI text goes through `vue-i18n`, switchable at runtime;
- Translation files live under [`frontend/src/i18n/`](./frontend/src/i18n) — add a new `xx.js` to support another language;
- Design language: **dark sidebar + light content area + card-based information hierarchy**, palette inspired by Tailwind Slate / Blue;
- Component library: **Element Plus**, with global tweaks to `border-radius`, `shadow`, and table headers for a more SaaS-like feel.

---

## CI / CD

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) runs three jobs:

1. **backend** — `ruff` lint + Django `check` & `migrate` (against an in-memory SQLite for speed);
2. **frontend** — `npm ci` + `npm run build`;
3. **docker** — builds backend and frontend images to make sure the `Dockerfile`s are always green.

---

## Troubleshooting

<details>
<summary><b>1. The page is blank after deploying on port 8880.</b></summary>

Check `docker compose ps` — `nginx`, `frontend`, and `backend` should all be `running`.
Then `docker compose logs -f frontend` to look for build errors.

</details>

<details>
<summary><b>2. /admin loads but has no styles.</b></summary>

This repo uses **WhiteNoise** to serve Django static files in production, so admin assets should work out of the box. If you upgraded from an older version, rebuild the backend image:

```bash
docker compose build --no-cache backend
docker compose up -d backend
```

</details>

<details>
<summary><b>3. RDKit / PyG installation is slow or fails locally.</b></summary>

The backend `Dockerfile` pins the official CPU PyTorch wheel + `torch_geometric` + `rdkit` in the right order. If local installs fail, follow the same install order, or just use the Docker setup.

</details>

<details>
<summary><b>4. Batch jobs stay in <code>pending</code> forever.</b></summary>

Make sure the Celery worker is running: `docker compose logs -f celery`.
Confirm Redis is reachable: `docker compose exec redis redis-cli ping` should return `PONG`.

</details>

<details>
<summary><b>5. How do I change the public port?</b></summary>

Edit `APP_PORT=xxxx` in `.env`, then `docker compose up -d` to recreate the Nginx container.

</details>

<details>
<summary><b>6. How do I upload my own pretrained weights?</b></summary>

Open the **Models** page → upload your `.pth` file → set `num_classes` (default 4). You can also `POST /api/models/` directly.

</details>

---

## License

Released under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

---

<div align="center">

**MCC-GCN** · Built with Django, Vue 3 & PyTorch Geometric

If this project helps your research, a star is much appreciated.

</div>
