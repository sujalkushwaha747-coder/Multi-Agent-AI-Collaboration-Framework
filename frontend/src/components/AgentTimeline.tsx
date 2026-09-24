import type { AgentRun } from "../types";
import { FormattedResponse } from "./FormattedResponse";
import { StatusBadge } from "./StatusBadge";

interface AgentTimelineProps {
  runs: AgentRun[];
}

const attemptLabels: Record<string, string[]> = {
  "Writer Agent": ["Initial Draft", "Revised Draft"],
  "Reviewer Agent": ["First Review", "Final Review"]
};

function stageLabel(run: AgentRun, sortedRuns: AgentRun[]) {
  const labels = attemptLabels[run.agent_name];
  if (!labels) {
    return run.agent_name;
  }

  const sameAgentRuns = sortedRuns.filter((item) => item.agent_name === run.agent_name);
  if (sameAgentRuns.length < 2) {
    return run.agent_name;
  }

  const attemptIndex = sameAgentRuns.findIndex((item) => item.id === run.id);
  return labels[attemptIndex] ?? `${run.agent_name} ${attemptIndex + 1}`;
}

export function AgentTimeline({ runs }: AgentTimelineProps) {
  if (!runs.length) {
    return (
      <div className="emptyState">
        <strong>Agent workflow</strong>
        <span>No multi-agent run has been recorded.</span>
      </div>
    );
  }

  const sortedRuns = runs.slice().sort((a, b) => a.sequence - b.sequence);

  return (
    <div className="timeline">
      {sortedRuns
        .map((run) => {
          const label = stageLabel(run, sortedRuns);

          return (
            <details key={run.id} className="timelineItem">
              <summary>
                <span className="timelineDot" aria-hidden="true" />
                <span className="stageTitle">
                  <strong>{label}</strong>
                  {label !== run.agent_name ? <span>{run.agent_name}</span> : null}
                </span>
                <StatusBadge status={run.status} />
                <span className="duration">
                  {run.duration_seconds === null
                    ? "Not timed"
                    : `${run.duration_seconds.toFixed(2)}s`}
                </span>
              </summary>
              <p>{run.summary}</p>
              {run.output ? <FormattedResponse text={run.output} className="agentOutput" /> : null}
            </details>
          );
        })}
    </div>
  );
}
