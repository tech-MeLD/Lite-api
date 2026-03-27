# 接口文档

本文档面向前后端调用方，说明接口如何调用、需要哪些请求头、会返回什么数据。

## 1. 基本信息

- 基础前缀：`/api/v1`
- 文档地址：
  - Swagger UI：`/docs`
  - ReDoc：`/redoc`
- 返回格式：
  - 成功：`{ "message": "...", "data": ... }`
  - 失败：`{ "code": "...", "message": "...", "details": ..., "request_id": "..." }`

## 2. 认证方式

除健康检查外，业务接口都需要在请求头带上：

```http
X-API-Key: your-api-key
```

所有响应头都会带：

```http
X-Request-ID: <uuid>
```

这个值可用于日志排查与问题追踪。

## 3. 健康检查接口

### 3.1 服务存活

- 方法：`GET`
- 路径：`/api/v1/health`
- 是否需要 API-Key：否

返回示例：

```json
{
  "message": "Service is healthy",
  "data": {
    "status": "ok"
  }
}
```

### 3.2 依赖健康检查

- 方法：`GET`
- 路径：`/api/v1/health/dependencies`
- 是否需要 API-Key：否

返回示例：

```json
{
  "message": "Dependency health check completed",
  "data": {
    "status": "ok",
    "services": {
      "redis": {
        "status": "ok",
        "detail": null
      },
      "sqlite": {
        "status": "ok",
        "detail": null
      }
    }
  }
}
```

说明：

- 全部依赖正常时返回 `200`
- 任一依赖异常时返回 `503`

## 4. GitHub 仓库统计接口

- 方法：`GET`
- 路径：`/api/v1/external/github/repo-stats`
- 是否需要 API-Key：是

查询参数：

- `owner`：GitHub 仓库所有者
- `repo`：GitHub 仓库名称

调用示例：

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi" \
  -H "X-API-Key: your-api-key"
```

成功返回示例：

```json
{
  "message": "GitHub repository statistics fetched successfully",
  "data": {
    "owner": "fastapi",
    "repository": "fastapi",
    "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
    "stars": 90000,
    "forks": 8000,
    "open_issues": 120,
    "watchers": 1500,
    "primary_language": "Python",
    "default_branch": "master",
    "html_url": "https://github.com/fastapi/fastapi",
    "updated_at": "2026-03-26T12:00:00Z"
  }
}
```

## 5. 天气查询接口

- 方法：`GET`
- 路径：`/api/v1/external/weather`
- 是否需要 API-Key：是

查询参数：

- `latitude`：纬度，范围 `-90` 到 `90`
- `longitude`：经度，范围 `-180` 到 `180`

调用示例：

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/external/weather?latitude=39.9042&longitude=116.4074" \
  -H "X-API-Key: your-api-key"
```

成功返回示例：

```json
{
  "message": "Weather data fetched successfully",
  "data": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "temperature_celsius": 22.5,
    "wind_speed_kmh": 8.1,
    "wind_direction_degrees": 180,
    "weather_code": 1,
    "observed_at": "2026-03-26T10:00:00Z"
  }
}
```

## 6. 天气历史接口

- 方法：`GET`
- 路径：`/api/v1/external/weather/history`
- 是否需要 API-Key：是

查询参数：

- `limit`：返回数量，范围 `1` 到 `100`，默认 `20`

调用示例：

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/external/weather/history?limit=20" \
  -H "X-API-Key: your-api-key"
```

成功返回示例：

```json
{
  "message": "Weather history fetched successfully",
  "data": [
    {
      "id": 1,
      "latitude": 39.9042,
      "longitude": 116.4074,
      "temperature_celsius": 22.5,
      "wind_speed_kmh": 8.1,
      "wind_direction_degrees": 180,
      "weather_code": 1,
      "observed_at": "2026-03-26T10:00:00Z",
      "fetched_at": "2026-03-26T10:05:00Z"
    }
  ]
}
```

## 7. 常见错误码

- `INVALID_API_KEY`：缺少或错误的 API-Key
- `VALIDATION_ERROR`：请求参数格式或范围不正确
- `UPSTREAM_SERVICE_ERROR`：调用 GitHub / 天气上游接口失败
- `HTTP_ERROR`：框架级 HTTP 异常
- `INTERNAL_SERVER_ERROR`：未捕获的服务端异常

错误返回示例：

```json
{
  "code": "INVALID_API_KEY",
  "message": "Invalid or missing API key",
  "details": null,
  "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58"
}
```
