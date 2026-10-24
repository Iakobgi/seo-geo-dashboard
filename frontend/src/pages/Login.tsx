import { useState } from "react";
import { Navigate, Link, useSearchParams, useLocation } from "react-router-dom";
import { Loader2, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import AuthLayout from "../components/AuthLayout";
import { Notice, Loading } from "../components/UI";
import { errorMessage } from "../api/helpers";
export default function Login() {
  const { user, loading: restoring, login, register } = useAuth();
  const [params, setParams] = useSearchParams();
  const location = useLocation();
  const mode = params.get("mode") === "register" ? "register" : "login";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const from = location.state?.from;
  const destination =
    typeof from === "string" &&
    /^\/(dashboard|audits|keywords|recommendations|agent|site-crawl|compare|snippet)(\?|$)/.test(from)
      ? from
      : "/dashboard";
  if (restoring) return <Loading />;
  if (user) return <Navigate to={destination} replace />;
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "register" && password !== confirm) {
      setError("Your passwords don’t match. Please check them.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (mode === "login") await login(email.trim(), password);
      else await register(email.trim(), password);
    } catch (err) {
      setError(errorMessage(err, "Unable to sign in. Please try again."));
    } finally {
      setLoading(false);
    }
  };
  return (
    <AuthLayout>
      <div className="auth-tabs" aria-label="Account access">
        <button
          disabled={loading}
          className={mode === "login" ? "active" : ""}
          onClick={() => {
            setParams({});
            setError(null);
          }}
        >
          Log in
        </button>
        <button
          disabled={loading}
          className={mode === "register" ? "active" : ""}
          onClick={() => {
            setParams({ mode: "register" });
            setError(null);
          }}
        >
          Create account
        </button>
      </div>
      <h1>{mode === "login" ? "Sign in" : "Create an account"}</h1>
      <p>
        {mode === "login"
          ? "Access your website audits, keywords, and recommendations."
          : "Create an account to audit and manage your website pages."}
      </p>
      {params.has("expired") && (
        <Notice>Your session ended. Please sign in again.</Notice>
      )}
      <form onSubmit={submit}>
        <fieldset disabled={loading}>
          <label className="field" htmlFor="email">
            Email address
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label className="field" htmlFor="password">
            Password
            <div className="password-field">
              <input
                id="password"
                type={visible ? "text" : "password"}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
                required
                minLength={mode === "register" ? 8 : undefined}
                maxLength={72}
                placeholder={
                  mode === "login" ? "Enter your password" : "Create a password"
                }
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                aria-label={visible ? "Hide password" : "Show password"}
                onClick={() => setVisible(!visible)}
              >
                {visible ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>
            {mode === "register" && (
              <p className="auth-hint">Use 8–72 characters.</p>
            )}
          </label>
          {mode === "register" && (
            <label className="field" htmlFor="confirm">
              Confirm password
              <input
                id="confirm"
                type={visible ? "text" : "password"}
                autoComplete="new-password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </label>
          )}
          {mode === "login" && (
            <div className="text-right mb-5 text-xs">
              <Link to="/forgot-password">Forgot password?</Link>
            </div>
          )}
          {error && <Notice>{error}</Notice>}
          <button className="button button-dark auth-submit" disabled={loading}>
            {loading ? (
              <Loader2 size={17} className="animate-spin" />
            ) : (
              <ArrowRight size={17} />
            )}
            {loading
              ? "Opening your workspace…"
              : mode === "login"
                ? "Log in to your workspace"
                : "Create your workspace"}
          </button>
        </fieldset>
      </form>
      <p className="auth-bottom">
        Website audits · SEO analysis · AI readiness
      </p>
    </AuthLayout>
  );
}
