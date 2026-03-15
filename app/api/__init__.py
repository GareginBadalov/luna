from fastapi import APIRouter, Depends

from app.api.deps import verify_api_key
from app.api.endpoints import v1_router

api_router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])
api_router.include_router(v1_router, prefix="/v1")
