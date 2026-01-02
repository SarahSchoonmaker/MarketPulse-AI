from __future__ import annotations
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from ..models import PriceBar, MarketEvent

def detect_and_store_events(db: Session, symbol_id: int, timeframe: str = "1d", lookback: int = 120) -> int:
    bars = (db.query(PriceBar)
            .filter(PriceBar.symbol_id == symbol_id, PriceBar.timeframe == timeframe)
            .order_by(PriceBar.ts.asc())
            .all())
    if len(bars) < 40:
        return 0
    df = pd.DataFrame([{
        "ts": b.ts,
        "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume or 0.0
    } for b in bars]).set_index("ts")

    df["prior_close"] = df["close"].shift(1)
    df["gap_pct"] = (df["open"] - df["prior_close"]) / df["prior_close"]
    df["range_pct"] = (df["high"] - df["low"]) / df["prior_close"]
    df["vol_z"] = (df["volume"] - df["volume"].rolling(20).mean()) / df["volume"].rolling(20).std()

    # breakout levels
    df["hh_20"] = df["high"].rolling(20).max().shift(1)
    df["ll_20"] = df["low"].rolling(20).min().shift(1)

    recent = df.tail(lookback).dropna()
    stored = 0
    for ts, row in recent.iterrows():
        metrics = {
            "gap_pct": float(row["gap_pct"]),
            "range_pct": float(row["range_pct"]),
            "volume_z": float(row["vol_z"]) if np.isfinite(row["vol_z"]) else None
        }

        # GAP events
        if abs(metrics["gap_pct"]) >= 0.015:
            etype = "GAP_UP" if metrics["gap_pct"] > 0 else "GAP_DOWN"
            sev = 3 if abs(metrics["gap_pct"]) < 0.03 else 4
            stored += _store(db, symbol_id, timeframe, ts, etype, sev, metrics)

        # Vol spike
        if metrics["volume_z"] is not None and metrics["volume_z"] >= 2.0:
            stored += _store(db, symbol_id, timeframe, ts, "VOL_SPIKE", 3, metrics)

        # Breakout
        if row["close"] > row["hh_20"]:
            stored += _store(db, symbol_id, timeframe, ts, "BREAKOUT_UP", 2, metrics)
        if row["close"] < row["ll_20"]:
            stored += _store(db, symbol_id, timeframe, ts, "BREAKOUT_DOWN", 2, metrics)

        # Reversal (simple): large range + close opposite side
        if metrics["range_pct"] >= 0.02:
            # If close near low after big up gap -> reversal down, etc.
            close_pos = (row["close"] - row["low"]) / max(row["high"] - row["low"], 1e-9)
            if close_pos <= 0.2:
                stored += _store(db, symbol_id, timeframe, ts, "REVERSAL_DOWN", 2, metrics)
            elif close_pos >= 0.8:
                stored += _store(db, symbol_id, timeframe, ts, "REVERSAL_UP", 2, metrics)

    db.commit()
    return stored

def _store(db: Session, symbol_id: int, timeframe: str, ts, event_type: str, severity: int, metrics: dict) -> int:
    rec = MarketEvent(symbol_id=symbol_id, timeframe=timeframe, event_ts=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
                      event_type=event_type, severity=severity, metrics_json=metrics)
    try:
        db.add(rec)
        db.flush()
        return 1
    except Exception:
        db.rollback()
        return 0
