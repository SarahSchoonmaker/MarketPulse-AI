import { Link, NavLink } from "react-router-dom";

export default function Nav() {
  return (
    <div style={{ display: "flex", gap: 16, padding: 12, borderBottom: "1px solid #ddd" }}>
      <Link to="/" style={{ fontWeight: 700, textDecoration: "none" }}>MarketPulse</Link>
      <NavLink to="/" style={{ textDecoration: "none" }}>Dashboard</NavLink>
      <NavLink to="/events" style={{ textDecoration: "none" }}>Events</NavLink>
    </div>
  );
}
