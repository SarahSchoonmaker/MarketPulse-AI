from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...schemas import LLMNoteOut
from ...services.llm_service import generate_daily_brief, generate_event_summary

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/daily-brief", response_model=LLMNoteOut)
def daily_brief(ticker: str = Query(...), timeframe: str = "1d", db: Session = Depends(get_db)):
    note = generate_daily_brief(db, ticker, timeframe=timeframe)
    return LLMNoteOut(id=note.id, note_type=note.note_type, output_json=note.output_json)

@router.post("/event-summary", response_model=LLMNoteOut)
def event_summary(event_id: int = Query(...), db: Session = Depends(get_db)):
    note = generate_event_summary(db, event_id)
    return LLMNoteOut(id=note.id, note_type=note.note_type, output_json=note.output_json)
