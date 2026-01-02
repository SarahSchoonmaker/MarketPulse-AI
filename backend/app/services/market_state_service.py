from __future__ import annotations
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from ..models import IndicatorValue, MarketState

def compute_and_store_market_states(db: Session, symbol_id: int, timeframe: str = "1d") -> int:
    # Load needed indicators into a dataframe
    q = (db.query(IndicatorValue)
         .filter(IndicatorValue.symbol_id == symbol_id, IndicatorValue.timeframe == timeframe,
                 IndicatorValue.name.in_(["sma_20", "sma_50", "vol_20"]))
         .order_by(IndicatorValue.ts.asc()))
    rows = q.all()
    if len(rows) < 60:
        return 0

    df = pd.DataFrame([{"ts": r.ts, "name": r.name, "value": r.value} for r in rows])
    piv = df.pivot(index="ts", columns="name", values="value").dropna()
    if piv.empty:
        return 0

    # Volatility buckets using rolling percentiles
    vol = piv["vol_20"]
    vol_rank = vol.rolling(120, min_periods=30).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
    # trend rules based on moving averages
    trend = []
    vol_state = []
    label = []
    for ts, row in piv.iterrows():
        sma20 = row["sma_20"]
        sma50 = row["sma_50"]
        # trend
        if sma20 > sma50:
            t = "UP"
        elif sma20 < sma50:
            t = "DOWN"
        else:
            t = "SIDEWAYS"
        # vol
        vr = vol_rank.loc[ts]
        if pd.isna(vr):
            v = "NORMAL"
        elif vr >= 0.8:
            v = "HIGH"
        elif vr <= 0.2:
            v = "LOW"
        else:
            v = "NORMAL"
        trend.append(t)
        vol_state.append(v)
        label.append(f"TREND_{t}_{v}VOL")

    out = pd.DataFrame({"trend_state": trend, "vol_state": vol_state, "label": label}, index=piv.index)
    stored = 0
    for ts, row in out.iterrows():
        rec = MarketState(symbol_id=symbol_id, timeframe=timeframe, ts=ts.to_pydatetime(),
                          trend_state=row["trend_state"], vol_state=row["vol_state"], label=row["label"])
        try:
            db.add(rec)
            db.flush()
            stored += 1
        except Exception:
            db.rollback()
            continue
    db.commit()
    return stored
