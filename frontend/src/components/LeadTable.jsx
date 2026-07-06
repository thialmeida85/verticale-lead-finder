import { Link } from "react-router-dom";

import ScoreBadge from "./ScoreBadge";

export default function LeadTable({ leads, onSave, onUpdate, onDelete, mode = "saved" }) {
  if (!leads.length) return <p className="status">Nenhum lead encontrado.</p>;

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>CNPJ</th>
            <th>Empresa</th>
            <th>Cidade</th>
            <th>CNAE</th>
            <th>Contato</th>
            <th>Porte</th>
            <th>Situação</th>
            <th>Tipo</th>
            <th>Score</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id || lead.cnpj}>
              <td>{lead.cnpj}</td>
              <td>
                {lead.id ? <Link to={`/leads/${lead.id}`}>{lead.razao_social}</Link> : <strong>{lead.razao_social}</strong>}
                <span>{lead.nome_fantasia || "-"}</span>
              </td>
              <td>{lead.cidade || "-"} / {lead.uf || "-"}</td>
              <td>
                <strong>{lead.cnae_principal || "-"}</strong>
                <span>{lead.cnae_descricao || "-"}</span>
              </td>
              <td>
                <strong>{lead.telefone_principal || "-"}</strong>
                <span>{lead.email || "-"}</span>
              </td>
              <td>{lead.porte || "-"}</td>
              <td>{lead.situacao_cadastral || "-"}</td>
              <td>{lead.matriz_filial || "-"}</td>
              <td><ScoreBadge score={lead.score} /></td>
              <td>
                <div className="row-actions">
                  {mode === "search" && <button type="button" onClick={() => onSave(lead)}>Salvar</button>}
                  {lead.id && <Link className="button-link" to={`/leads/${lead.id}`}>Detalhes</Link>}
                  {mode === "saved" && (
                    <>
                      <select value={lead.status_lead || "novo"} onChange={(event) => onUpdate(lead.id, { status_lead: event.target.value })}>
                        <option value="novo">Novo</option>
                        <option value="abordado">Abordado</option>
                        <option value="qualificado">Qualificado</option>
                        <option value="descartado">Descartado</option>
                      </select>
                      <button type="button" onClick={() => onUpdate(lead.id, { nao_contatar: !lead.nao_contatar })}>
                        {lead.nao_contatar ? "Liberar" : "Não contatar"}
                      </button>
                      <button type="button" className="danger" onClick={() => onDelete(lead.id)}>Excluir</button>
                    </>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
