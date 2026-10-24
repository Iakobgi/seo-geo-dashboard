import { useState, useEffect } from "react";
import type { ReactNode } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Network,
  Columns2,
  TextCursorInput,
  Search,
  Tags,
  Sparkles,
  LogOut,
  ListChecks,
  Menu,
  X,
  ArrowUpRight,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { Brand } from "./UI";
const navItems = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/audits", label: "Website audits", icon: Search },
  { to: "/site-crawl", label: "Site crawl", icon: Network },
  { to: "/compare", label: "Compare audits", icon: Columns2 },
  { to: "/snippet", label: "Search snippet", icon: TextCursorInput },
  { to: "/keywords", label: "Keyword tracking", icon: Tags },
  { to: "/recommendations", label: "Recommendations", icon: ListChecks },
  { to: "/agent", label: "AI workspace", icon: Sparkles },
];
export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const location = useLocation();
  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);
  useEffect(() => {
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);
  useEffect(() => {
    if (!open || !window.matchMedia("(max-width: 800px)").matches) return;
    const previous = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    const drawer = document.getElementById("workspace-navigation");
    const controls = () =>
      Array.from(
        drawer?.querySelectorAll<HTMLElement>(
          "a[href], button:not([disabled])",
        ) || [],
      );
    controls()[0]?.focus();
    document.body.style.overflow = "hidden";
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const items = controls();
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    };
    window.addEventListener("keydown", trap);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", trap);
      previous?.focus();
    };
  }, [open]);
  return (
    <div className="app-shell">
      {open && (
        <button
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}
      <aside
        id="workspace-navigation"
        className={`sidebar ${open ? "is-open" : ""}`}
      >
        <div className="sidebar-brand">
          <Brand light />
          <button
            className="mobile-only icon-button"
            aria-label="Close navigation"
            onClick={() => setOpen(false)}
          >
            <X size={20} />
          </button>
        </div>
        <div className="workspace-label">
          <span className="workspace-avatar">W</span>
          <div>
            My workspace<small>SEO & AI visibility</small>
          </div>
          <span className="status-dot" />
        </div>
        <p className="nav-caption">WORKSPACE</p>
        <nav aria-label="Workspace">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-tip">
          <Sparkles size={20} />
          <h3>AI content tools</h3>
          <p>Generate plans, page titles, descriptions, and structured data.</p>
          <Link to="/agent">
            Explore AI tools <ArrowUpRight size={15} />
          </Link>
        </div>
        <div className="sidebar-user">
          <span className="user-avatar">
            {user?.email.charAt(0).toUpperCase()}
          </span>
          <div>
            <strong>Personal account</strong>
            <small title={user?.email}>{user?.email}</small>
          </div>
          <button
            onClick={logout}
            className="icon-button"
            title="Sign out"
            aria-label="Sign out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="workspace-header">
          <div className="flex items-center gap-3">
            <button
              className="mobile-only icon-button"
              aria-label="Open navigation"
              aria-expanded={open}
              aria-controls="workspace-navigation"
              onClick={() => setOpen(true)}
            >
              <Menu size={20} />
            </button>
            <span>
              Workspace <span className="text-gray-300 mx-2">/</span>{" "}
              <strong>
                {navItems.find((item) => item.to === location.pathname)?.label}
              </strong>
            </span>
          </div>
          <Link to="/audits" className="header-link">
            New audit <ArrowUpRight size={15} />
          </Link>
        </header>
        <main id="main-content" className="workspace-content">
          {children}
        </main>
        <footer className="workspace-footer">
          SEO/GEO AI <span>Website audits · SEO & GEO analysis</span>
        </footer>
      </div>
    </div>
  );
}
