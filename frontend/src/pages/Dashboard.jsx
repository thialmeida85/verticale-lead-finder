import { useEffect, useState } from "react";

import { getDashboard } from "../api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getDashboard().then(setStats).catch(console.error);
  }, []);

  if (!stats) return <p className="status">Carregando indicadores...</p>;

  return (
    <section className="page">
      <header className="page-header">
        <h1>Dashboard</h1>
        <p>Visão operacional da prospecção B2B.</p>
      </header>
      <div className="metrics-grid">
        <Metric label="Total de leads" value={stats.total_leads} />
        <Metric label="Com telefone" value={stats.leads_com_telefone} />
        <Metric label="Com e-mail" value={stats.leads_com_email} />
        <Metric label="Score alto" value={stats.leads_score_alto} />
        <Metric label="Exportados" value={stats.leads_exportados} />
      </div>
      <div className="dashboard-grid">
        <Breakdown title="Leads por cidade" items={stats.leads_por_cidade} />
        <Breakdown title="Leads por UF" items={stats.leads_por_uf} />
        <Breakdown title="Leads por status" items={stats.leads_por_status} />
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Breakdown({ title, items }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      <div className="compact-list">
        {Object.entries(items).map(([label, value]) => (
          <div key={label} className="compact-row">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
