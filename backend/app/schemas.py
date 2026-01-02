from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class SymbolOut(BaseModel):
    ticker: str
    name: Optional[str] = None

class PriceBarOut(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

class IndicatorOut(BaseModel):
    ts: datetime
    name: str
    value: float

class MarketStateOut(BaseModel):
    ts: datetime
    trend_state: str
    vol_state: str
    label: str

class EventOut(BaseModel):
    id: int
    event_ts: datetime
    event_type: str
    severity: int
    metrics_json: Dict

class LLMNoteOut(BaseModel):
    id: int
    note_type: str
    output_json: Dict
