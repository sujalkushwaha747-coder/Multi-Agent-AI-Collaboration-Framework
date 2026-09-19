import { useEffect, useState } from "react";
import { Sidebar, type PageKey } from "./components/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { History } from "./pages/History";
import { KnowledgeBase } from "./pages/KnowledgeBase";
import { Methodology } from "./pages/Methodology";
import { NewExperiment } from "./pages/NewExperiment";
import { Results } from "./pages/Results";
import type { Experiment } from "./types";

function parseHash(): { page: PageKey; id: string | null } {
  const raw = window.location.hash.replace("#", "") || "dashboard";
  const [pageRaw, query] = raw.split("?");
  const allowed: PageKey[] = [
    "dashboard",
    "experiment",
    "results",
    "knowledge",
    "history",
    "methodology"
  ];
  const page = allowed.includes(pageRaw as PageKey) ? (pageRaw as PageKey) : "dashboard";
  const id = new URLSearchParams(query || "").get("id");
  return { page, id };
}

export default function App() {
  const [{ page, id }, setRoute] = useState(parseHash);
  const [activeExperiment, setActiveExperiment] = useState<Experiment | null>(null);

  useEffect(() => {
    const onHashChange = () => setRoute(parseHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  function navigate(nextPage: PageKey, nextId?: string | null) {
    window.location.hash = nextId ? `${nextPage}?id=${nextId}` : nextPage;
    setRoute({ page: nextPage, id: nextId ?? null });
  }

  function onExperimentReady(experiment: Experiment) {
    setActiveExperiment(experiment);
    navigate("results", experiment.id);
  }

  return (
    <div className="appShell">
      <Sidebar active={page} onNavigate={(nextPage) => navigate(nextPage)} />
      <div className="mainSurface">
        {page === "dashboard" ? <Dashboard /> : null}
        {page === "experiment" ? <NewExperiment onExperimentReady={onExperimentReady} /> : null}
        {page === "results" ? (
          <Results experimentId={id} initialExperiment={activeExperiment} />
        ) : null}
        {page === "knowledge" ? <KnowledgeBase /> : null}
        {page === "history" ? (
          <History onOpenExperiment={(experimentId) => navigate("results", experimentId)} />
        ) : null}
        {page === "methodology" ? <Methodology /> : null}
      </div>
    </div>
  );
}

