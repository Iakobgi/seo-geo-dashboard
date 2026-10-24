import type { ReactNode } from "react";
import { Check, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { Brand } from "./UI";
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="auth-page">
      <aside className="auth-story">
        <Brand light />
        <div className="auth-story-copy">
          <p className="eyebrow">SEO & GEO WORKSPACE</p>
          <h2>
            Website audits.
            <br />
            <span>SEO &amp; GEO analysis.</span>
          </h2>
          <p>
            Review page content, search metadata, and AI readiness in one
            workspace.
          </p>
          {[
            "Understand your SEO & AI readiness",
            "Turn findings into actionable improvements",
            "Measure your progress, one audit at a time",
          ].map((text) => (
            <div className="auth-benefit" key={text}>
              <Check size={17} />
              {text}
            </div>
          ))}
        </div>
        <p className="auth-story-footer">
          SEO/GEO AI · Website analysis and recommendations
        </p>
      </aside>
      <main id="main-content" className="auth-form-side">
        <div className="auth-card">
          <div className="auth-mobile-brand">
            <Brand />
          </div>
          {children}
          <Link className="auth-back" to="/">
            <ArrowLeft size={14} /> Back to home
          </Link>
        </div>
      </main>
    </div>
  );
}
