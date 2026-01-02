import { useState } from "react";
import { apiGet, apiPost } from "../api/client";
import type { EventRow } from "../types";

export default function EventsPage() {
  const [ticker, setTicker] = useState("SPY");
  const [events, setEvents] = useState<EventRow[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [err, setErr] = useState<string>("");

  async function refresh() {
    setErr("");
    try {
      await apiPost(`/events/detect?ticker=${encodeURIComponent(ticker)}&timeframe=1d`);
      const rows = await apiGet<EventRow[]>(`/events/list?ticker=${encodeURIComponent(ticker)}&timeframe=1d&limit=50`);
      setEvents(rows);
      setSummary(null);
    } catch (e: any) {
      setErr(e.message ?? String(e));
    }
  }

  async function summarize(eventId: number) {
    setErr("");
    try {
      const r = await apiPost<any>(`/notes/event-summary?event_id=${eventId}`);
      setSummary(r.output_json);
    } catch (e: any) {
      setErr(e.message ?? String(e));
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h2>Market Events</h2>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input value={ticker} onChange={(e) => setTicker(e.target.value)} />
        <button onClick={refresh}>Detect + Load</button>
      </div>

      <div style={{ display: "flex", gap: 16, marginTop: 16, flexWrap: "wrap" }}>
        <div style={{ flex: "1 1 560px" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>Time</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>Type</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>Severity</th>
                <th style={{ borderBottom: "1px solid #ddd" }}></th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id}>
                  <td style={{ padding: "8px 0" }}>{e.event_ts.slice(0, 10)}</td>
                  <td>{e.event_type}</td>
                  <td>{e.severity}</td>
                  <td style={{ textAlign: "right" }}>
                    <button onClick={() => summarize(e.id)}>AI Summary</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ flex: "1 1 420px", border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
          <h3>AI Event Summary</h3>
          <pre style={{ background: "#f6f6f6", padding: 12, whiteSpace: "pre-wrap" }}>
            {summary ? JSON.stringify(summary, null, 2) : "Select an event to summarize."}
          </pre>
        </div>
      </div>
    </div>
  );
}
