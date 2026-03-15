from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Building, Organization
from app.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    def _organizations_loader(self):
        return (
            selectinload(self.model.organizations).selectinload(Organization.phones),
            selectinload(self.model.organizations).selectinload(Organization.activities),
        )

    def list_within_radius_with_organizations(
        self,
        db: Session,
        *,
        latitude: float,
        longitude: float,
        radius_m: float,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Building]:
        point_geography = cast(
            func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
            self.model.location.type,
        )
        stmt = (
            select(self.model)
            .options(*self._organizations_loader())
            .where(func.ST_DWithin(self.model.location, point_geography, radius_m))
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def list_within_bbox_with_organizations(
        self,
        db: Session,
        *,
        min_latitude: float,
        min_longitude: float,
        max_latitude: float,
        max_longitude: float,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Building]:
        stmt = (
            select(self.model)
            .options(*self._organizations_loader())
            .where(self.model.latitude >= min_latitude)
            .where(self.model.latitude <= max_latitude)
            .where(self.model.longitude >= min_longitude)
            .where(self.model.longitude <= max_longitude)
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


building_repository = BuildingRepository(Building)
