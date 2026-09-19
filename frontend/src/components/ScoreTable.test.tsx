import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreTable } from "./ScoreTable";

describe("ScoreTable", () => {
  it("renders comparison rows", () => {
    render(
      <ScoreTable
        metrics={[
          {
            metric: "Accuracy",
            single_agent: 80,
            multi_agent: 90,
            difference: 10,
            better_architecture: "Multi-Agent",
            higher_is_better: true,
            methodology: "Reference comparison",
            estimated: false
          }
        ]}
      />
    );

    expect(screen.getByText("Accuracy")).toBeInTheDocument();
    expect(screen.getAllByText("Multi-Agent").length).toBeGreaterThan(0);
  });

  it("renders the not evaluated state", () => {
    render(<ScoreTable metrics={[]} />);
    expect(screen.getByText("Not evaluated yet.")).toBeInTheDocument();
  });
});
