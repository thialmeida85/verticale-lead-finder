import { useEffect, useState } from "react";

import { getImportJob, importCsv, importPdf } from "../api";

const finishedStatuses = new Set(["concluido", "pausado_limite_api", "erro"]);

export default function Importar() {
  const [csvFile, setCsvFile] = useState(null);
  const [pdfFile, setPdfFile] = useState(null);
  const [status, setStatus] = useState("");
  const [csvResult, setCsvResult] = useState(null);
  const [pdfJob, setPdfJob] = useState(null);

  useEffect(() => {
    if (!pdfJob?.id || finishedStatuses.has(pdfJob.status)) return undefined;

    const timer = window.setInterval(async () => {
      try {
        setPdfJob(await getImportJob(pdfJob.id));
      } catch (error) {
        setStatus(error.message);
      }
    }, 2500);

    return () => window.clearInterval(timer);
  }, [pdfJob]);

  async function handleCsvSubmit(event) {
    event.preventDefault();
    if (!csvFile) {
      setStatus("Selecione um arquivo CSV.");
      return;
    }

    setStatus("Importando CSV...");
    setCsvResult(null);
    try {
      const data = await importCsv(csvFile);
      setCsvResult(data);
      setStatus("Importação CSV concluída.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function handlePdfSubmit(event) {
    event.preventDefault();
    if (!pdfFile) {
      setStatus("Selecione um arquivo PDF.");
      return;
    }

    setStatus("Extraindo CNPJs do PDF e iniciando enriquecimento...");
    setPdfJob(null);
    try {
      const data = await importPdf(pdfFile);
      setPdfJob(data);
      setStatus("Importação PDF iniciada.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <h1>Importar leads</h1>
        <p>Suba listas em CSV ou PDFs com CNPJs para criar leads e enriquecer dados.</p>
      </header>

      <div className="import-grid">
        <form className="panel import-card" onSubmit={handleCsvSubmit}>
          <h2>Importar CSV</h2>
          <input type="file" accept=".csv,.emprescsv,text/csv" onChange={(event) => setCsvFile(event.target.files?.[0] || null)} />
          <button type="submit">Importar CSV</button>
          <p className="status">
            Colunas aceitas: cnpj, razao_social, nome_fantasia, cidade, uf, telefone, email,
            segmento, cnae, cnae_descricao, porte, situacao, observacoes e tags.
          </p>
        </form>

        <form className="panel import-card" onSubmit={handlePdfSubmit}>
          <h2>Importar de PDF</h2>
          <input type="file" accept=".pdf,application/pdf" onChange={(event) => setPdfFile(event.target.files?.[0] || null)} />
          <button type="submit">Importar PDF</button>
          <p className="status">
            O sistema extrai apenas CNPJs válidos, cria leads provisórios e consulta a API um por um.
          </p>
        </form>
      </div>

      {status && <p className="status">{status}</p>}

      {csvResult && (
        <ResultPanel
          title="Resultado do CSV"
          metrics={[
            ["Importados", csvResult.importados],
            ["Atualizados", csvResult.atualizados],
            ["Ignorados", csvResult.ignorados],
          ]}
          errors={csvResult.erros}
        />
      )}

      {pdfJob && (
        <ResultPanel
          title="Andamento do PDF"
          metrics={[
            ["Status", labelStatus(pdfJob.status)],
            ["CNPJs", pdfJob.total],
            ["Processados", pdfJob.processados],
            ["Criados", pdfJob.importados],
            ["Já existiam", pdfJob.atualizados],
            ["Enriquecidos", pdfJob.enriquecidos],
            ["Ignorados", pdfJob.ignorados],
          ]}
          errors={pdfJob.erros || []}
        />
      )}
    </section>
  );
}

function ResultPanel({ title, metrics, errors }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      <div className="metrics-grid import-metrics">
        {metrics.map(([label, value]) => (
          <Metric key={label} label={label} value={value} />
        ))}
      </div>
      {!!errors.length && (
        <div className="table-wrap import-errors">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Erro</th>
              </tr>
            </thead>
            <tbody>
              {errors.map((error, index) => (
                <tr key={`${error.linha || error.cnpj || "erro"}-${index}`}>
                  <td>{error.linha || error.cnpj || "-"}</td>
                  <td>{error.erro}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
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
