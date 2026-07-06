import { useState } from "react";

import { exportLeads } from "../api";
import { Toggle } from "../components/Filters";

export default function Exportar() {
  const [format, setFormat] = useState("csv");
  const [filters, setFilters] = useState({
    cidade: "",
    uf: "",
    segmento: "",
    cnae: "",
    min_score: "",
    status_lead: "",
    tem_telefone: "",
    tem_email: "",
    excluir_nao_contatar: true,
    excluir_descartados: true,
    excluir_ja_abordados: false,
  });
  const [status, setStatus] = useState("");

  function setField(field, value) {
    setFilters({ ...filters, [field]: value });
  }

  async function handleExport() {
    setStatus("Gerando arquivo...");
    try {
      const payload = {
        ...filters,
        min_score: filters.min_score ? Number(filters.min_score) : null,
        tem_telefone: filters.tem_telefone || null,
        tem_email: filters.tem_email || null,
      };
      const { blob, filename } = await exportLeads(format, payload);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
      setStatus("Exportação pronta.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Exportar leads</h1>
        <p>Gere CSV ou XLSX pronto para prospecção.</p>
      </header>
      <div className="panel filter-form">
        <select value={format} onChange={(event) => setFormat(event.target.value)}>
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
        </select>
        <input value={filters.cidade} onChange={(event) => setField("cidade", event.target.value)} placeholder="Cidade" />
        <input value={filters.uf} onChange={(event) => setField("uf", event.target.value.toUpperCase())} placeholder="UF" maxLength="2" />
        <input value={filters.segmento} onChange={(event) => setField("segmento", event.target.value)} placeholder="Segmento" />
        <input value={filters.cnae} onChange={(event) => setField("cnae", event.target.value)} placeholder="CNAE" />
        <input type="number" min="0" max="100" value={filters.min_score} onChange={(event) => setField("min_score", event.target.value)} placeholder="Score mínimo" />
        <select value={filters.status_lead} onChange={(event) => setField("status_lead", event.target.value)}>
          <option value="">Status</option>
          <option value="importado">Importado</option>
          <option value="novo">Novo</option>
          <option value="abordado">Abordado</option>
          <option value="qualificado">Qualificado</option>
          <option value="descartado">Descartado</option>
        </select>
        <Toggle label="Somente com telefone" checked={filters.tem_telefone === "true"} onChange={(checked) => setField("tem_telefone", checked ? "true" : "")} />
        <Toggle label="Somente com e-mail" checked={filters.tem_email === "true"} onChange={(checked) => setField("tem_email", checked ? "true" : "")} />
        <Toggle label="Excluir não contatar" checked={filters.excluir_nao_contatar} onChange={(checked) => setField("excluir_nao_contatar", checked)} />
        <Toggle label="Excluir descartados" checked={filters.excluir_descartados} onChange={(checked) => setField("excluir_descartados", checked)} />
        <Toggle label="Excluir já abordados" checked={filters.excluir_ja_abordados} onChange={(checked) => setField("excluir_ja_abordados", checked)} />
        <button type="button" onClick={handleExport}>Exportar</button>
      </div>
      {status && <p className="status">{status}</p>}
    </section>
  );
}
