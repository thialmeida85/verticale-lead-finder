export default function Filters({ filters, onChange, saved = false }) {
  function setField(field, value) {
    onChange({ ...filters, [field]: value });
  }

  return (
    <div className="filters">
      <input value={filters.q || ""} onChange={(event) => setField("q", event.target.value)} placeholder="Termo, nome ou CNPJ" />
      <input value={filters.cidade || ""} onChange={(event) => setField("cidade", event.target.value)} placeholder="Cidade" />
      <input value={filters.uf || ""} onChange={(event) => setField("uf", event.target.value.toUpperCase())} placeholder="UF" maxLength="2" />
      <input value={filters.segmento || ""} onChange={(event) => setField("segmento", event.target.value)} placeholder="Segmento" />
      <input value={filters.cnae || ""} onChange={(event) => setField("cnae", event.target.value)} placeholder="CNAE" />
      <input type="number" min="0" max="100" value={filters.min_score || ""} onChange={(event) => setField("min_score", event.target.value)} placeholder="Score mínimo" />
      {saved && (
        <>
          <select value={filters.status_lead || ""} onChange={(event) => setField("status_lead", event.target.value)}>
            <option value="">Status</option>
            <option value="importado">Importado</option> {/* Adicionado */}
            <option value="novo">Novo</option>
            <option value="abordado">Abordado</option>
            <option value="qualificado">Qualificado</option>
            <option value="descartado">Descartado</option>
          </select>
          <Toggle label="Tem telefone" checked={filters.tem_telefone === "true"} onChange={(checked) => setField("tem_telefone", checked ? "true" : "")} />
          <Toggle label="Tem e-mail" checked={filters.tem_email === "true"} onChange={(checked) => setField("tem_email", checked ? "true" : "")} />
          <Toggle label="Possível WhatsApp" checked={filters.possivel_whatsapp === "true"} onChange={(checked) => setField("possivel_whatsapp", checked ? "true" : "")} />
          <Toggle label="Apenas CNPJ" checked={filters.apenas_cnpj === "true"} onChange={(checked) => setField("apenas_cnpj", checked ? "true" : "")} />
          <Toggle label="Não contatar" checked={filters.nao_contatar === "true"} onChange={(checked) => setField("nao_contatar", checked ? "true" : "")} />
          <input type="date" value={filters.data_cadastro || ""} onChange={(event) => setField("data_cadastro", event.target.value)} />
        </>
      )}
    </div>
  );
}

export function Toggle({ label, checked, onChange }) {
  return (
    <label className="toggle">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      {label}
    </label>
  );
}
