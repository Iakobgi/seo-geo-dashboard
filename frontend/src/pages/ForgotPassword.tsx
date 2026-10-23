import { useState } from "react";
import { Link } from "react-router-dom";
import { Loader2, Mail } from "lucide-react";
import { authApi } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import AuthLayout from "../components/AuthLayout";
import { Notice } from "../components/UI";
export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await authApi.requestPasswordReset(email.trim());
      setSent(true);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };
  return (
    <AuthLayout>
      <p className="eyebrow">ACCOUNT RECOVERY</p>
      <h1>Let’s get you back in.</h1>
      <p>Enter your email to request a password reset link.</p>
      {sent ? (
        <div role="status" className="success-message">
          If an account exists for that email, we’ll send a reset link. Check
          your inbox and spam folder. If it doesn’t arrive, contact your
          workspace administrator.
        </div>
      ) : (
        <form onSubmit={submit}>
          <label className="field" htmlFor="recovery-email">
            Email address
            <input
              id="recovery-email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
            />
          </label>
          {error && <Notice>{error}</Notice>}
          <button disabled={loading} className="button button-dark auth-submit">
            {loading ? (
              <Loader2 size={17} className="animate-spin" />
            ) : (
              <Mail size={17} />
            )}
            Send reset link
          </button>
        </form>
      )}
      <p className="auth-bottom">
        <Link to="/login">Back to login</Link>
      </p>
    </AuthLayout>
  );
}
