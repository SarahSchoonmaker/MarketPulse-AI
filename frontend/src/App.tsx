import { Routes, Route } from "react-router-dom";
import Nav from "./components/Nav";
import Dashboard from "./pages/Dashboard";
import SymbolPage from "./pages/Symbol";
import EventsPage from "./pages/Events";

export default function App() {
  return (
    <div>
      <Nav />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/symbol/:ticker" element={<SymbolPage />} />
        <Route path="/events" element={<EventsPage />} />
      </Routes>
    </div>
  );
}
