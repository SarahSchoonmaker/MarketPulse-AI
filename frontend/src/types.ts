export type PriceBar = { ts: string; open: number; high: number; low: number; close: number; volume?: number | null };
export type MarketState = { ts: string; trend_state: string; vol_state: string; label: string };
export type EventRow = { id: number; event_ts: string; event_type: string; severity: number; metrics_json: any };
