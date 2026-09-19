interface StatusBadgeProps {
  status: string | null | undefined;
}

const toneByStatus: Record<string, string> = {
  completed: "statusBadge success",
  indexed: "statusBadge success",
  failed: "statusBadge danger",
  partial: "statusBadge warning",
  running: "statusBadge info",
  running_single: "statusBadge info",
  running_multi: "statusBadge info",
  uploaded: "statusBadge neutral"
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const label = status || "not evaluated";
  return <span className={toneByStatus[label] || "statusBadge neutral"}>{label.replaceAll("_", " ")}</span>;
}

