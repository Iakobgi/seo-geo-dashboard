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
          <p className="eyebrow">YOUR NEXT ADVANTAGE</p>
          <h2>
            Great content
            <br />
            deserves to
            <br />
            be <em>discovered.</em>
          </h2>
          <p>
            A clearer view of your search visibility. A smarter way to decide
            what comes next.
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
          SEO/GEO AI · Built for the next era of search
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
