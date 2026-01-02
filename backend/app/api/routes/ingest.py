from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...services.ingest_service import ingest_daily, get_or_create_symbol
from ...services.indicator_service import compute_and_store_indicators
from ...services.market_state_service import compute_and_store_market_states
from ...services.event_service import detect_and_store_events

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/daily")
def ingest_daily_endpoint(ticker: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    ins = ingest_daily(db, ticker, timeframe="1d")
    sym = get_or_create_symbol(db, ticker)
    ind = compute_and_store_indicators(db, sym.id, "1d")
    ms = compute_and_store_market_states(db, sym.id, "1d")
    ev = detect_and_store_events(db, sym.id, "1d")
    return {"ticker": ticker.upper(), "price_bars_added": ins, "indicators_added": ind, "market_states_added": ms, "events_added": ev}
