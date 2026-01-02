from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base

class Symbol(Base):
    __tablename__ = "symbols"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    asset_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
