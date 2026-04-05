import { useEffect, useState } from "react";

import { SectionCard } from "../components/SectionCard";
import { EmptyState } from "../components/EmptyState";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { formatDate, titleCase } from "../lib/format";
import type { AuthUser, Role, UserCreatePayload, UserState } from "../types/api";

const emptyUserForm: UserCreatePayload = {
  full_name: "",
  email: "",
  password: "",
  role: "viewer",
  state: "active",
};

export function UsersPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [form, setForm] = useState<UserCreatePayload>(emptyUserForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadUsers(token);
  }, [token]);

  async function loadUsers(authToken: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await api.users(authToken);
      setUsers(response.items);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await api.createUser(token, form);
      setForm(emptyUserForm);
      await loadUsers(token);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to create user.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStateChange(userId: string, state: UserState) {
    if (!token) {
      return;
    }

    try {
      await api.updateUserState(token, userId, state);
      await loadUsers(token);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to update user state.");
    }
  }

  return (
    <div className="page-grid">
      <div className="two-column-grid">
        <SectionCard title="Create user" subtitle="Quick admin workflow for testing access scenarios.">
          <form className="stack-form" onSubmit={handleCreateUser}>
            <input
              placeholder="Full name"
              value={form.full_name}
              onChange={(event) => setForm({ ...form, full_name: event.target.value })}
            />
            <input
              placeholder="Email"
              type="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
            />
            <input
              placeholder="Password"
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
            />
            <div className="inline-controls">
              <select
                value={form.role}
                onChange={(event) => setForm({ ...form, role: event.target.value as Role })}
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
              <select
                value={form.state}
                onChange={(event) => setForm({ ...form, state: event.target.value as UserState })}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create user"}
            </button>
          </form>
        </SectionCard>

        <SectionCard title="Access notes" subtitle="How to read the user table from the frontend.">
          <div className="info-block">
            <p>Use this page to create new testers, flip account state, and verify the auth workflow.</p>
            <p>
              Active users can log in. Inactive and suspended users will be rejected by the backend
              even if the email and password are correct.
            </p>
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Users" subtitle="Current users from the `/users` admin endpoint.">
        {error ? <p className="error-text">{error}</p> : null}
        {loading ? (
          <p>Loading users...</p>
        ) : users.length ? (
          <div className="table-grid">
            <div className="table-head">
              <span>Name</span>
              <span>Email</span>
              <span>Role</span>
              <span>State</span>
              <span>Created</span>
              <span>Action</span>
            </div>
            {users.map((user) => (
              <div className="table-row" key={user.id}>
                <span>{user.full_name}</span>
                <span>{user.email}</span>
                <span>{titleCase(user.role)}</span>
                <span>{titleCase(user.state)}</span>
                <span>{user.created_at ? formatDate(user.created_at) : "Now"}</span>
                <span>
                  <select
                    value={user.state}
                    onChange={(event) => handleStateChange(user.id, event.target.value as UserState)}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No users found" body="Create a user to begin exploring access states." />
        )}
      </SectionCard>
    </div>
  );
}
