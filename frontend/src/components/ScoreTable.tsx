import type { EvaluationMetric } from "../types";

interface ScoreTableProps {
  metrics: EvaluationMetric[];
}

function formatValue(value: number | null, metric: string) {
  if (value === null || value === undefined) return "Not evaluated";
  if (metric.toLowerCase().includes("time")) return `${value.toFixed(2)}s`;
  if (metric.toLowerCase().includes("hallucination")) return `${value.toFixed(1)}%`;
  return value.toFixed(1);
}

export function ScoreTable({ metrics }: ScoreTableProps) {
  if (!metrics.length) {
    return (
      <div className="emptyState">
        <strong>Performance Evaluation</strong>
        <span>Not evaluated yet.</span>
      </div>
    );
  }

  return (
    <div className="tableWrap">
      <table className="dataTable">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Single-Agent</th>
            <th>Multi-Agent</th>
            <th>Difference</th>
            <th>Better</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric) => (
            <tr key={metric.metric}>
              <td>
                <strong>{metric.metric}</strong>
                <small>{metric.estimated ? "Estimated" : "Measured"}</small>
              </td>
              <td>{formatValue(metric.single_agent, metric.metric)}</td>
              <td>{formatValue(metric.multi_agent, metric.metric)}</td>
              <td>
                {metric.difference === null || metric.difference === undefined
                  ? "Not evaluated"
                  : metric.difference.toFixed(2)}
              </td>
              <td>{metric.better_architecture}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

