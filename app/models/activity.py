from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Index, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id", ondelete="RESTRICT"), nullable=True)

    parent: Mapped["Activity | None"] = relationship(back_populates="children", remote_side=[id])
    children: Mapped[list["Activity"]] = relationship(back_populates="parent")
    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_activities, back_populates="activities"
    )

    __table_args__ = (
        Index("ix_activities_parent_id", "parent_id"),
        Index(
            "uq_activities_parent_lower_name",
            func.coalesce(parent_id, 0),
            func.lower(name),
            unique=True,
        ),
    )
