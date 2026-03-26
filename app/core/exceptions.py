from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class UpstreamServiceError(Exception):
    def __init__(self, service_name: str, detail: str, status_code: int = status.HTTP_502_BAD_GATEWAY) -> None:
        self.service_name = service_name
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UpstreamServiceError)
    async def upstream_service_error_handler(_: Request, exc: UpstreamServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": f"{exc.service_name} request failed",
                "data": {
                    "detail": exc.detail,
                    "service": exc.service_name,
                },
            },
        )
