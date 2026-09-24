import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AgentTimeline } from "./AgentTimeline";
import type { AgentRun } from "../types";

function run(id: string, agent_name: string, sequence: number): AgentRun {
  return {
    id,
    agent_name,
    sequence,
    status: "completed",
    duration_seconds: 1.25,
    summary: "Completed",
    output: null,
    metadata_json: {},
    error_message: null,
    created_at: "2026-09-24T00:00:00Z"
  };
}

describe("AgentTimeline", () => {
  it("labels repeated writer and reviewer stages clearly", () => {
    render(
      <AgentTimeline
        runs={[
          run("research", "Research Agent", 1),
          run("planner", "Planner Agent", 2),
          run("writer-1", "Writer Agent", 3),
          run("reviewer-1", "Reviewer Agent", 4),
          run("writer-2", "Writer Agent", 5),
          run("reviewer-2", "Reviewer Agent", 6),
          run("verifier", "Verifier Agent", 7)
        ]}
      />
    );

    expect(screen.getByText("Initial Draft")).toBeInTheDocument();
    expect(screen.getByText("First Review")).toBeInTheDocument();
    expect(screen.getByText("Revised Draft")).toBeInTheDocument();
    expect(screen.getByText("Final Review")).toBeInTheDocument();
  });
});
