from fastapi import APIRouter

from app.api.endpoints.v1.organizations import router as organizations_router

router = APIRouter()
router.include_router(organizations_router)
