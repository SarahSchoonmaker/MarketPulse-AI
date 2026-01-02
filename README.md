# MarketPulse AI Analytics

**MarketPulse AI Analytics** is a full-stack analytics MVP that ingests market data, computes deterministic technical/risk metrics, detects market events, and uses an LLM to generate **structured, auditable summaries** for traders and analysts.

> Design principle: **Indicators & event logic are deterministic.** The LLM summarizes the computed facts; it does not generate trading signals.

---

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Postgres
- **Market Data:** Alpha Vantage (daily adjusted)
- **AI:** OpenAI API (JSON output)
- **Frontend:** React + Recharts
- **Dev:** Docker Compose (Postgres only)

---

## Features

### Project 1 — Market State Dashboard

- Ingest daily OHLCV from Alpha Vantage
- Compute indicators: SMA(20/50), RSI(14), ATR(14), returns, realized vol
- Classify market conditions ("market state"):
  - **Trend:** UP / DOWN / SIDEWAYS (based on SMA20 vs SMA50)
  - **Volatility:** LOW / NORMAL / HIGH (based on rolling volatility percentiles)
- Generate an **AI daily brief** (structured JSON) from the latest computed values

### Project 2 — Event & Risk Monitor

- Detect events:
  - **GAP_UP / GAP_DOWN** (open vs prior close)
  - **VOL_SPIKE** (volume z-score)
  - **BREAKOUT_UP / BREAKOUT_DOWN** (20-day high/low break)
  - **REVERSAL_UP / REVERSAL_DOWN** (large range + close position)
- Generate an **AI event summary** (structured JSON) per event

---

## Local Setup

### 1) Start Postgres

```bash
docker compose up -d
```

### 2) Backend

```bash
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open: `http://localhost:8000/health`

### 3) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## Quick Demo Flow (Recommended)

1. Go to the Dashboard page
2. Enter a ticker (e.g., `SPY`) and click **Ingest + Compute**
3. View:
   - **Price chart + latest market state**
   - Click **Generate Brief** to create an AI daily brief
4. Go to **Events**
   - Click **Detect + Load**
   - Click **AI Summary** on any event row

---

## Environment Variables

Backend `.env`:

- `DATABASE_URL` (Postgres SQLAlchemy URL)
- `ALPHAVANTAGE_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-4.1-mini`)

---

## Notes

- For MVP speed, tables auto-create on backend startup (`Base.metadata.create_all`).
- Alembic is included if you want migrations later (recommended for production).
- Alpha Vantage free-tier rate limits are real — ingest sparingly.

---

## Disclaimer

This project is for educational/research use only. It does not provide investment advice.
