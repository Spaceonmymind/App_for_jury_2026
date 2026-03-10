from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Score(Base):
    __tablename__ = "scores"

    __table_args__ = (
        UniqueConstraint(
            "expert_id",
            "project_id",
            "criterion_id",
            name="uq_score_expert_project_criterion"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    expert_id: Mapped[int] = mapped_column(ForeignKey("experts.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    criterion_id: Mapped[int] = mapped_column(ForeignKey("criteria.id"), nullable=False, index=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    expert = relationship("Expert", back_populates="scores")
    project = relationship("Project", back_populates="scores")
    criterion = relationship("Criterion", back_populates="scores")