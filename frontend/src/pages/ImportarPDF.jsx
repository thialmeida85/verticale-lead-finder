import { useEffect, useState } from "react";

import { getImportJob, importPdf } from "../api";

const finishedStatuses = new Set(["concluido", "pausado_limite_api", "erro"]);

export default function ImportarPDF() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [job, setJob] = useState(null);
  const isImporting = job?.id && !finishedStatuses.has(job.status);

  useEffect(() => {
    if (!job?.id || finishedStatuses.has(job.status)) return undefined;

    const timer = window.setInterval(async () => {
      try {
        setJob(await getImportJob(job.id));
      } catch (error) {
        setStatus(error.message);
      }
    }, 2500);

    return () => window.clearInterval(timer);
  }, [job]);

  function handleFileChange(event) {
    setFile(event.target.files[0]);
    setStatus("");
    setJob(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setStatus("Por favor, selecione um arquivo PDF.");
      return;
    }

    setStatus("Extraindo CNPJs do PDF e iniciando importação...");
    try {
      const data = await importPdf(file);
      setJob(data);
      setStatus(data.status === "erro" ? "Não foi possível iniciar a importação PDF." : `Importação iniciada: ${data.total} CNPJs encontrados.`);
    } catch (error) {
      setStatus(error.message);
      setJob(null);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Importar Leads de PDF</h1>
      </header>
      <div className="panel">
        <p>
          Faça o upload de um arquivo PDF para extrair CNPJs. Os leads serão pré-cadastrados com o status "Importado" e poderão ser
          enriquecidos posteriormente na tela de "Leads Salvos".
        </p>
        <form onSubmit={handleSubmit} className="form-stack">
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button type="submit" disabled={!file || isImporting}>
            Enviar e Processar
          </button>
        </form>
        {status && <p className="status">{status}</p>}
        {job && (
          <div className="metrics-grid import-metrics">
            <Metric label="Status" value={labelStatus(job.status)} />
            <Metric label="CNPJs encontrados" value={job.total} />
            <Metric label="Processados" value={job.processados} />
            <Metric label="Criados" value={job.importados} />
            <Metric label="Já existiam" value={job.atualizados} />
            <Metric label="Enriquecidos" value={job.enriquecidos} />
            <Metric label="Ignorados" value={job.ignorados} />
            <Metric label="Erros" value={job.erros?.length || 0} />
          </div>
        )}
        {!!job?.erros?.length && (
          <div className="table-wrap import-errors">
            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Erro</th>
                </tr>
              </thead>
              <tbody>
                {job.erros.map((error, index) => (
                  <tr key={`${error.cnpj || error.item || "erro"}-${index}`}>
                    <td>{error.cnpj || error.item || "-"}</td>
                    <td>{error.erro}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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

function labelStatus(status) {
  const labels = {
    pendente: "Pendente",
    processando: "Processando",
    concluido: "Concluído",
    pausado_limite_api: "Pausado por limite",
    erro: "Erro",
  };
  return labels[status] || status;
}
