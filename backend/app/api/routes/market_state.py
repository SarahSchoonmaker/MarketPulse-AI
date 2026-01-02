from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...models import Symbol, MarketState
from ...schemas import MarketStateOut

router = APIRouter(prefix="/market-state", tags=["market-state"])

@router.get("", response_model=list[MarketStateOut])
def get_market_state(ticker: str, timeframe: str = "1d", limit: int = 300, db: Session = Depends(get_db)):
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one()
    rows = (db.query(MarketState)
            .filter(MarketState.symbol_id == sym.id, MarketState.timeframe == timeframe)
            .order_by(MarketState.ts.desc())
            .limit(limit)
            .all())
    rows = list(reversed(rows))
    return [MarketStateOut(ts=r.ts, trend_state=r.trend_state, vol_state=r.vol_state, label=r.label) for r in rows]
