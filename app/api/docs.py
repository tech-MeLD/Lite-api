from app.schemas.common import ErrorResponse

UNAUTHORIZED_RESPONSE = {
    "model": ErrorResponse,
    "description": "Missing or invalid API key",
    "content": {
        "application/json": {
            "example": {
                "code": "INVALID_API_KEY",
                "message": "Invalid or missing API key",
                "details": None,
                "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58",
            }
        }
    },
}

VALIDATION_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": [
                    {
                        "loc": ["query", "owner"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ],
                "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58",
            }
        }
    },
}

UPSTREAM_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Upstream service request failed",
    "content": {
        "application/json": {
            "example": {
                "code": "UPSTREAM_SERVICE_ERROR",
                "message": "GitHub API request failed",
                "details": {
                    "service": "GitHub API",
                    "detail": "rate limit exceeded",
                },
                "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58",
            }
        }
    },
}

DEPENDENCY_UNHEALTHY_RESPONSE = {
    "description": "One or more dependencies are unhealthy",
    "content": {
        "application/json": {
            "example": {
                "message": "Dependency health check completed",
                "data": {
                    "status": "degraded",
                    "services": {
                        "redis": {"status": "error", "detail": "Connection refused"},
                        "sqlite": {"status": "ok", "detail": None},
                    },
                },
            }
        }
    },
}
