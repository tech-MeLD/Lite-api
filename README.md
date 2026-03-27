# 标准 FastAPI 后端

这是一个保持轻量、但已经具备公网 API 基本防护能力的 FastAPI 模板。

## 这次新增了什么

- 统一日志，自动生成或透传 `X-Request-ID`
- 统一 API 异常码和错误返回结构
- 简单 `X-API-Key` 鉴权
- GitHub 数据走 Redis TTL 缓存
- 天气数据使用 SQLite + SQLModel 持久化
- `pre-commit`、`ruff`、`mypy`、`pytest`
- GitHub Actions CI

## 设计原则

这套方案刻意避免过度工程化：

- 不引入 Alembic
- 不上 JWT / OAuth
- 不拆成复杂的模块层级
- 不增加消息队列或后台任务系统

目标是让团队“现在就能稳定开发”，而不是一开始就背上很重的维护成本。

## API 概览

公开接口：

- `GET /api/v1/health`
- `GET /api/v1/health/dependencies`

需要 API-Key 的接口：

- `GET /api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi`
- `GET /api/v1/external/weather?latitude=39.9042&longitude=116.4074`
- `GET /api/v1/external/weather/history?limit=20`

请求头示例：

```http
X-API-Key: your-api-key
```

所有响应也会带上：

```http
X-Request-ID: <uuid>
```

## 异常返回格式

```json
{
  "code": "INVALID_API_KEY",
  "message": "Invalid or missing API key",
  "details": null,
  "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58"
}
```

当前定义的异常码：

- `INVALID_API_KEY`
- `VALIDATION_ERROR`
- `UPSTREAM_SERVICE_ERROR`
- `HTTP_ERROR`
- `INTERNAL_SERVER_ERROR`

## 关键设计决策

### 1. Python 版本统一

团队基线固定为 `Python 3.11.14`。

同时在这些位置统一：

- `pyproject.toml`
- `.python-version`
- `Dockerfile`
- GitHub Actions

Python 版本不应该只写在依赖里，而是要在包元数据、本地工具链、CI、容器运行时一起固定。

### 2. GitHub 数据

GitHub 数据暂时不落库，只通过 Redis 做 TTL 缓存，减少外部 API 请求次数，也能降低被盗刷后的放大效应。

### 3. 天气数据

天气数据会落到 SQLite，通过 SQLModel 管理。当前实现会优先复用近期缓存记录，并支持历史查询接口。

## 本地开发

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

然后根据 `.env.example` 准备 `.env`，再启动：

```bash
uvicorn app.main:app --reload
```

## Makefile

如果团队习惯统一命令入口，现在可以直接使用：

```bash
make dev
make run
make check
make docker-up
```

常用目标：

- `make dev`：安装项目和开发依赖
- `make run`：本地热更新启动服务
- `make lint`：执行 Ruff
- `make typecheck`：执行 mypy
- `make test`：执行 pytest
- `make check`：串行执行 lint、类型检查、测试

如果你在 Windows 上使用，建议通过 Git Bash、WSL 或已安装 `make` 的终端来执行。

## Docker

```bash
docker compose up --build
```

会同时启动：

- FastAPI 服务
- Redis 缓存
- 挂载 SQLite 数据目录

## 健康检查

- `GET /api/v1/health`：基础存活检查
- `GET /api/v1/health/dependencies`：Redis 和 SQLite 依赖检查

依赖健康检查在全部正常时返回 `200`，任一依赖异常时返回 `503`。

## 代码质量工具

```bash
pre-commit install
pre-commit run --all-files
ruff check .
mypy app
pytest
```

## CI

GitHub Actions 会执行：

- `ruff check .`
- `mypy app`
- `pytest`

## 文档

- 接口文档：`docs/API.md`
- 设计文档：`docs/DESIGN.md`
- 测试文档：`docs/TESTING.md`
