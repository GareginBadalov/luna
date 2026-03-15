from pydantic import BaseModel

from app.schemas.building import BuildingRead
from app.schemas.organization import OrganizationRead


class GeoSearchResult(BaseModel):
    organizations: list[OrganizationRead]
    buildings: list[BuildingRead]
