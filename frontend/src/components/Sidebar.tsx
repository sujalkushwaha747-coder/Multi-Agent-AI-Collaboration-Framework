import {
  BarChart3,
  BookOpenCheck,
  Database,
  FlaskConical,
  History,
  Info
} from "lucide-react";

export type PageKey =
  | "dashboard"
  | "experiment"
  | "results"
  | "knowledge"
  | "history"
  | "methodology";

interface SidebarProps {
  active: PageKey;
  onNavigate: (page: PageKey) => void;
}

const items = [
  { key: "dashboard", label: "Dashboard", icon: BarChart3 },
  { key: "experiment", label: "New Experiment", icon: FlaskConical },
  { key: "results", label: "Results", icon: BookOpenCheck },
  { key: "knowledge", label: "Knowledge Base", icon: Database },
  { key: "history", label: "History", icon: History },
  { key: "methodology", label: "Methodology", icon: Info }
] as const;

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brandBlock">
        <div className="brandMark">S</div>
        <div>
          <strong>ShodhAI</strong>
          <span>LLM Architecture Lab</span>
        </div>
      </div>
      <nav aria-label="Primary">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              className={active === item.key ? "navItem active" : "navItem"}
              onClick={() => onNavigate(item.key)}
              type="button"
              title={item.label}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

