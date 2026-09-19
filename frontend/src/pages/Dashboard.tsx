import { Activity, Clock, FlaskConical, Gauge } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { api } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import type { DashboardMetricPoint, DashboardSummary } from "../types";

function fmt(value: number | null | undefined, suffix = "") {
  return value === null || value === undefined ? "Not evaluated" : `${value.toFixed(1)}${suffix}`;
}

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetricPoint[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.dashboardSummary(), api.dashboardMetrics()])
      .then(([summaryData, metricData]) => {
        setSummary(summaryData);
        setMetrics(metricData);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const chartData = useMemo(
    () =>
      metrics.map((item, index) => ({
        name: `#${index + 1}`,
        "Single Accuracy": item.accuracy_single,
        "Multi Accuracy": item.accuracy_multi,
        "Single Quality": item.quality_single,
        "Multi Quality": item.quality_multi,
        "Single Complete": item.completeness_single,
        "Multi Complete": item.completeness_multi,
        "Single Hallucination": item.hallucination_single,
        "Multi Hallucination": item.hallucination_multi,
        "Single Time": item.execution_time_single,
        "Multi Time": item.execution_time_multi,
        "Single Overall": item.overall_single,
        "Multi Overall": item.overall_multi
      })),
    [metrics]
  );

  if (error) {
    return (
      <main className="pageShell">
        <div className="alert danger">{error}</div>
      </main>
    );
  }

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <div>
          <p className="eyebrow">Performance Dashboard</p>
          <h1>Single-Agent vs Multi-Agent LLM Performance</h1>
          <p>Compare AI architectures using measurable performance metrics.</p>
        </div>
      </header>

      <section className="metricGrid" aria-label="Dashboard summary">
        <MetricCard
          icon={FlaskConical}
          label="Total experiments"
          value={String(summary?.total_experiments ?? 0)}
          detail={`${summary?.completed_experiments ?? 0} completed`}
        />
        <MetricCard
          icon={Gauge}
          label="Single-Agent average"
          value={fmt(summary?.single_agent_average_score)}
          detail="Overall score"
        />
        <MetricCard
          icon={Activity}
          label="Multi-Agent average"
          value={fmt(summary?.multi_agent_average_score)}
          detail={
            summary?.multi_agent_improvement_percentage === null ||
            summary?.multi_agent_improvement_percentage === undefined
              ? "No aggregate delta"
              : `${summary.multi_agent_improvement_percentage.toFixed(1)}% delta`
          }
        />
        <MetricCard
          icon={Clock}
          label="Average execution time"
          value={`${fmt(summary?.average_single_execution_time, "s")} / ${fmt(
            summary?.average_multi_execution_time,
            "s"
          )}`}
          detail="Single / Multi"
        />
      </section>

      {chartData.length === 0 ? (
        <div className="emptyState wide">
          <strong>No experiments yet</strong>
          <span>Run a comparison to populate the dashboard.</span>
        </div>
      ) : (
        <section className="chartGrid">
          <article className="chartPanel">
            <h2>Accuracy comparison</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Single Accuracy" fill="#2563eb" />
                <Bar dataKey="Multi Accuracy" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </article>

          <article className="chartPanel">
            <h2>Quality and completeness</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="Single Quality" stroke="#2563eb" />
                <Line type="monotone" dataKey="Multi Quality" stroke="#10b981" />
                <Line type="monotone" dataKey="Single Complete" stroke="#f59e0b" />
                <Line type="monotone" dataKey="Multi Complete" stroke="#ef4444" />
              </LineChart>
            </ResponsiveContainer>
          </article>

          <article className="chartPanel">
            <h2>Hallucination rate</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Single Hallucination" fill="#ef4444" />
                <Bar dataKey="Multi Hallucination" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </article>

          <article className="chartPanel">
            <h2>Execution time and overall score</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="Single Time" stroke="#2563eb" />
                <Line type="monotone" dataKey="Multi Time" stroke="#10b981" />
                <Line type="monotone" dataKey="Single Overall" stroke="#7c3aed" />
                <Line type="monotone" dataKey="Multi Overall" stroke="#0891b2" />
              </LineChart>
            </ResponsiveContainer>
          </article>
        </section>
      )}
    </main>
  );
}

