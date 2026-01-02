from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.db import Base

class PriceBar(Base):
    __tablename__ = "price_bars"
    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "ts", name="uq_pricebar_symbol_tf_ts"),
        Index("ix_pricebars_symbol_tf_ts", "symbol_id", "timeframe", "ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id", ondelete="CASCADE"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)  # e.g. '1d'
    ts: Mapped["DateTime"] = mapped_column(DateTime(timezone=False), index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="alphavantage")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    symbol = relationship("Symbol")
