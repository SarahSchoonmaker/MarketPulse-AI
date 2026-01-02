from .symbols import router as symbols_router
from .ingest import router as ingest_router
from .analytics import router as analytics_router
from .market_state import router as market_state_router
from .events import router as events_router
from .notes import router as notes_router

all_routers = [
    symbols_router,
    ingest_router,
    analytics_router,
    market_state_router,
    events_router,
    notes_router,
]
