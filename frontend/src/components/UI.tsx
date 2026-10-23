import { AlertCircle, ArrowUpRight, Loader2, Orbit } from "lucide-react";
import { Link } from "react-router-dom";
import type { ReactNode } from "react";
export function Brand({ light = false }: { light?: boolean }) {
  return (
    <Link to="/" className={`brand ${light ? "brand-light" : ""}`}>
      <span className="brand-mark">
        <Orbit size={23} />
      </span>
      SEO<span className="brand-slash">/</span>GEO
      <span className="brand-ai">AI</span>
    </Link>
  );
}
export function PageHeading({
  eyebrow = "YOUR WORKSPACE",
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="muted">{description}</p>
      </div>
      {action}
    </div>
  );
}
export function Loading() {
  return (
    <div className="loading-state" role="status">
      <Loader2 className="animate-spin" size={24} />
      <span>Loading your workspace…</span>
    </div>
  );
}
export function Notice({
  children,
  retry,
}: {
  children: ReactNode;
  retry?: () => void;
}) {
  return (
    <div className="notice" role="alert">
      <AlertCircle size={18} className="shrink-0" />
      <span>{children}</span>
      {retry && <button onClick={retry}>Try again</button>}
    </div>
  );
}
export function Empty({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <ArrowUpRight size={24} />
      </span>
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
