import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Dashboard } from "./Dashboard";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  LineChart: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CartesianGrid: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  Bar: () => <div />,
  Line: () => <div />
}));

vi.mock("../api/client", () => ({
  api: {
    dashboardSummary: vi.fn(),
    dashboardMetrics: vi.fn()
  }
}));

import { api } from "../api/client";

describe("Dashboard", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders dashboard summary", async () => {
    vi.mocked(api.dashboardSummary).mockResolvedValue({
      total_experiments: 0,
      completed_experiments: 0,
      single_agent_average_score: null,
      multi_agent_average_score: null,
      average_single_execution_time: null,
      average_multi_execution_time: null,
      average_accuracy_single: null,
      average_accuracy_multi: null,
      average_quality_single: null,
      average_quality_multi: null,
      average_hallucination_single: null,
      average_hallucination_multi: null,
      average_completeness_single: null,
      average_completeness_multi: null,
      multi_agent_improvement_percentage: null
    });
    vi.mocked(api.dashboardMetrics).mockResolvedValue([]);

    render(<Dashboard />);
    expect(screen.getByText("Single-Agent vs Multi-Agent LLM Performance")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("No experiments yet")).toBeInTheDocument());
  });

  it("renders API errors", async () => {
    vi.mocked(api.dashboardSummary).mockRejectedValue(new Error("Backend unavailable"));
    vi.mocked(api.dashboardMetrics).mockResolvedValue([]);

    render(<Dashboard />);
    await waitFor(() => expect(screen.getByText("Backend unavailable")).toBeInTheDocument());
  });
});
