import { useEffect, useState } from "react";

import { deleteLead, enrichLead, getLeads, updateLead } from "../api";
import Filters from "../components/Filters";
import LeadTable from "../components/LeadTable";

export default function Leads() {
  const [filters, setFilters] = useState({});
  const [leads, setLeads] = useState([]);
  const [status, setStatus] = useState("");

  async function load() {
    setStatus("Carregando leads...");
    try {
      const data = await getLeads(filters);
      setLeads(data);
      setStatus("");
    } catch (error) {
      setStatus(error.message);
    }
  }

  useEffect(() => {
    load();
  }, [filters]);

  async function handleUpdate(id, payload) {
    await updateLead(id, payload);
    await load();
  }

  async function handleDelete(id) {
    await deleteLead(id);
    await load();
  }

  async function handleEnrich(id) {
    setStatus("Enriquecendo contato...");
    try {
      await enrichLead(id);
      await load();
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Leads salvos</h1>
        <p>Filtre, qualifique, bloqueie abordagem e remova registros.</p>
      </header>
      <Filters filters={filters} onChange={setFilters} saved />
      {status ? <p className="status">{status}</p> : <LeadTable leads={leads} onUpdate={handleUpdate} onDelete={handleDelete} onEnrich={handleEnrich} />}
    </section>
  );
}
