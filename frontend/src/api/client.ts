import type {
  DashboardMetricPoint,
  DashboardSummary,
  DocumentRecord,
  Experiment,
  ExperimentListItem,
  RetrievedChunk,
  TaskCategory
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers
    });
  } catch (error) {
    const message =
      error instanceof TypeError
        ? `Backend is not reachable at ${API_BASE_URL}. Start the FastAPI server and make sure this frontend origin is allowed by CORS.`
        : "Unable to reach the backend API.";
    throw new Error(message);
  }
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      // keep default message
    }
    throw new Error(message);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export interface RunComparisonPayload {
  prompt: string;
  task_category: TaskCategory;
  document_ids: string[];
  reference_answer?: string | null;
}

export const api = {
  dashboardSummary: () => request<DashboardSummary>("/dashboard/summary"),
  dashboardMetrics: () => request<DashboardMetricPoint[]>("/dashboard/metrics"),
  listExperiments: (search = "") =>
    request<ExperimentListItem[]>(
      `/experiments${search ? `?search=${encodeURIComponent(search)}` : ""}`
    ),
  getExperiment: (id: string) => request<Experiment>(`/experiments/${id}`),
  runComparison: (payload: RunComparisonPayload) =>
    request<Experiment>("/experiments/run-comparison", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  queueComparison: (payload: RunComparisonPayload) =>
    request<Experiment>("/experiments/run-comparison-async", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  runExistingComparison: (id: string) =>
    request<Experiment>(`/experiments/${id}/run-both`, {
      method: "POST",
      body: JSON.stringify({})
    }),
  deleteExperiment: (id: string) =>
    request<void>(`/experiments/${id}`, { method: "DELETE" }),
  listDocuments: () => request<DocumentRecord[]>("/documents"),
  uploadDocument: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<DocumentRecord>("/documents/upload", {
      method: "POST",
      body
    });
  },
  indexDocument: (id: string) =>
    request<DocumentRecord>(`/documents/${id}/index`, { method: "POST" }),
  deleteDocument: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),
  searchDocuments: (
    query: string,
    documentIds: string[] = [],
    topK = 5
  ) =>
    request<{ query: string; results: RetrievedChunk[] }>("/documents/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        document_ids: documentIds,
        top_k: topK
      })
    }),
  listBenchmarkPrompts: () =>
    request<Array<{ id: string; category: TaskCategory; prompt: string }>>(
      "/benchmarks/prompts"
    ),
  health: () => request<Record<string, unknown>>("/health")
};
