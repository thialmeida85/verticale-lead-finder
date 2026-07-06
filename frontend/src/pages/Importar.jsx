import { useState } from "react";

import { importCsv } from "../api";

export default function Importar() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setStatus("Selecione um arquivo CSV.");
      return;
    }

    setStatus("Importando arquivo...");
    setResult(null);
    try {
      const data = await importCsv(file);
      setResult(data);
      setStatus("Importação concluída.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Importar CSV</h1>
        <p>Suba uma lista de empresas para salvar leads sem duplicar CNPJ.</p>
      </header>
      <form className="panel import-panel" onSubmit={handleSubmit}>
        <input type="file" accept=".csv,.emprescsv,text/csv" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        <button type="submit">Importar</button>
      </form>
      <div className="panel">
        <h2>Colunas aceitas</h2>
        <p className="status">
          cnpj, razao_social, nome_fantasia, cidade, uf, telefone, email, segmento,
          cnae, cnae_descricao, porte, situacao, observacoes e tags.
        </p>
      </div>
      {status && <p className="status">{status}</p>}
      {result && (
        <div className="panel">
          <h2>Resultado</h2>
          <div className="metrics-grid">
            <Metric label="Importados" value={result.importados} />
            <Metric label="Atualizados" value={result.atualizados} />
            <Metric label="Ignorados" value={result.ignorados} />
          </div>
          {!!result.erros.length && (
            <div className="table-wrap import-errors">
              <table>
                <thead>
                  <tr>
                    <th>Linha</th>
                    <th>Erro</th>
                  </tr>
                </thead>
                <tbody>
                  {result.erros.map((error, index) => (
                    <tr key={`${error.linha}-${index}`}>
                      <td>{error.linha}</td>
                      <td>{error.erro}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
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
