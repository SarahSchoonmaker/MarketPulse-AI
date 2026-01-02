from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...models import Symbol, PriceBar, IndicatorValue
from ...schemas import PriceBarOut, IndicatorOut

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/price-bars", response_model=list[PriceBarOut])
def get_price_bars(ticker: str, timeframe: str = "1d", limit: int = 300, db: Session = Depends(get_db)):
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one()
    rows = (db.query(PriceBar)
            .filter(PriceBar.symbol_id == sym.id, PriceBar.timeframe == timeframe)
            .order_by(PriceBar.ts.desc())
            .limit(limit)
            .all())
    rows = list(reversed(rows))
    return [PriceBarOut(ts=r.ts, open=r.open, high=r.high, low=r.low, close=r.close, volume=r.volume) for r in rows]

@router.get("/indicators", response_model=list[IndicatorOut])
def get_indicators(
    ticker: str,
    timeframe: str = "1d",
    names: str = Query("sma_20,sma_50,rsi_14,atr_14,vol_20"),
    limit: int = 500,
    db: Session = Depends(get_db),
):
    sym = db.query(Symbol).filter(Symbol.ticker == ticker.upper()).one()
    name_list = [n.strip() for n in names.split(",") if n.strip()]
    rows = (db.query(IndicatorValue)
            .filter(IndicatorValue.symbol_id == sym.id, IndicatorValue.timeframe == timeframe,
                    IndicatorValue.name.in_(name_list))
            .order_by(IndicatorValue.ts.desc())
            .limit(limit)
            .all())
    rows = list(reversed(rows))
    return [IndicatorOut(ts=r.ts, name=r.name, value=r.value) for r in rows]
