import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./home-hero.css";
import {
  ArrowRight,
  ArrowUpRight,
  Search,
  Sparkles,
  ScanLine,
  Menu,
  X,
  ChartNoAxesCombined,
  ListChecks,
} from "lucide-react";
import { Brand } from "../components/UI";
import { useAuth } from "../contexts/AuthContext";
export default function Home() {
  const { user } = useAuth();
  const start = user ? "/dashboard" : "/login?mode=register";
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!menuOpen) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
        document.getElementById("home-menu-toggle")?.focus();
      }
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [menuOpen]);

  return (
    <div className="marketing">
      <main id="main-content">
        <section className="film-hero" aria-labelledby="home-hero-title">
          <div className="film-media" aria-hidden="true" />
          <img
            className="film-visual"
            src="/media/website-overview.svg"
            alt="Example website layout with page content, metadata, structured data, and an illustrative audit history graph."
          />
          <div className="film-shade" aria-hidden="true" />
          <nav className="film-nav" aria-label="Main navigation">
            <Brand light />
            <div className="film-nav-links">
              <a href="#features">The platform</a>
              <a href="#workflow">How it works</a>
            </div>
            <div className="film-nav-actions">
              <Link to={user ? "/dashboard" : "/login"}>
                {user ? "Dashboard" : "Log in"}
              </Link>
              <Link className="film-nav-cta" to={start}>
                Get started <ArrowUpRight size={15} />
              </Link>
            </div>
            <button
              id="home-menu-toggle"
              type="button"
              className="film-menu-toggle"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
              aria-controls="home-mobile-menu"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
              <span>{menuOpen ? "Close" : "Menu"}</span>
            </button>
            {menuOpen && (
              <div className="film-mobile-menu" id="home-mobile-menu">
                <a href="#features" onClick={() => setMenuOpen(false)}>
                  The platform <ArrowUpRight size={17} />
                </a>
                <a href="#workflow" onClick={() => setMenuOpen(false)}>
                  How it works <ArrowUpRight size={17} />
                </a>
                <Link to={user ? "/dashboard" : "/login"}>
                  {user ? "Dashboard" : "Log in"}
                  <ArrowUpRight size={17} />
                </Link>
                <Link to={start} className="film-mobile-start">
                  Get started <ArrowRight size={17} />
                </Link>
              </div>
            )}
          </nav>
          <div className="film-content">
            <h1 id="home-hero-title">
              SEO &amp; GEO
              <br />
              <span>Website analysis.</span>
            </h1>
            <p>
              Audit your pages, review SEO and AI readiness scores, and get
              practical recommendations for your website.
            </p>
            <div className="film-actions">
              <Link className="film-button film-button-primary" to={start}>
                Run an audit <ArrowUpRight size={17} />
              </Link>
              <a className="film-button film-button-secondary" href="#features">
                View features <ArrowRight size={17} />
              </a>
            </div>
          </div>
        </section>
        <div className="platform-strip">
          <span>WEBSITE OPTIMIZATION</span>
          <strong>
            Traditional search <Search size={18} />
          </strong>
          <span className="strip-plus">+</span>
          <strong>
            AI answer engines <Sparkles size={18} />
          </strong>
          <span className="strip-end">SEO and GEO in one dashboard.</span>
        </div>
        <section id="features" className="feature-section">
          <div className="section-intro">
            <p className="eyebrow">PLATFORM FEATURES</p>
            <h2>Website audits and recommendations.</h2>
            <p>
              Review page content, track audit scores, and manage improvements
              from one workspace.
            </p>
          </div>
          <div className="feature-grid">
            {[
              {
                icon: ScanLine,
                tag: "01 / DIAGNOSE",
                title: "SEO & GEO audits",
                text: "Audit titles, metadata, content, and page structure. Get separate SEO and GEO scores with concrete recommendations.",
              },
              {
                icon: ChartNoAxesCombined,
                tag: "02 / TRACK",
                title: "Progress tracking",
                text: "Compare repeat audits, organize your keyword watchlist, and see how your page scores change over time.",
              },
              {
                icon: ListChecks,
                tag: "03 / IMPROVE",
                title: "Content recommendations",
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
            <p className="eyebrow">HOW IT WORKS</p>
            <h2>
              Analyze. Improve.
              <br />
              Measure.
            </h2>
            <Link className="button button-mint" to={start}>
              Run an audit <ArrowRight size={18} />
            </Link>
          </div>
          <ol>
            {[
              [
                "Add your website",
                "Enter a public page URL. We’ll examine its content and structure.",
              ],
              [
                "Review the results",
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
        <p>Website audits, SEO and GEO analysis.</p>
        <span>© {new Date().getFullYear()} SEO/GEO AI</span>
      </footer>
    </div>
  );
}
