from __future__ import annotations
import hashlib, json
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Symbol, IndicatorValue, MarketState, MarketEvent, LLMNote
from ..core.openai_client import chat_json

DAILY_SYSTEM = (
    "You are an assistant that writes concise, risk-focused market briefs. "
    "Use ONLY the provided metrics and classifications. Do not predict prices. "
    "Return STRICT JSON with keys: headline, market_state, key_levels, state_summary, risk_notes, invalidation."
)

EVENT_SYSTEM = (
    "You are an assistant that summarizes market events for traders. "
    "Use ONLY the provided event metrics and context. Do not predict. "
    "Return STRICT JSON with keys: event_title, event_type, what_happened, numbers, interpretation, risk_flags, followups."
)

def _hash_payload(payload: dict) -> str:
    s = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def generate_daily_brief(db: Session, ticker: str, timeframe: str = "1d") -> LLMNote:
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one()
    # latest market state
    ms = (db.query(MarketState)
          .filter(MarketState.symbol_id == sym.id, MarketState.timeframe == timeframe)
          .order_by(MarketState.ts.desc())
          .first())
    if not ms:
        raise ValueError("No market state found. Ingest data + compute indicators first.")

    # latest indicators for key levels
    names = ["sma_20", "sma_50", "rsi_14", "atr_14", "vol_20"]
    inds = (db.query(IndicatorValue)
            .filter(IndicatorValue.symbol_id == sym.id, IndicatorValue.timeframe == timeframe,
                    IndicatorValue.name.in_(names))
            .order_by(IndicatorValue.ts.desc())
            .all())
    latest = {}
    for r in inds:
        if r.name not in latest:
            latest[r.name] = {"ts": r.ts.isoformat(), "value": r.value}

    payload = {
        "ticker": sym.ticker,
        "timeframe": timeframe,
        "asof_ts": ms.ts.isoformat(),
        "market_state": {"trend": ms.trend_state, "volatility": ms.vol_state, "label": ms.label},
        "indicators": latest,
        "constraints": [
            "No predictions. Summarize current conditions.",
            "Use short bullets."
        ]
    }
    ih = _hash_payload(payload)

    existing = (db.query(LLMNote)
                .filter(LLMNote.note_type == "DAILY_BRIEF", LLMNote.symbol_id == sym.id,
                        LLMNote.timeframe == timeframe, LLMNote.asof_ts == ms.ts, LLMNote.input_hash == ih)
                .first())
    if existing:
        return existing

    user = json.dumps(payload, indent=2)
    out, meta = chat_json(DAILY_SYSTEM, user)

    note = LLMNote(
        note_type="DAILY_BRIEF",
        symbol_id=sym.id,
        timeframe=timeframe,
        asof_ts=ms.ts,
        input_hash=ih,
        output_json=out,
        model=meta.get("model"),
        latency_ms=meta.get("latency_ms"),
        prompt_tokens=meta.get("prompt_tokens"),
        completion_tokens=meta.get("completion_tokens"),
        total_tokens=meta.get("total_tokens"),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def generate_event_summary(db: Session, event_id: int) -> LLMNote:
    ev = db.query(MarketEvent).filter(MarketEvent.id == event_id).one()
    sym = db.query(Symbol).filter(Symbol.id == ev.symbol_id).one()

    payload = {
        "ticker": sym.ticker,
        "timeframe": ev.timeframe,
        "event_ts": ev.event_ts.isoformat(),
        "event_type": ev.event_type,
        "severity": ev.severity,
        "metrics": ev.metrics_json,
        "constraints": [
            "No predictions. Explain what the event means and what to watch."
        ]
    }
    ih = _hash_payload(payload)

    existing = (db.query(LLMNote)
                .filter(LLMNote.note_type == "EVENT_SUMMARY", LLMNote.related_event_id == ev.id,
                        LLMNote.input_hash == ih)
                .first())
    if existing:
        return existing

    user = json.dumps(payload, indent=2)
    out, meta = chat_json(EVENT_SYSTEM, user)

    note = LLMNote(
        note_type="EVENT_SUMMARY",
        symbol_id=sym.id,
        related_event_id=ev.id,
        timeframe=ev.timeframe,
        asof_ts=ev.event_ts,
        input_hash=ih,
        output_json=out,
        model=meta.get("model"),
        latency_ms=meta.get("latency_ms"),
        prompt_tokens=meta.get("prompt_tokens"),
        completion_tokens=meta.get("completion_tokens"),
        total_tokens=meta.get("total_tokens"),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
