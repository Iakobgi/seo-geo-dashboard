import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { authApi } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import AuthLayout from "../components/AuthLayout";
import { Notice } from "../components/UI";
export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Your passwords don’t match.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(token, password);
      setSuccess(true);
    } catch (err) {
      setError(
        errorMessage(
          err,
          "This link may have expired. Request a new reset link.",
        ),
      );
    } finally {
      setLoading(false);
    }
  };
  return (
    <AuthLayout>
      <p className="eyebrow">A FRESH START</p>
      <h1>Set a new password.</h1>
      <p>Choose a password you haven’t used before.</p>
      {!token ? (
        <Notice>
          This reset link is incomplete.{" "}
          <Link to="/forgot-password">Request a new link.</Link>
        </Notice>
      ) : success ? (
        <div role="status" className="success-message">
          Your password has been updated.{" "}
          <Link to="/login">Log in to your workspace.</Link>
        </div>
      ) : (
        <form onSubmit={submit}>
          <label className="field" htmlFor="new-password">
            New password
            <input
              id="new-password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              maxLength={72}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="auth-hint">Use 8–72 characters.</p>
          </label>
          <label className="field" htmlFor="confirm-password">
            Confirm password
            <input
              id="confirm-password"
              type="password"
              autoComplete="new-password"
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </label>
          {error && <Notice>{error}</Notice>}
          <button disabled={loading} className="button button-dark auth-submit">
            {loading && <Loader2 size={17} className="animate-spin" />}Update
            password
          </button>
          <p className="auth-bottom">
            <Link to="/forgot-password">Request a new reset link</Link>
          </p>
        </form>
      )}
    </AuthLayout>
  );
}
