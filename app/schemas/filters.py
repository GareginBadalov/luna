from pydantic import BaseModel, Field, model_validator


class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class GeoRadiusFilter(PaginationParams):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(gt=0)


class GeoBBoxFilter(PaginationParams):
    min_latitude: float = Field(ge=-90, le=90)
    min_longitude: float = Field(ge=-180, le=180)
    max_latitude: float = Field(ge=-90, le=90)
    max_longitude: float = Field(ge=-180, le=180)

    @model_validator(mode="after")
    def validate_bbox(self) -> "GeoBBoxFilter":
        if self.min_latitude > self.max_latitude:
            raise ValueError("min_latitude must be less than or equal to max_latitude")
        if self.min_longitude > self.max_longitude:
            raise ValueError("min_longitude must be less than or equal to max_longitude")
        return self


class BuildingOrganizationsFilter(PaginationParams):
    building_id: int = Field(gt=0)


class OrganizationSearchFilter(PaginationParams):
    name: str = Field(min_length=1)


class ActivityIdOrganizationsFilter(BaseModel):
    activity_id: int = Field(gt=0)
    include_descendants: bool = False


class ActivityNameOrganizationsFilter(BaseModel):
    name: str = Field(min_length=1)
