from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base

class MarketState(Base):
    """Deterministic classification of market conditions (trend + volatility)."""
    __tablename__ = "market_states"
    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "ts", name="uq_marketstate_symbol_tf_ts"),
        Index("ix_marketstate_symbol_tf_ts", "symbol_id", "timeframe", "ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id", ondelete="CASCADE"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    ts: Mapped["DateTime"] = mapped_column(DateTime(timezone=False), index=True)

    trend_state: Mapped[str] = mapped_column(String(16))       # UP/DOWN/SIDEWAYS
    vol_state: Mapped[str] = mapped_column(String(16))         # LOW/NORMAL/HIGH
    label: Mapped[str] = mapped_column(String(64))             # e.g. TREND_UP_HIGHVOL

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
