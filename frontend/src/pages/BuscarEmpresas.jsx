import { useState } from "react";

import { consultarCnpj, saveLead } from "../api";
import { Toggle } from "../components/Filters";
import LeadTable from "../components/LeadTable";

const initialFilters = {
  cnpj: "",
  termo: "",
  cidade: "",
  uf: "",
  cnae: "",
  segmento: "",
  porte: "",
  somente_ativas: true,
  somente_matriz: false,
  somente_com_telefone: false,
  limite: 20,
};

export default function BuscarEmpresas() {
  const [filters, setFilters] = useState(initialFilters);
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("");

  function setField(field, value) {
    setFilters({ ...filters, [field]: value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("Consultando API de CNPJ...");
    try {
      const data = await consultarCnpj({ ...filters, limite: Number(filters.limite) || 20 });
      setResults(data);
      setStatus(data.length ? `${data.length} resultado(s) encontrado(s).` : "Nenhum resultado encontrado para os filtros informados.");
    } catch (error) {
      setStatus(error.message);
      setResults([]);
    }
  }

  async function handleSave(lead) {
    setStatus("Salvando lead...");
    try {
      await saveLead(lead);
      setStatus("Lead salvo. Duplicidades por CNPJ são atualizadas automaticamente.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Buscar empresas</h1>
        <p>Consulte por CNPJ e prepare a tela para APIs com busca por filtros.</p>
      </header>
      <form className="panel filter-form" onSubmit={handleSubmit}>
        <input value={filters.cnpj} onChange={(event) => setField("cnpj", event.target.value)} placeholder="CNPJ" />
        <input value={filters.termo} onChange={(event) => setField("termo", event.target.value)} placeholder="Termo" />
        <input value={filters.cidade} onChange={(event) => setField("cidade", event.target.value)} placeholder="Cidade" />
        <input value={filters.uf} onChange={(event) => setField("uf", event.target.value.toUpperCase())} placeholder="UF" maxLength="2" />
        <input value={filters.cnae} onChange={(event) => setField("cnae", event.target.value)} placeholder="CNAE" />
        <input value={filters.segmento} onChange={(event) => setField("segmento", event.target.value)} placeholder="Segmento" />
        <input value={filters.porte} onChange={(event) => setField("porte", event.target.value)} placeholder="Porte" />
        <input type="number" min="1" max="100" value={filters.limite} onChange={(event) => setField("limite", event.target.value)} placeholder="Limite" />
        <Toggle label="Somente empresas ativas" checked={filters.somente_ativas} onChange={(checked) => setField("somente_ativas", checked)} />
        <Toggle label="Somente matriz" checked={filters.somente_matriz} onChange={(checked) => setField("somente_matriz", checked)} />
        <Toggle label="Somente com telefone" checked={filters.somente_com_telefone} onChange={(checked) => setField("somente_com_telefone", checked)} />
        <button type="submit">Buscar</button>
      </form>
      {status && <p className="status">{status}</p>}
      <LeadTable leads={results} mode="search" onSave={handleSave} />
    </section>
  );
}
