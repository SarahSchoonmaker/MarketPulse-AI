from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...models import Symbol, MarketEvent
from ...schemas import EventOut
from ...services.event_service import detect_and_store_events
from ...services.ingest_service import get_or_create_symbol

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/detect")
def detect_events(ticker: str, timeframe: str = "1d", db: Session = Depends(get_db)):
    sym = get_or_create_symbol(db, ticker)
    added = detect_and_store_events(db, sym.id, timeframe=timeframe)
    return {"ticker": ticker.upper(), "events_added": added}

@router.get("/list", response_model=list[EventOut])
def list_events(ticker: str, timeframe: str = "1d", limit: int = 50, db: Session = Depends(get_db)):
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one()
    rows = (db.query(MarketEvent)
            .filter(MarketEvent.symbol_id == sym.id, MarketEvent.timeframe == timeframe)
            .order_by(MarketEvent.event_ts.desc())
            .limit(limit)
            .all())
    return [EventOut(id=r.id, event_ts=r.event_ts, event_type=r.event_type, severity=r.severity, metrics_json=r.metrics_json) for r in rows]
