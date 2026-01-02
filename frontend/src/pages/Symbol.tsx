import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { apiGet, apiPost } from "../api/client";
import type { PriceBar, MarketState } from "../types";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function SymbolPage() {
  const { ticker } = useParams();
  const T = (ticker ?? "").toUpperCase();

  const [bars, setBars] = useState<PriceBar[]>([]);
  const [states, setStates] = useState<MarketState[]>([]);
  const [brief, setBrief] = useState<any>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        setErr("");
        const b = await apiGet<PriceBar[]>(`/analytics/price-bars?ticker=${T}&timeframe=1d&limit=260`);
        const s = await apiGet<MarketState[]>(`/market-state?ticker=${T}&timeframe=1d&limit=260`);
        setBars(b);
        setStates(s);
      } catch (e: any) {
        setErr(e.message ?? String(e));
      }
    })();
  }, [T]);

  const chartData = useMemo(() => {
    return bars.map((b) => ({
      ts: b.ts.slice(0, 10),
      close: b.close,
    }));
  }, [bars]);

  async function generateBrief() {
    setErr("");
    try {
      const r = await apiPost<any>(`/notes/daily-brief?ticker=${T}&timeframe=1d`);
      setBrief(r.output_json);
    } catch (e: any) {
      setErr(e.message ?? String(e));
    }
  }

  const latestState = states.length ? states[states.length - 1] : null;

  return (
    <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h2>{T}</h2>

      {err && <div style={{ color: "crimson" }}>{err}</div>}

      <div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ flex: "1 1 520px", border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
          <h3>Price (Daily Close)</h3>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="ts" hide />
                <YAxis domain={["auto", "auto"]} />
                <Tooltip />
                <Line type="monotone" dataKey="close" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {latestState && (
            <div style={{ marginTop: 8 }}>
              <strong>Market State:</strong> {latestState.trend_state} / {latestState.vol_state} — {latestState.label}
            </div>
          )}
        </div>

        <div style={{ flex: "1 1 420px", border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
          <h3>AI Daily Brief</h3>
          <button onClick={generateBrief}>Generate Brief</button>
          <pre style={{ marginTop: 12, background: "#f6f6f6", padding: 12, whiteSpace: "pre-wrap" }}>
            {brief ? JSON.stringify(brief, null, 2) : "No brief yet."}
          </pre>
        </div>
      </div>
    </div>
  );
}
