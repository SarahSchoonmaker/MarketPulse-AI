from sqlalchemy import String, DateTime, ForeignKey, Integer, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base

class MarketEvent(Base):
    __tablename__ = "market_events"
    __table_args__ = (
        Index("ix_event_symbol_tf_ts", "symbol_id", "timeframe", "event_ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id", ondelete="CASCADE"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    event_ts: Mapped["DateTime"] = mapped_column(DateTime(timezone=False), index=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)   # GAP_UP, VOL_SPIKE, etc.
    severity: Mapped[int] = mapped_column(Integer, default=1)         # 1-5
    metrics_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
