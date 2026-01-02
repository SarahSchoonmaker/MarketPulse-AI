from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.db import Base, engine
from .api.routes import all_routers

app = FastAPI(title="MarketPulse AI Analytics API", version="0.1.0")

# CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (MVP). For production, use Alembic migrations.
Base.metadata.create_all(bind=engine)

for r in all_routers:
    app.include_router(r)

@app.get("/health")
def health():
    return {"status": "ok"}
