from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.activity import organization_activities

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.building import Building
    from app.models.organization_phone import OrganizationPhone


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False)

    building: Mapped["Building"] = relationship(back_populates="organizations")
    phones: Mapped[list["OrganizationPhone"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        secondary=organization_activities, back_populates="organizations"
    )
