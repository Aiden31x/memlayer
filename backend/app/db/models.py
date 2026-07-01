import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, DateTime, Float, ForeignKey, String, func, null
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String,nullable=False,index=True)
    agent_id: Mapped[str | null] = mapped_column(String,nullable=True,index=True)
    text: Mapped[str] = mapped_column(String,nullable=False)
    category: Mapped[str] = mapped_column(String,nullable=False)
    status: Mapped[str] = mapped_column(String,nullable=False,default="active", index=True)
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True),ForeignKey("memories.id"),nullable=True)
    confidence: Mapped[float] = mapped_column(Float,nullable=False,default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime,nullable=False,default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now(), onupdate=func.now())
