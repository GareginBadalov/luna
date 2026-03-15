from sqlalchemy import func, literal, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def get_by_name(self, db: Session, name: str) -> Activity | None:
        stmt = select(self.model).where(
            or_(
                self.model.name == name,
                func.lower(self.model.name) == name.lower(),
            )
        )
        return db.scalar(stmt)

    def collect_subtree_ids(
        self,
        db: Session,
        *,
        root_activity_id: int,
        include_descendants: bool,
        max_depth: int | None = None,
    ) -> list[int]:
        if not include_descendants:
            return [root_activity_id]

        activity_tree = select(
            self.model.id.label("id"),
            literal(0).label("depth"),
        ).where(self.model.id == root_activity_id)
        cte = activity_tree.cte(name="activity_tree", recursive=True)
        child = aliased(self.model)

        recursive_part = select(
            child.id.label("id"),
            (cte.c.depth + 1).label("depth"),
        ).where(child.parent_id == cte.c.id)

        if max_depth is not None:
            recursive_part = recursive_part.where(cte.c.depth < max_depth)

        cte = cte.union_all(recursive_part)
        stmt = select(cte.c.id).distinct()
        return list(db.scalars(stmt).all())


activity_repository = ActivityRepository(Activity)
