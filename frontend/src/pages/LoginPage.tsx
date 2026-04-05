import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/auth";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("shivanshu@example.com");
  const [password, setPassword] = useState("shivanshu123");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as { from?: string } | null)?.from ?? "/";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login-shell">
      <section className="login-hero">
        <p className="eyebrow">Frontend Start Point</p>
        <h1>React control room for the finance backend.</h1>
        <p>
          Sign in with the seeded admin account to explore reports, user access, roles, and records
          against the FastAPI backend we just built.
        </p>
        <div className="login-demo-card">
          <span>Demo Admin</span>
          <strong>shivanshu@example.com</strong>
          <code>shivanshu123</code>
        </div>
      </section>

      <section className="login-panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">Email</label>
            <input id="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          {error ? <p className="error-text">{error}</p> : null}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign in to dashboard"}
          </button>
        </form>
      </section>
    </div>
  );
}
