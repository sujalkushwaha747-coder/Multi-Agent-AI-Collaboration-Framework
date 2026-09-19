import { RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { api } from "../api/client";
import { AgentTimeline } from "../components/AgentTimeline";
import { FormattedResponse } from "../components/FormattedResponse";
import { ScoreTable } from "../components/ScoreTable";
import { StatusBadge } from "../components/StatusBadge";
import type { Experiment } from "../types";

interface ResultsProps {
  experimentId: string | null;
  initialExperiment: Experiment | null;
}

function formatSeconds(value: number | null | undefined) {
  return value === null || value === undefined ? "Not timed" : `${value.toFixed(2)}s`;
}

function formatModelName(value: string | null | undefined) {
  if (!value) {
    return { provider: "Provider not recorded", model: "Model not recorded" };
  }
  const [provider, ...modelParts] = value.split(":");
  if (modelParts.length === 0) {
    return { provider: "Provider not recorded", model: value };
  }
  return {
    provider: provider.charAt(0).toUpperCase() + provider.slice(1),
    model: modelParts.join(":")
  };
}

const liveStatuses = new Set([
  "created",
  "queued",
  "running",
  "running_single",
  "single_completed",
  "running_multi",
  "multi_completed"
]);

export function Results({ experimentId, initialExperiment }: ResultsProps) {
  const [experiment, setExperiment] = useState<Experiment | null>(initialExperiment);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const id = experimentId || initialExperiment?.id || null;

  async function load() {
    if (!id) return;
    setIsRefreshing(true);
    setError("");
    try {
      setExperiment(await api.getExperiment(id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load results.");
    } finally {
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    if (id) {
      load();
    }
  }, [id]);

  useEffect(() => {
    if (!id || !experiment || !liveStatuses.has(experiment.status)) return;
    const timer = window.setInterval(() => {
      load();
    }, 3000);
    return () => window.clearInterval(timer);
  }, [id, experiment?.status]);

  const chartData = useMemo(() => {
    const metrics = experiment?.evaluation?.metrics ?? [];
    return metrics
      .filter((metric) => metric.metric !== "Execution Time")
      .map((metric) => ({
        metric: metric.metric,
        "Single-Agent": metric.single_agent,
        "Multi-Agent": metric.multi_agent
      }));
  }, [experiment]);

  if (!id && !experiment) {
    return (
      <main className="pageShell">
        <div className="emptyState wide">
          <strong>No result selected</strong>
          <span>Run or open an experiment to view detailed results.</span>
        </div>
      </main>
    );
  }

  return (
    <main className="pageShell">
      <header className="pageHeader splitHeader">
        <div>
          <p className="eyebrow">Comparison Result</p>
          <h1>Experiment Results</h1>
          <p>{experiment?.prompt ?? "Loading experiment..."}</p>
        </div>
        <button className="iconTextButton" type="button" onClick={load} disabled={isRefreshing}>
          <RefreshCw size={17} className={isRefreshing ? "spin" : ""} />
          <span>Refresh</span>
        </button>
      </header>

      {error ? <div className="alert danger">{error}</div> : null}

      {experiment && liveStatuses.has(experiment.status) ? (
        <div className="alert info">
          <span>
            Experiment is still running. This page refreshes automatically while the
            selected LLM provider completes the Single-Agent and Multi-Agent workflow.
          </span>
        </div>
      ) : null}

      {experiment ? (
        <>
          <section className="resultGrid">
            <article className="responsePanel">
              <div className="panelTitle">
                <h2>Single-Agent Response</h2>
                <StatusBadge status={experiment.single_result?.status} />
              </div>
              <FormattedResponse
                text={
                  experiment.single_result?.response ||
                  experiment.single_result?.error_message ||
                  "Not evaluated yet."
                }
              />
              <footer>
                <span>{formatSeconds(experiment.single_result?.execution_time_seconds)}</span>
                <span>
                  {formatModelName(experiment.single_result?.model_name).provider} ·{" "}
                  {formatModelName(experiment.single_result?.model_name).model}
                </span>
              </footer>
            </article>

            <article className="responsePanel">
              <div className="panelTitle">
                <h2>Multi-Agent Response</h2>
                <StatusBadge status={experiment.multi_result?.status} />
              </div>
              <FormattedResponse
                text={
                  experiment.multi_result?.response ||
                  experiment.multi_result?.error_message ||
                  "Not evaluated yet."
                }
              />
              <footer>
                <span>{formatSeconds(experiment.multi_result?.execution_time_seconds)}</span>
                <span>
                  {formatModelName(experiment.multi_result?.model_name).provider} ·{" "}
                  {formatModelName(experiment.multi_result?.model_name).model}
                </span>
              </footer>
            </article>
          </section>

          <section className="contentSection">
            <div className="sectionTitle">
              <h2>Performance Evaluation</h2>
              <StatusBadge status={experiment.evaluation?.status} />
            </div>
            <div className="providerSummary">
              <span>
                Single-Agent: {formatModelName(experiment.single_result?.model_name).provider} ·{" "}
                {formatModelName(experiment.single_result?.model_name).model}
              </span>
              <span>
                Multi-Agent: {formatModelName(experiment.multi_result?.model_name).provider} ·{" "}
                {formatModelName(experiment.multi_result?.model_name).model}
              </span>
            </div>
            <ScoreTable metrics={experiment.evaluation?.metrics ?? []} />
          </section>

          {chartData.length ? (
            <section className="chartPanel fullWidth">
              <h2>Overall comparison chart</h2>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Single-Agent" fill="#2563eb" />
                  <Bar dataKey="Multi-Agent" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </section>
          ) : null}

          <section className="contentSection">
            <div className="sectionTitle">
              <h2>Multi-Agent agent workflow</h2>
              <span className="muted">
                {experiment.multi_result?.revision_attempts ?? 0} revision attempts
              </span>
            </div>
            <AgentTimeline runs={experiment.agent_runs} />
          </section>

          <section className="contentSection">
            <h2>Retrieval information</h2>
            <div className="retrievalGrid">
              <div className="retrievalColumn">
                <h3>Single-Agent Context</h3>
                {(experiment.single_result?.retrieval_context ?? []).length ? (
                  (experiment.single_result?.retrieval_context ?? []).map((chunk, index) => (
                    <article key={chunk.chunk_id} className="retrievalItem">
                      <div className="retrievalMeta">
                        <strong>Context {index + 1}</strong>
                        <span>Score {chunk.score.toFixed(4)}</span>
                      </div>
                      <FormattedResponse text={chunk.text} className="retrievalText" />
                    </article>
                  ))
                ) : (
                  <div className="emptyState compact">
                    <strong>No single-agent context</strong>
                    <span>No retrieved chunks were attached to this run.</span>
                  </div>
                )}
              </div>

              <div className="retrievalColumn">
                <h3>Multi-Agent Context</h3>
                {(experiment.multi_result?.retrieval_context ?? []).length ? (
                  (experiment.multi_result?.retrieval_context ?? []).map((chunk, index) => (
                    <article key={`multi-${chunk.chunk_id}`} className="retrievalItem">
                      <div className="retrievalMeta">
                        <strong>Context {index + 1}</strong>
                        <span>Score {chunk.score.toFixed(4)}</span>
                      </div>
                      <FormattedResponse text={chunk.text} className="retrievalText" />
                    </article>
                  ))
                ) : (
                  <div className="emptyState compact">
                    <strong>No multi-agent context</strong>
                    <span>No retrieved chunks were attached to this run.</span>
                  </div>
                )}
              </div>
            </div>
          </section>
        </>
      ) : (
        <div className="emptyState wide">
          <strong>Loading results</strong>
          <span>Please wait.</span>
        </div>
      )}
    </main>
  );
}
