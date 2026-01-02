import { useState } from "react";
import { apiPost } from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [ticker, setTicker] = useState("SPY");
  const [status, setStatus] = useState<string>("");
  const nav = useNavigate();

  async function ingest() {
    setStatus("Ingesting...");
    try {
      const r = await apiPost<any>(`/ingest/daily?ticker=${encodeURIComponent(ticker)}`);
      setStatus(JSON.stringify(r, null, 2));
      nav(`/symbol/${ticker.toUpperCase()}`);
    } catch (e: any) {
      setStatus(e.message ?? String(e));
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: "0 auto" }}>
      <h2>Dashboard</h2>
      <p>Enter a ticker, ingest daily data (Alpha Vantage), then view analytics + AI brief.</p>

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input value={ticker} onChange={(e) => setTicker(e.target.value)} />
        <button onClick={ingest}>Ingest + Compute</button>
      </div>

      <pre style={{ marginTop: 12, background: "#f6f6f6", padding: 12, whiteSpace: "pre-wrap" }}>
        {status}
      </pre>
    </div>
  );
}
