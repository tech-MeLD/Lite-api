# Standard FastAPI Backend

一个适合团队协作的标准化 FastAPI RESTful API 模板，包含：

- 分层结构：`api / schemas / services / core`
- RESTful 路由与 `/api/v1` 版本控制
- 外部 API 聚合示例：GitHub 仓库统计、天气数据
- 统一配置管理与环境变量加载
- Docker 化运行环境
- Python 版本统一策略

## Why This Structure

这个模板的目标不是“先跑起来”，而是让团队后续维护成本更低：

- `pyproject.toml` 是依赖和 Python 版本范围的单一事实来源
- `.python-version` 固定本地开发使用的 Python 版本
- `Dockerfile` 固定容器内 Python 版本和系统依赖
- `.env.example` 统一环境变量约定

## Project Structure

```text
.
├─ app
│  ├─ api
│  │  ├─ routes
│  │  └─ router.py
│  ├─ core
│  ├─ schemas
│  ├─ services
│  └─ main.py
├─ tests
├─ .env.example
├─ .python-version
├─ docker-compose.yml
├─ Dockerfile
└─ pyproject.toml
```

## API Endpoints

### 1. Health Check

`GET /api/v1/health`

### 2. GitHub Repository Stats

`GET /api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi`

返回示例：

```json
{
  "message": "GitHub repository statistics fetched successfully",
  "data": {
    "owner": "fastapi",
    "repository": "fastapi",
    "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
    "stars": 0,
    "forks": 0,
    "open_issues": 0,
    "watchers": 0,
    "primary_language": "Python",
    "default_branch": "master",
    "html_url": "https://github.com/fastapi/fastapi",
    "updated_at": "2026-03-26T00:00:00+00:00"
  }
}
```

### 3. Weather Data

`GET /api/v1/external/weather?latitude=39.9042&longitude=116.4074`

## Local Development

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

### 4. Prepare Environment Variables

复制 `.env.example` 为 `.env`，然后按需修改：

```env
APP_ENV=development
DEBUG=true
REQUEST_TIMEOUT_SECONDS=10
GITHUB_API_BASE_URL=https://api.github.com
WEATHER_API_BASE_URL=https://api.open-meteo.com/v1
```

### 5. Run the Service

```bash
uvicorn app.main:app --reload
```

启动后访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Docker

### Build and Run

```bash
docker compose up --build
```

## Testing

```bash
pytest
```

## Team Standardization Recommendations

### 1. Python Version Should Not Be Managed Only in Dependencies

Python 版本不建议只写在依赖列表里。标准做法是同时固定在以下几个位置：

- `pyproject.toml` 中的 `requires-python`
- `.python-version`
- `Dockerfile` 的基础镜像
- CI 配置中的 Python 版本

这样可以同时约束：

- 包安装时的可用版本范围
- 本地开发工具选用的解释器版本
- 容器运行时的真实版本
- 持续集成环境的一致性

### 2. Recommended Team Workflow

- 本地开发统一使用 `Python 3.11.14`
- 所有人通过 `pyproject.toml` 安装依赖，不手写零散 `requirements.txt`
- 生产和测试环境优先通过 Docker 运行
- 后续如果接入 CI，继续固定 `3.11.14`

### 3. When to Add requirements.txt

如果你的部署平台或某些内部工具仍然强依赖 `requirements.txt`，可以从 `pyproject.toml` 派生生成一个锁定文件；但在这个模板里，建议 `pyproject.toml` 作为主入口，避免维护两份手工依赖清单。

## Notes

- GitHub API 可能受到速率限制，生产环境建议加认证令牌或缓存
- 天气接口当前使用 Open-Meteo 公共接口，便于快速演示和联调
- 如果后续需要数据库、认证、日志、链路追踪，可以继续在当前结构上扩展
