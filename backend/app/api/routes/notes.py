import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...services.llm_service import generate_daily_brief
from ...schemas import LLMNoteOut

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/daily-brief", response_model=LLMNoteOut)
def daily_brief(ticker: str = Query(..., min_length=1), timeframe: str = "1d", db: Session = Depends(get_db)):
    note = generate_daily_brief(db, ticker, timeframe=timeframe)

    # note.output_json is stored as a JSON string; convert to dict for response
    output = note.output_json
    if isinstance(output, str):
        output = json.loads(output)

    return LLMNoteOut(
        id=note.id,
        note_type=note.note_type,
        output_json=output,
    )
