import { Eye, Search, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import type { ExperimentListItem } from "../types";

interface HistoryProps {
  onOpenExperiment: (id: string) => void;
}

function fmt(value: number | null | undefined, suffix = "") {
  return value === null || value === undefined ? "Not evaluated" : `${value.toFixed(1)}${suffix}`;
}

export function History({ onOpenExperiment }: HistoryProps) {
  const [items, setItems] = useState<ExperimentListItem[]>([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"date" | "single" | "multi">("date");
  const [error, setError] = useState("");

  async function load(query = "") {
    try {
      setItems(await api.listExperiments(query));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load history.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(search);
  }

  async function remove(id: string) {
    try {
      await api.deleteExperiment(id);
      setItems((current) => current.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed.");
    }
  }

  const sorted = useMemo(() => {
    return items.slice().sort((a, b) => {
      if (sortBy === "single") return (b.single_score ?? -1) - (a.single_score ?? -1);
      if (sortBy === "multi") return (b.multi_score ?? -1) - (a.multi_score ?? -1);
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [items, sortBy]);

  return (
    <main className="pageShell">
      <header className="pageHeader splitHeader">
        <div>
          <p className="eyebrow">Experiment History</p>
          <h1>Saved Experiments</h1>
          <p>Review previous comparisons and reopen detailed results.</p>
        </div>
        <form className="searchForm" onSubmit={submit}>
          <Search size={17} />
          <input
            aria-label="Search experiments"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search prompt"
          />
        </form>
      </header>

      {error ? <div className="alert danger">{error}</div> : null}

      <div className="toolbar">
        <label>
          <span>Sort</span>
          <select value={sortBy} onChange={(event) => setSortBy(event.target.value as typeof sortBy)}>
            <option value="date">Date</option>
            <option value="single">Single-Agent score</option>
            <option value="multi">Multi-Agent score</option>
          </select>
        </label>
      </div>

      <section className="contentSection">
        {sorted.length === 0 ? (
          <div className="emptyState wide">
            <strong>No experiment history</strong>
            <span>Saved comparisons will appear here.</span>
          </div>
        ) : (
          <div className="tableWrap">
            <table className="dataTable">
              <thead>
                <tr>
                  <th>Experiment</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Single score</th>
                  <th>Multi score</th>
                  <th>Winner</th>
                  <th>Time</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.prompt}</strong>
                      <small>{new Date(item.created_at).toLocaleString()}</small>
                    </td>
                    <td>{item.task_category}</td>
                    <td>
                      <StatusBadge status={item.status} />
                    </td>
                    <td>{fmt(item.single_score)}</td>
                    <td>{fmt(item.multi_score)}</td>
                    <td>{item.winner ?? "Not evaluated"}</td>
                    <td>
                      {fmt(item.single_execution_time, "s")} / {fmt(item.multi_execution_time, "s")}
                    </td>
                    <td>
                      <div className="rowActions">
                        <button
                          className="iconButton"
                          type="button"
                          onClick={() => onOpenExperiment(item.id)}
                          title="View details"
                          aria-label={`View ${item.id}`}
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          className="iconButton danger"
                          type="button"
                          onClick={() => remove(item.id)}
                          title="Delete experiment"
                          aria-label={`Delete ${item.id}`}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

