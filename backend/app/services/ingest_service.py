from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Symbol, PriceBar
from ..core.alpha_vantage import fetch_daily  

def get_or_create_symbol(db: Session, ticker: str) -> Symbol:
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one_or_none()
    if sym:
        return sym
    sym = Symbol(ticker=ticker.upper(), name=None, asset_type="EQUITY")
    db.add(sym)
    db.commit()
    db.refresh(sym)
    return sym

def ingest_daily(db: Session, ticker: str, timeframe: str = "1d") -> int:
    sym = get_or_create_symbol(db, ticker)
    payload = fetch_daily(sym.ticker)        
    series = payload["Time Series (Daily)"]

    inserted = 0
    for day_str, row in series.items():
        ts = datetime.fromisoformat(day_str)
        bar = PriceBar(
            symbol_id=sym.id,
            timeframe=timeframe,
            ts=ts,
            open=float(row["1. open"]),
            high=float(row["2. high"]),
            low=float(row["3. low"]),
            close=float(row["4. close"]),
            volume=float(row["5. volume"]) if "5. volume" in row else None,  
            source="alphavantage",
        )
        try:
            db.add(bar)
            db.flush()
            inserted += 1
        except Exception:
            db.rollback()
            continue

    db.commit()
    return inserted
