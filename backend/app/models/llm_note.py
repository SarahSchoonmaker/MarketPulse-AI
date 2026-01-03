from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base

class LLMNote(Base):
    __tablename__ = "llm_notes"
    __table_args__ = (
        Index("ix_llmnote_symbol_type_ts", "symbol_id", "note_type", "asof_ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    note_type: Mapped[str] = mapped_column(String(32), index=True)  # DAILY_BRIEF / EVENT_SUMMARY
    symbol_id: Mapped[int | None] = mapped_column(
        ForeignKey("symbols.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    related_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("market_events.id", ondelete="SET NULL"),
        nullable=True
    )

    timeframe: Mapped[str | None] = mapped_column(String(16), nullable=True)
    asof_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, index=True)

    input_hash: Mapped[str] = mapped_column(String(64), index=True)
    output_json: Mapped[dict] = mapped_column(JSONB)

    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
