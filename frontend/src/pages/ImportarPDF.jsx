import { useState } from "react";

import { importPdf } from "../api";

export default function ImportarPDF() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  function handleFileChange(event) {
    setFile(event.target.files[0]);
    setStatus("");
    setResult(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setStatus("Por favor, selecione um arquivo PDF.");
      return;
    }

    setStatus("Processando PDF, por favor aguarde...");
    try {
      const data = await importPdf(file);
      setResult(data);
      setStatus("Processamento concluído!");
    } catch (error) {
      setStatus(error.message);
      setResult(null);
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
          <button type="submit" disabled={!file || status.includes("Processando")}>
            Enviar e Processar
          </button>
        </form>
        {status && <p className="status">{status}</p>}
        {result && (
          <div className="import-result">
            <p><strong>Novos leads criados:</strong> {result.criados}</p>
            <p><strong>Leads ignorados (CNPJ já existente):</strong> {result.ignorados}</p>
          </div>
        )}
      </div>
    </section>
  );
}