from sqlalchemy import String, DateTime, Float, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base

class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "ts", "name", name="uq_indicator_symbol_tf_ts_name"),
        Index("ix_indicator_symbol_tf_ts", "symbol_id", "timeframe", "ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id", ondelete="CASCADE"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    ts: Mapped["DateTime"] = mapped_column(DateTime(timezone=False), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
