import { NavLink, Route, Routes } from "react-router-dom";

import BuscarEmpresas from "./pages/BuscarEmpresas";
import Dashboard from "./pages/Dashboard";
import Exportar from "./pages/Exportar";
import ImportarPDF from "./pages/ImportarPDF"; // Importar a nova página
import Importar from "./pages/Importar";
import LeadDetalhes from "./pages/LeadDetalhes";
import Leads from "./pages/Leads";
import "./styles.css";

const navItems = [
  ["Dashboard", "/"],
  ["Buscar empresas", "/buscar"],
  ["Leads salvos", "/leads"],
  ["Importar CSV", "/importar"],
  ["Importar PDF", "/importar-pdf"], // Adicionar o novo item de menu
  ["Exportar leads", "/exportar"],
];

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Verticale</div>
        <nav>
          {navItems.map(([label, to]) => (
            <NavLink key={to} to={to} end={to === "/"}>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/buscar" element={<BuscarEmpresas />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/leads/:id" element={<LeadDetalhes />} />
          <Route path="/importar" element={<Importar />} />
          <Route path="/importar-pdf" element={<ImportarPDF />} /> {/* Adicionar a nova rota */}
          <Route path="/exportar" element={<Exportar />} />
        </Routes>
      </main>
    </div>
  );
}
