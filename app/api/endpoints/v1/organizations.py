from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import (
    activity_repository,
    building_repository,
    organization_repository,
)
from app.schemas import (
    ActivityIdOrganizationsFilter,
    ActivityNameOrganizationsFilter,
    BuildingOrganizationsFilter,
    GeoBBoxFilter,
    GeoRadiusFilter,
    GeoSearchResult,
    OrganizationRead,
    OrganizationSearchFilter,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "/by-building",
    response_model=list[OrganizationRead],
    summary="Список организаций по зданию",
    description=(
        "Возвращает список организаций, привязанных к конкретному зданию.\n\n"
        "Body: `id здания`, `смещение`, `лимит`.\n"
        "Response: массив объектов `OrganizationRead`."
    ),
    response_description="Список организаций в указанном здании.",
)
def list_organizations_by_building(
    payload: BuildingOrganizationsFilter,
    db: Session = Depends(get_db),
) -> list[OrganizationRead]:
    return organization_repository.list_by_building(
        db,
        payload.building_id,
        offset=payload.offset,
        limit=payload.limit,
    )


@router.post(
    "/search",
    response_model=list[OrganizationRead],
    summary="Поиск организаций по названию",
    description=(
        "Ищет организации по части названия (регистронезависимый поиск).\n\n"
        "Body: `Название организации`, `смещение`, `лимит`.\n"
        "Response: массив объектов `OrganizationRead`."
    ),
    response_description="Список найденных организаций.",
)
def search_organizations_by_name(
    payload: OrganizationSearchFilter,
    db: Session = Depends(get_db),
) -> list[OrganizationRead]:
    return organization_repository.search_by_name(db, name=payload.name, offset=payload.offset, limit=payload.limit)


@router.post(
    "/geo/radius",
    response_model=GeoSearchResult,
    summary="Организации и здания в радиусе",
    description=(
        "Возвращает два списка в одном ответе: здания и организации внутри заданного радиуса от точки.\n\n"
        "Body: `Широта`, `Долгота`, `Радиус в метрах` `Смещение`, `Лимит`.\n"
        "Response: объект `GeoSearchResult` с полями `organizations` и `buildings`."
    ),
    response_description="Организации и здания в заданном радиусе.",
)
def list_organizations_and_buildings_within_radius(
    payload: GeoRadiusFilter,
    db: Session = Depends(get_db),
) -> GeoSearchResult:
    buildings = building_repository.list_within_radius_with_organizations(
        db,
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_m=payload.radius_m,
        offset=payload.offset,
        limit=payload.limit,
    )
    organizations = [organization for building in buildings for organization in building.organizations]
    return GeoSearchResult(organizations=organizations, buildings=buildings)


@router.post(
    "/geo/bbox",
    response_model=GeoSearchResult,
    summary="Организации и здания в прямоугольной области",
    description=(
        "Возвращает два списка в одном ответе: здания и организации внутри прямоугольной области (bbox).\n\n"
        "Body: `Мин широта`, `Мин долгота`, `Макс широта`, `Макс долгота`, `смещение`, `лимит`.\n"
        "Response: объект `GeoSearchResult` с полями `organizations` и `buildings`."
    ),
    response_description="Организации и здания в указанной прямоугольной области.",
)
def list_organizations_and_buildings_within_bbox(
    payload: GeoBBoxFilter,
    db: Session = Depends(get_db),
) -> GeoSearchResult:
    buildings = building_repository.list_within_bbox_with_organizations(
        db,
        min_latitude=payload.min_latitude,
        min_longitude=payload.min_longitude,
        max_latitude=payload.max_latitude,
        max_longitude=payload.max_longitude,
        offset=payload.offset,
        limit=payload.limit,
    )
    organizations = [organization for building in buildings for organization in building.organizations]
    return GeoSearchResult(organizations=organizations, buildings=buildings)


@router.post(
    "/by-activity-id",
    response_model=list[OrganizationRead],
    summary="Список организаций по идентификатору деятельности",
    description=(
        "Ищет организации, связанные с указанной деятельностью.\n\n"
        "Body: `id Деятельности`, `Флаг включения потомков в поиск`.\n"
        "Если `include_descendants=true`, в поиск включаются дочерние деятельности.\n"
        "Response: массив объектов `OrganizationRead`."
    ),
    response_description="Список организаций по виду деятельности.",
)
def list_organizations_by_activity_id(
    payload: ActivityIdOrganizationsFilter,
    db: Session = Depends(get_db),
) -> list[OrganizationRead]:
    activity = activity_repository.get(db, payload.activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found.")

    activity_ids = activity_repository.collect_subtree_ids(
        db,
        root_activity_id=payload.activity_id,
        include_descendants=payload.include_descendants,
    )
    return organization_repository.list_by_activity_ids(db, activity_ids)


@router.post(
    "/by-activity-name",
    response_model=list[OrganizationRead],
    summary="Список организаций по названию деятельности",
    description=(
        "Ищет организации по названию деятельности и ее дочерним узлам дерева.\n\n"
        "Body: `Название деятельности`.\n"
        "Поиск по дереву ограничен глубиной 3.\n"
        "Response: массив объектов `OrganizationRead`."
    ),
    response_description="Список организаций по названию деятельности и потомкам.",
)
def list_organizations_by_activity_name(
    payload: ActivityNameOrganizationsFilter,
    db: Session = Depends(get_db),
) -> list[OrganizationRead]:
    activity = activity_repository.get_by_name(db, payload.name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found.")

    activity_ids = activity_repository.collect_subtree_ids(
        db,
        root_activity_id=activity.id,
        include_descendants=True,
        max_depth=2,
    )
    return organization_repository.list_by_activity_ids(db, activity_ids)


@router.get(
    "/{organization_id}",
    response_model=OrganizationRead,
    summary="Карточка организации по идентификатору",
    description=(
        "Возвращает полную карточку организации: здание, телефоны и деятельности.\n\n"
        "Path-param: `organization_id`.\n"
        "Response: объект `OrganizationRead`."
    ),
    response_description="Карточка организации.",
)
def get_organization_by_id(
    organization_id: int,
    db: Session = Depends(get_db),
) -> OrganizationRead:
    organization = organization_repository.get(db, organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return organization
