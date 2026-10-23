import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowUpRight,
  Search,
  Sparkles,
  ScanLine,
  Check,
  Globe2,
  ChartNoAxesCombined,
  ListChecks,
} from "lucide-react";
import { Brand } from "../components/UI";
import { useAuth } from "../contexts/AuthContext";
export default function Home() {
  const { user } = useAuth();
  const start = user ? "/dashboard" : "/login?mode=register";
  return (
    <div className="marketing">
      <nav className="marketing-nav">
        <Brand />
        <div className="marketing-links">
          <a href="#features">Platform</a>
          <a href="#workflow">How it works</a>
        </div>
        <div className="flex items-center gap-5">
          <Link className="login-link" to={user ? "/dashboard" : "/login"}>
            {user ? "Dashboard" : "Log in"}
          </Link>
          <Link className="button button-dark" to={start}>
            Get started <ArrowUpRight size={16} />
          </Link>
        </div>
      </nav>
      <main id="main-content">
        <section className="hero">
          <div className="hero-copy">
            <div className="hero-badge">
              <span className="status-dot" /> Built for the next era of search
            </div>
            <h1>
              Be found.
              <br />
              Be the <span>answer.</span>
            </h1>
            <p>
              Search is changing. Make your website easier to discover in search
              engines and easier to understand by AI.
            </p>
            <div className="hero-actions">
              <Link className="button button-dark" to={start}>
                Find your opportunities <ArrowRight size={18} />
              </Link>
              <a href="#workflow" className="text-link">
                See how it works <ArrowUpRight size={16} />
              </a>
            </div>
            <div className="hero-notes">
              <span>
                <Check size={15} /> SEO + GEO in one workspace
              </span>
              <span>
                <Check size={15} /> Actionable page insights
              </span>
            </div>
          </div>
          <div className="hero-visual" aria-label="Illustrative audit preview">
            <div className="preview-window">
              <div className="preview-toolbar">
                <span className="flex gap-1.5">
                  <i />
                  <i />
                  <i />
                </span>
                <span>Website visibility / Overview</span>
                <span className="preview-label">EXAMPLE</span>
              </div>
              <div className="preview-body">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="eyebrow">YOUR NEXT OPPORTUNITY</p>
                    <h3>A clearer path to visibility.</h3>
                  </div>
                  <span className="preview-orbit">
                    <Globe2 size={24} />
                  </span>
                </div>
                <div className="preview-scores">
                  <div>
                    <span>Search readiness</span>
                    <strong>
                      84<small>/100</small>
                    </strong>
                    <div className="preview-bar">
                      <i style={{ width: "84%" }} />
                    </div>
                    <p>SEO score</p>
                  </div>
                  <div>
                    <span>AI readiness</span>
                    <strong>
                      72<small>/100</small>
                    </strong>
                    <div className="preview-bar mint">
                      <i style={{ width: "72%" }} />
                    </div>
                    <p>GEO score</p>
                  </div>
                </div>
                <div className="preview-chart">
                  <div className="flex justify-between">
                    <strong>Small changes. Clear progress.</strong>
                    <span>Illustrative data</span>
                  </div>
                  <svg
                    viewBox="0 0 420 100"
                    role="img"
                    aria-label="Illustrative upward score trend"
                  >
                    <defs>
                      <linearGradient
                        id="chart-fill"
                        x1="0"
                        x2="0"
                        y1="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor="#52d6b0"
                          stopOpacity=".25"
                        />
                        <stop
                          offset="100%"
                          stopColor="#52d6b0"
                          stopOpacity="0"
                        />
                      </linearGradient>
                    </defs>
                    <path
                      d="M0 85 L60 73 L120 78 L180 45 L240 52 L300 28 L360 34 L420 8 L420 100 L0 100Z"
                      fill="url(#chart-fill)"
                    />
                    <path
                      d="M0 85 L60 73 L120 78 L180 45 L240 52 L300 28 L360 34 L420 8"
                      fill="none"
                      stroke="#45b997"
                      strokeWidth="3"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <div className="preview-finding">
                  <span>
                    <Sparkles size={18} />
                  </span>
                  <div>
                    <strong>Make your content answer-ready</strong>
                    <p>Add clear answers and structured page information.</p>
                  </div>
                  <ArrowUpRight size={18} />
                </div>
              </div>
            </div>
            <div className="floating-note">
              <span>
                <Check size={18} />
              </span>
              <div>
                Less guesswork.<strong>More direction.</strong>
              </div>
            </div>
          </div>
        </section>
        <div className="platform-strip">
          <span>ONE WORKSPACE. A WIDER VIEW.</span>
          <strong>
            Traditional search <Search size={18} />
          </strong>
          <span className="strip-plus">+</span>
          <strong>
            AI answer engines <Sparkles size={18} />
          </strong>
          <span className="strip-end">Built to help you improve both.</span>
        </div>
        <section id="features" className="feature-section">
          <div className="section-intro">
            <p className="eyebrow">FROM INSIGHT TO ACTION</p>
            <h2>
              Know what’s working.
              <br />
              See what’s next.
            </h2>
            <p>
              Connect the dots between your content, search performance, and AI
              readiness.
            </p>
          </div>
          <div className="feature-grid">
            {[
              {
                icon: ScanLine,
                tag: "01 / DIAGNOSE",
                title: "See the full picture.",
                text: "Audit titles, metadata, content, and page structure. Get separate SEO and GEO scores with concrete recommendations.",
              },
              {
                icon: ChartNoAxesCombined,
                tag: "02 / TRACK",
                title: "Keep progress in view.",
                text: "Compare repeat audits, organize your keyword watchlist, and see how your page scores change over time.",
              },
              {
                icon: ListChecks,
                tag: "03 / IMPROVE",
                title: "Make your next move.",
                text: "Work through recommendations and generate draft titles, descriptions, FAQs, and structured data with AI.",
              },
            ].map(({ icon: Icon, tag, title, text }) => (
              <article className="feature-card" key={tag}>
                <Icon size={27} />
                <p className="eyebrow">{tag}</p>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>
        <section id="workflow" className="workflow-section">
          <div>
            <p className="eyebrow">A SIMPLE WAY FORWARD</p>
            <h2>
              Your website.
              <br />
              Your next chapter.
            </h2>
            <Link className="button button-mint" to={start}>
              Start your first audit <ArrowRight size={18} />
            </Link>
          </div>
          <ol>
            {[
              [
                "Add your website",
                "Enter a public page URL. We’ll examine its content and structure.",
              ],
              [
                "Understand the gaps",
                "Review your SEO and GEO scores, page details, and recommended improvements.",
              ],
              [
                "Improve, then measure",
                "Create a plan, update your website, and run another audit to compare results.",
              ],
            ].map(([title, text], index) => (
              <li key={title}>
                <span>0{index + 1}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      </main>
      <footer className="marketing-footer">
        <Brand />
        <p>Better content. Greater discoverability.</p>
        <span>© {new Date().getFullYear()} SEO/GEO AI</span>
      </footer>
    </div>
  );
}
