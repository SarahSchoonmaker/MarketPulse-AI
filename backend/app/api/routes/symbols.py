from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...models import Symbol
from ...schemas import SymbolOut

router = APIRouter(prefix="/symbols", tags=["symbols"])

@router.get("/search", response_model=list[SymbolOut])
def search_symbols(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    q_u = q.upper()
    rows = (db.query(Symbol)
            .filter(Symbol.ticker.like(f"%{q_u}%"))
            .order_by(Symbol.ticker.asc())
            .limit(20)
            .all())
    return [SymbolOut(ticker=r.ticker, name=r.name) for r in rows]
