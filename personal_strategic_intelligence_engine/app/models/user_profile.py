"""User Profile model."""
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class UserProfile(Base, TimestampMixin):
    """User profile and system constitution."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mission_statement: Mapped[str] = mapped_column(Text, nullable=False)
    values: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    priorities: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    non_negotiables: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    active_goals: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_tolerance: Mapped[str] = mapped_column(String(50), nullable=False, default="moderate")
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
