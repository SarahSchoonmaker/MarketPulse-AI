from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import pandas as pd
from ..models import PriceBar, IndicatorValue

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.ewm(alpha=1/period, adjust=False).mean()
    loss = down.ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

def compute_and_store_indicators(db: Session, symbol_id: int, timeframe: str = "1d") -> int:
    bars = (db.query(PriceBar)
            .filter(PriceBar.symbol_id == symbol_id, PriceBar.timeframe == timeframe)
            .order_by(PriceBar.ts.asc())
            .all())
    if len(bars) < 30:
        return 0

    df = pd.DataFrame([{
        "ts": b.ts,
        "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume
    } for b in bars]).set_index("ts")

    df["ret_1"] = df["close"].pct_change()
    df["vol_20"] = df["ret_1"].rolling(20).std() * np.sqrt(252)
    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["rsi_14"] = _rsi(df["close"], 14)
    df["atr_14"] = _atr(df, 14)

    indicators = ["ret_1", "vol_20", "sma_20", "sma_50", "rsi_14", "atr_14"]
    rows = df[indicators].dropna()

    stored = 0
    for ts, row in rows.iterrows():
        for name in indicators:
            val = float(row[name])
            rec = IndicatorValue(symbol_id=symbol_id, timeframe=timeframe, ts=ts.to_pydatetime(), name=name, value=val)
            try:
                db.add(rec)
                db.flush()
                stored += 1
            except Exception:
                db.rollback()
                continue
    db.commit()
    return stored
