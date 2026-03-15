from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Activity
from app.repositories import activity_repository, building_repository, organization_repository


def test_activity_collect_subtree_ids_with_depth_limit(db_session: Session) -> None:
    root = activity_repository.get_by_name(db_session, "Автомобили")
    assert root is not None

    ids_depth_1 = activity_repository.collect_subtree_ids(
        db_session,
        root_activity_id=root.id,
        include_descendants=True,
        max_depth=1,
    )
    ids_depth_2 = activity_repository.collect_subtree_ids(
        db_session,
        root_activity_id=root.id,
        include_descendants=True,
        max_depth=2,
    )
    assert len(ids_depth_2) >= len(ids_depth_1)

    names_depth_1 = set(db_session.scalars(select(Activity.name).where(Activity.id.in_(ids_depth_1))).all())
    names_depth_2 = set(db_session.scalars(select(Activity.name).where(Activity.id.in_(ids_depth_2))).all())
    assert "Запчасти" not in names_depth_1
    assert "Запчасти" in names_depth_2


def test_organization_list_by_activity_ids_returns_unique_orgs(db_session: Session) -> None:
    food = activity_repository.get_by_name(db_session, "Еда")
    meat = activity_repository.get_by_name(db_session, "Мясная продукция")
    assert food is not None
    assert meat is not None

    result = organization_repository.list_by_activity_ids(db_session, [food.id, meat.id])
    ids = [item.id for item in result]
    assert len(ids) == len(set(ids))


def test_building_repo_returns_buildings_with_organizations(db_session: Session) -> None:
    buildings = building_repository.list_within_radius_with_organizations(
        db_session,
        latitude=55.75,
        longitude=37.61,
        radius_m=5000,
        offset=0,
        limit=20,
    )
    assert buildings
    assert all(hasattr(building, "organizations") for building in buildings)
