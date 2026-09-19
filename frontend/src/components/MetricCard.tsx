import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  detail?: string;
  icon: LucideIcon;
}

export function MetricCard({ label, value, detail, icon: Icon }: MetricCardProps) {
  return (
    <article className="metricCard">
      <div className="metricIcon" aria-hidden="true">
        <Icon size={20} />
      </div>
      <div>
        <p className="eyebrow">{label}</p>
        <strong>{value}</strong>
        {detail ? <span>{detail}</span> : null}
      </div>
    </article>
  );
}

