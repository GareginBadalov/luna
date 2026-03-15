from dataclasses import dataclass
from pathlib import Path
import random
import sys

from geoalchemy2 import WKTElement
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.models import Activity, Building, Organization, OrganizationPhone


@dataclass(frozen=True)
class BuildingSeed:
    address: str
    latitude: float
    longitude: float


BUILDINGS: list[BuildingSeed] = [
    BuildingSeed("г. Москва, ул. Ленина, 1", 55.751244, 37.618423),
    BuildingSeed("г. Москва, ул. Тверская, 7", 55.764673, 37.605682),
    BuildingSeed("г. Москва, ул. Арбат, 12", 55.749514, 37.591123),
    BuildingSeed("г. Москва, пр-т Мира, 22", 55.781376, 37.633393),
    BuildingSeed("г. Москва, Ленинградский пр-т, 33", 55.790121, 37.544215),
    BuildingSeed("г. Москва, ул. Профсоюзная, 14", 55.677521, 37.562899),
    BuildingSeed("г. Москва, Кутузовский пр-т, 18", 55.746911, 37.539882),
    BuildingSeed("г. Москва, ул. Блюхера, 32/1", 55.773845, 37.654203),
    BuildingSeed("г. Москва, Варшавское ш., 85", 55.647923, 37.620781),
    BuildingSeed("г. Москва, ул. Новослободская, 45", 55.785822, 37.600139),
    BuildingSeed("г. Москва, ул. Лобачевского, 66", 55.671244, 37.512634),
    BuildingSeed("г. Москва, Рязанский пр-т, 27", 55.724375, 37.772116),
]

ORG_PREFIXES = [
    "ООО",
    "АО",
    "ИП",
]

ORG_NAMES = [
    "Рога и Копыта",
    "Городская Еда",
    "Молочный Дом",
    "Мясной Ряд",
    "АвтоЛиния",
    "Легион Сервис",
    "ТехноСклад",
    "Север Логистик",
    "Вектор Плюс",
    "Сириус Трейд",
    "Прогресс Групп",
    "Сигма Маркет",
]

ACTIVITY_TREE = {
    "Еда": {
        "Мясная продукция": {},
        "Молочная продукция": {},
    },
    "Автомобили": {
        "Грузовые": {
            "Запчасти для грузовых": {},
            "Аксессуары для грузовых": {},
        },
        "Легковые": {
            "Запчасти": {},
            "Аксессуары": {},
        },
    },
}

# Deterministic scenarios for activity-based API tests.
# They explicitly cover:
# - root level only
# - child level only
# - grandchild level only
# - mixed levels within one branch
# - mixed levels across branches
ACTIVITY_SCENARIOS: list[list[str]] = [
    ["Еда"],
    ["Мясная продукция"],
    ["Молочная продукция"],
    ["Автомобили"],
    ["Грузовые"],
    ["Легковые"],
    ["Запчасти"],
    ["Аксессуары"],
    ["Запчасти для грузовых"],
    ["Аксессуары для грузовых"],
    ["Еда", "Мясная продукция", "Молочная продукция"],
    ["Автомобили", "Легковые", "Запчасти"],
    ["Автомобили", "Грузовые", "Запчасти для грузовых"],
    ["Еда", "Автомобили"],
]


def make_phone(rng: random.Random) -> str:
    if rng.random() < 0.55:
        first = rng.randint(2, 9)
        return f"{first}-{rng.randint(100, 999)}-{rng.randint(100, 999)}"
    return f"8-{rng.randint(900, 999)}-{rng.randint(100, 999)}-{rng.randint(10, 99)}-{rng.randint(10, 99)}"


def create_activity_tree(
    session,
    tree: dict[str, dict],
    parent: Activity | None = None,
    index: dict[str, Activity] | None = None,
) -> dict[str, Activity]:
    if index is None:
        index = {}

    for name, children in tree.items():
        activity = Activity(name=name, parent=parent)
        session.add(activity)
        session.flush()
        index[name] = activity
        create_activity_tree(session, children, activity, index)

    return index


def assign_activities_for_organization(
    idx: int,
    rng: random.Random,
    activity_index: dict[str, Activity],
    activity_pool: list[Activity],
) -> list[Activity]:
    if idx < len(ACTIVITY_SCENARIOS):
        scenario_names = ACTIVITY_SCENARIOS[idx]
        return [activity_index[name] for name in scenario_names]
    return rng.sample(activity_pool, k=rng.randint(1, 3))


def init_database(organizations_count: int = 35, seed: int = 42) -> None:
    if not 30 <= organizations_count <= 40:
        raise ValueError("organizations_count must be between 30 and 40")

    rng = random.Random(seed)
    session = SessionLocal()
    try:
        session.execute(
            text(
                "TRUNCATE TABLE organization_activities, organization_phones, "
                "organizations, activities, buildings RESTART IDENTITY CASCADE"
            )
        )
        session.commit()

        buildings: list[Building] = []
        for item in BUILDINGS:
            building = Building(
                address=item.address,
                latitude=item.latitude,
                longitude=item.longitude,
                location=WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326),
            )
            session.add(building)
            buildings.append(building)
        session.flush()

        activity_index = create_activity_tree(session, ACTIVITY_TREE)
        activity_pool = list(activity_index.values())

        for idx in range(organizations_count):
            name = f'{rng.choice(ORG_PREFIXES)} "{rng.choice(ORG_NAMES)} {idx + 1}"'
            organization = Organization(
                name=name,
                building_id=rng.choice(buildings).id,
            )
            session.add(organization)
            session.flush()

            if idx == 0:
                phones = ["2-222-222", "3-333-333", "8-923-666-13-13"]
            else:
                phones = [make_phone(rng) for _ in range(rng.randint(1, 3))]

            for phone in phones:
                session.add(
                    OrganizationPhone(
                        organization_id=organization.id,
                        phone=phone,
                    )
                )

            organization.activities.extend(
                assign_activities_for_organization(
                    idx=idx,
                    rng=rng,
                    activity_index=activity_index,
                    activity_pool=activity_pool,
                )
            )

        session.commit()
        print(
            f"Database initialized: {len(buildings)} buildings, "
            f"{len(activity_pool)} activities, {organizations_count} organizations."
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
