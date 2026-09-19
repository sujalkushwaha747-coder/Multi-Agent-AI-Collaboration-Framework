export type TaskCategory = "academic" | "technical" | "general";

export interface DocumentRecord {
  id: string;
  original_filename: string;
  content_type: string | null;
  file_extension: string;
  file_size: number;
  status: string;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
  indexed_at: string | null;
}

export interface RetrievedChunk {
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  text: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface AgentRun {
  id: string;
  agent_name: string;
  sequence: number;
  status: string;
  duration_seconds: number | null;
  summary: string | null;
  output: string | null;
  metadata_json: Record<string, unknown>;
  error_message: string | null;
  created_at: string;
}

export interface AgentResult {
  id: string;
  response: string;
  status: string;
  execution_time_seconds: number | null;
  model_name: string | null;
  retrieval_context: RetrievedChunk[];
  metadata_json: Record<string, unknown>;
  error_message: string | null;
  created_at: string;
}

export interface MultiAgentResult extends AgentResult {
  revision_attempts: number;
}

export interface EvaluationMetric {
  metric: string;
  single_agent: number | null;
  multi_agent: number | null;
  difference: number | null;
  better_architecture: "Single-Agent" | "Multi-Agent" | "Tie" | "Not evaluated";
  higher_is_better: boolean;
  methodology: string;
  estimated: boolean;
  improvement_percentage?: number | null;
}

export interface EvaluationResult {
  id: string;
  status: string;
  accuracy_single: number | null;
  accuracy_multi: number | null;
  quality_single: number | null;
  quality_multi: number | null;
  hallucination_single: number | null;
  hallucination_multi: number | null;
  completeness_single: number | null;
  completeness_multi: number | null;
  overall_single: number | null;
  overall_multi: number | null;
  winner: string | null;
  methodology: Record<string, unknown>;
  metrics: EvaluationMetric[];
  error_message: string | null;
  created_at: string;
}

export interface Experiment {
  id: string;
  prompt: string;
  task_category: TaskCategory;
  reference_answer: string | null;
  document_ids: string[];
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  single_result: AgentResult | null;
  multi_result: MultiAgentResult | null;
  evaluation: EvaluationResult | null;
  agent_runs: AgentRun[];
}

export interface ExperimentListItem {
  id: string;
  prompt: string;
  task_category: TaskCategory;
  status: string;
  created_at: string;
  single_score: number | null;
  multi_score: number | null;
  winner: string | null;
  single_execution_time: number | null;
  multi_execution_time: number | null;
}

export interface DashboardSummary {
  total_experiments: number;
  completed_experiments: number;
  single_agent_average_score: number | null;
  multi_agent_average_score: number | null;
  average_single_execution_time: number | null;
  average_multi_execution_time: number | null;
  average_accuracy_single: number | null;
  average_accuracy_multi: number | null;
  average_quality_single: number | null;
  average_quality_multi: number | null;
  average_hallucination_single: number | null;
  average_hallucination_multi: number | null;
  average_completeness_single: number | null;
  average_completeness_multi: number | null;
  multi_agent_improvement_percentage: number | null;
}

export interface DashboardMetricPoint {
  experiment_id: string;
  created_at: string;
  task_category: TaskCategory;
  accuracy_single: number | null;
  accuracy_multi: number | null;
  quality_single: number | null;
  quality_multi: number | null;
  completeness_single: number | null;
  completeness_multi: number | null;
  hallucination_single: number | null;
  hallucination_multi: number | null;
  execution_time_single: number | null;
  execution_time_multi: number | null;
  overall_single: number | null;
  overall_multi: number | null;
}

