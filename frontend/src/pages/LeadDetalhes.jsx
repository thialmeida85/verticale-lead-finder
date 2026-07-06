import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getLead, updateLead } from "../api";
import ScoreBadge from "../components/ScoreBadge";

const detailFields = [
  ["CNPJ", "cnpj"],
  ["Razão social", "razao_social"],
  ["Nome fantasia", "nome_fantasia"],
  ["Situação cadastral", "situacao_cadastral"],
  ["Data de abertura", "data_abertura"],
  ["Natureza jurídica", "natureza_juridica"],
  ["Porte", "porte"],
  ["Capital social", "capital_social"],
  ["Matriz ou filial", "matriz_filial"],
  ["CNAE principal", "cnae_principal"],
  ["Descrição do CNAE", "cnae_descricao"],
  ["CNAEs secundários", "cnaes_secundarios"],
  ["Telefone 1", "telefone_1"],
  ["Telefone 2", "telefone_2"],
  ["Telefone principal", "telefone_principal"],
  ["E-mail", "email"],
  ["CEP", "cep"],
  ["Logradouro", "logradouro"],
  ["Número", "numero"],
  ["Complemento", "complemento"],
  ["Bairro", "bairro"],
  ["Cidade", "cidade"],
  ["UF", "uf"],
  ["Status", "status_lead"],
  ["Tags", "tags"],
  ["Observações", "observacoes"],
  ["Fonte dos dados", "fonte"],
  ["Data da consulta", "data_consulta"],
];

export default function LeadDetalhes() {
  const { id } = useParams();
  const [lead, setLead] = useState(null);
  const [status, setStatus] = useState("Carregando...");
  const [form, setForm] = useState({ status_lead: "", tags: "", observacoes: "", nao_contatar: false });

  async function load() {
    const data = await getLead(id);
    setLead(data);
    setForm({
      status_lead: data.status_lead || "novo",
      tags: Array.isArray(data.tags) ? data.tags.join(", ") : data.tags || "",
      observacoes: data.observacoes || "",
      nao_contatar: data.nao_contatar,
    });
    setStatus("");
  }

  useEffect(() => {
    load().catch((error) => setStatus(error.message));
  }, [id]);

  async function handleSave() {
    setStatus("Salvando alterações...");
    try {
      await updateLead(id, {
        ...form,
        tags: form.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
      });
      await load();
    } catch (error) {
      setStatus(error.message);
    }
  }

  if (status && !lead) return <p className="status">{status}</p>;

  return (
    <section className="page">
      <Link to="/leads" className="back-link">Voltar</Link>
      <header className="page-header lead-title">
        <div>
          <h1>{lead.nome_fantasia || lead.razao_social}</h1>
          <p>{lead.cnae_descricao}</p>
        </div>
        <ScoreBadge score={lead.score} />
      </header>
      <div className="panel edit-panel">
        <select value={form.status_lead} onChange={(event) => setForm({ ...form, status_lead: event.target.value })}>
          <option value="novo">Novo</option>
          <option value="abordado">Abordado</option>
          <option value="qualificado">Qualificado</option>
          <option value="descartado">Descartado</option>
        </select>
        <input value={form.tags} onChange={(event) => setForm({ ...form, tags: event.target.value })} placeholder="Tags" />
        <label className="toggle">
          <input type="checkbox" checked={form.nao_contatar} onChange={(event) => setForm({ ...form, nao_contatar: event.target.checked })} />
          Não contatar
        </label>
        <textarea value={form.observacoes} onChange={(event) => setForm({ ...form, observacoes: event.target.value })} placeholder="Observações" />
        <button type="button" onClick={handleSave}>Salvar alterações</button>
      </div>
      {status && <p className="status">{status}</p>}
      <div className="panel">
        <dl className="details-grid">
          {detailFields.map(([label, key]) => (
            <div key={key}>
              <dt>{label}</dt>
              <dd>{Array.isArray(lead[key]) ? JSON.stringify(lead[key]) : String(lead[key] ?? "-")}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
