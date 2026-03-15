"""Agent Definition model."""
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AgentDefinition(Base, TimestampMixin):
    """Board agent definition with constitution."""

    __tablename__ = "agent_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    constitution_text: Mapped[str] = mapped_column(Text, nullable=False)
    version_id: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mandate: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    focus_areas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
