# 测试文档

本文档面向 QA 和开发者，说明如何验证接口质量、自动化测试覆盖了什么、手工测试应该检查什么。

## 1. 当前自动化测试范围

当前项目已经覆盖以下内容：

- 健康检查接口
- 依赖健康检查接口
- GitHub 仓库统计接口
- 天气查询接口
- 天气历史接口
- API-Key 缺失时的鉴权失败

说明：

- 路由测试通过依赖覆写和 monkeypatch 避免真实调用上游 API
- 这是故意的，目标是让测试更稳定、更快

## 2. 自动化校验命令

推荐顺序：

```bash
make lint
make typecheck
make test
```

或一键执行：

```bash
make check
```

如果本地 Python 环境有问题，优先使用 Docker 作为统一校验环境。

## 3. 我本次完成的最终校验

在 Docker 的 Python 3.11.14 环境中已通过：

- `ruff check .`
- `mypy app`
- `pytest`

测试结果：

- `6 passed`

## 4. 手工测试建议

### 4.1 基础可用性

- 访问 `/docs` 能打开 Swagger
- 访问 `/redoc` 能打开 ReDoc
- 访问 `/api/v1/health` 返回 `200`
- 访问 `/api/v1/health/dependencies` 在依赖正常时返回 `200`

### 4.2 鉴权

- 不带 `X-API-Key` 调业务接口，应该返回 `401`
- 带错误的 `X-API-Key` 调业务接口，应该返回 `401`
- 带正确的 `X-API-Key` 调业务接口，应该返回 `200`

### 4.3 参数校验

- GitHub 接口缺少 `owner` 或 `repo`，应返回 `422`
- 天气接口纬度超范围，应返回 `422`
- 天气历史接口 `limit` 超范围，应返回 `422`

### 4.4 数据行为

- GitHub 接口首次请求后再次请求，应优先命中 Redis 缓存
- 天气接口首次请求后再次请求，应优先命中 SQLite 近期缓存
- 天气历史接口应能看到已写入的天气记录

### 4.5 错误可观测性

- 所有响应头都应含 `X-Request-ID`
- 错误响应体应含 `request_id`
- 服务日志中应能根据 `request_id` 找到对应请求

## 5. 推荐手工测试命令

### 5.1 健康检查

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/health/dependencies
```

### 5.2 鉴权成功

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi" \
  -H "X-API-Key: your-api-key"
```

### 5.3 鉴权失败

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi"
```

## 6. 缺口与后续建议

当前测试已经足够支撑这个阶段，但还可以继续演进：

- 增加 service 层单元测试
- 增加 Redis / SQLite 的集成测试
- 增加基于真实容器的端到端 smoke test
- 增加 GitHub / 天气上游失败场景测试

当前没有继续往下做，是为了避免测试体系先于业务复杂度膨胀。
