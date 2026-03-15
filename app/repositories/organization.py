from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models import Organization, organization_activities
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def _base_query(self) -> Select[tuple[Organization]]:
        return select(self.model).options(
            selectinload(self.model.building),
            selectinload(self.model.phones),
            selectinload(self.model.activities),
        )

    def list_by_building(
        self, db: Session, building_id: int, *, offset: int = 0, limit: int = 100
    ) -> list[Organization]:
        stmt = self._base_query().where(self.model.building_id == building_id).offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def search_by_name(self, db: Session, name: str, *, offset: int = 0, limit: int = 100) -> list[Organization]:
        stmt = self._base_query().where(self.model.name.ilike(f"%{name}%")).offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def list_by_activity_ids(
        self,
        db: Session,
        activity_ids: list[int],
    ) -> list[Organization]:
        if not activity_ids:
            return []

        org_ids_subquery = (
            select(organization_activities.c.organization_id)
            .where(organization_activities.c.activity_id.in_(activity_ids))
            .distinct()
            .subquery()
        )

        stmt = (
            self._base_query()
            .where(self.model.id.in_(select(org_ids_subquery.c.organization_id)))
            .order_by(self.model.id)
        )
        return list(db.scalars(stmt).all())


organization_repository = OrganizationRepository(Organization)
