import { AlertCircle, CheckCircle2, Clock } from "lucide-react";
import { useEffect, useState } from "react";
import { api, type RunComparisonPayload } from "../api/client";
import { PromptForm } from "../components/PromptForm";
import type { DocumentRecord, Experiment } from "../types";

interface NewExperimentProps {
  onExperimentReady: (experiment: Experiment) => void;
}

export function NewExperiment({ onExperimentReady }: NewExperimentProps) {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listDocuments()
      .then(setDocuments)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function runComparison(payload: RunComparisonPayload) {
    setIsRunning(true);
    setError("");
    setMessage("Creating experiment and starting background run...");
    try {
      const experiment = await api.queueComparison(payload);
      setMessage("Experiment started. Opening live result view...");
      onExperimentReady(experiment);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed.");
      setMessage("");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <div>
          <p className="eyebrow">New Experiment</p>
          <h1>Run Comparison</h1>
          <p>Both architectures receive the same prompt and are evaluated side by side.</p>
        </div>
      </header>

      {error ? (
        <div className="alert danger">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      ) : null}

      {message ? (
        <div className="alert info">
          {isRunning ? <Clock size={18} /> : <CheckCircle2 size={18} />}
          <span>{message}</span>
        </div>
      ) : null}

      <section className="twoColumn">
        <PromptForm documents={documents} isRunning={isRunning} onSubmit={runComparison} />
        <aside className="methodPanel">
          <h2>Workflow</h2>
          <ol className="plainList">
            <li>Validate prompt</li>
            <li>Create experiment</li>
            <li>Run Single-Agent</li>
            <li>Run Multi-Agent workflow</li>
            <li>Evaluate both outputs</li>
            <li>Store and display results</li>
          </ol>
        </aside>
      </section>
    </main>
  );
}
