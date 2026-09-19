import type { AgentRun } from "../types";
import { FormattedResponse } from "./FormattedResponse";
import { StatusBadge } from "./StatusBadge";

interface AgentTimelineProps {
  runs: AgentRun[];
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

  return (
    <div className="timeline">
      {runs
        .slice()
        .sort((a, b) => a.sequence - b.sequence)
        .map((run) => (
          <details key={run.id} className="timelineItem">
            <summary>
              <span className="timelineDot" aria-hidden="true" />
              <strong>{run.agent_name}</strong>
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
        ))}
    </div>
  );
}
