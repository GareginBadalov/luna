from fastapi import FastAPI
import uvicorn

from app.api import api_router

app = FastAPI(title="Luna Organizations API")
app.include_router(api_router)


@app.get(
    "/health",
    tags=["health"],
    summary="Проверка доступности сервиса",
    description="Служебный endpoint для проверки, что API-сервис запущен и отвечает.",
    response_description="Статус работоспособности API.",
)
def healthcheck() -> dict[str, str]:
    """Проверка состояния приложения."""
    return {"status": "ok"}
