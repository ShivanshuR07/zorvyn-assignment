import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { SectionCard } from "../components/SectionCard";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { formatDate, titleCase } from "../lib/format";
import type {
  AuthUser,
  Role,
  UserCreatePayload,
  UserState,
  UserUpdatePayload,
} from "../types/api";

const emptyUserForm: UserCreatePayload = {
  full_name: "",
  email: "",
  password: "",
  role: "viewer",
  state: "active",
};

const emptyUserEditForm: UserUpdatePayload = {
  full_name: "",
  password: "",
  role: "viewer",
  state: "active",
};

export function UsersPage() {
  const { token, user: currentUser } = useAuth();
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [createForm, setCreateForm] = useState<UserCreatePayload>(emptyUserForm);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<UserUpdatePayload>(emptyUserEditForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
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

  function beginEdit(user: AuthUser) {
    setEditingUserId(user.id);
    setEditForm({
      full_name: user.full_name,
      password: "",
      role: user.role,
      state: user.state,
    });
    setError(null);
  }

  function cancelEdit() {
    setEditingUserId(null);
    setEditForm(emptyUserEditForm);
  }

  async function handleCreateUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await api.createUser(token, createForm);
      setCreateForm(emptyUserForm);
      await loadUsers(token);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to create user.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUpdateUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !editingUserId) {
      return;
    }

    setSaving(true);
    setError(null);

    const payload: UserUpdatePayload = {
      full_name: editForm.full_name?.trim(),
      role: editForm.role as Role,
      state: editForm.state as UserState,
    };

    if (editForm.password?.trim()) {
      payload.password = editForm.password.trim();
    }

    try {
      await api.updateUser(token, editingUserId, payload);
      cancelEdit();
      await loadUsers(token);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to update user.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteUser(user: AuthUser) {
    if (!token) {
      return;
    }

    const confirmed = window.confirm(`Delete ${user.full_name}? This cannot be undone.`);
    if (!confirmed) {
      return;
    }

    setDeletingId(user.id);
    setError(null);

    try {
      await api.deleteUser(token, user.id);
      if (editingUserId === user.id) {
        cancelEdit();
      }
      await loadUsers(token);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to delete user.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="page-grid">
      <div className="two-column-grid">
        <SectionCard title="Create user" subtitle="Admin can create new accounts for each dashboard role.">
          <form className="stack-form" onSubmit={handleCreateUser}>
            <input
              placeholder="Full name"
              value={createForm.full_name}
              onChange={(event) => setCreateForm({ ...createForm, full_name: event.target.value })}
            />
            <input
              placeholder="Email"
              type="email"
              value={createForm.email}
              onChange={(event) => setCreateForm({ ...createForm, email: event.target.value })}
            />
            <input
              placeholder="Password"
              type="password"
              value={createForm.password}
              onChange={(event) => setCreateForm({ ...createForm, password: event.target.value })}
            />
            <div className="inline-controls">
              <select
                value={createForm.role}
                onChange={(event) => setCreateForm({ ...createForm, role: event.target.value as Role })}
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
              <select
                value={createForm.state}
                onChange={(event) =>
                  setCreateForm({ ...createForm, state: event.target.value as UserState })
                }
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

        <SectionCard
          title="Edit user"
          subtitle="Admin can update profile details, role, status, and password."
        >
          {editingUserId ? (
            <form className="stack-form" onSubmit={handleUpdateUser}>
              <input
                placeholder="Full name"
                value={editForm.full_name ?? ""}
                onChange={(event) => setEditForm({ ...editForm, full_name: event.target.value })}
              />
              <input
                placeholder="New password (optional)"
                type="password"
                value={editForm.password ?? ""}
                onChange={(event) => setEditForm({ ...editForm, password: event.target.value })}
              />
              <div className="inline-controls">
                <select
                  value={editForm.role ?? "viewer"}
                  onChange={(event) => setEditForm({ ...editForm, role: event.target.value as Role })}
                >
                  <option value="viewer">Viewer</option>
                  <option value="analyst">Analyst</option>
                  <option value="admin">Admin</option>
                </select>
                <select
                  value={editForm.state ?? "active"}
                  onChange={(event) => setEditForm({ ...editForm, state: event.target.value as UserState })}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
              <div className="button-row">
                <button className="primary-button" type="submit" disabled={saving}>
                  {saving ? "Saving..." : "Save changes"}
                </button>
                <button className="ghost-button" type="button" onClick={cancelEdit}>
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <EmptyState
              title="Select a user"
              body="Choose Edit from the table to load that user into the admin update form."
            />
          )}
        </SectionCard>
      </div>

      <SectionCard title="Users" subtitle="Admin CRUD view over the `/users` resource.">
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
                <span>
                  {user.full_name}
                  {currentUser?.id === user.id ? <span className="table-note">You</span> : null}
                </span>
                <span>{user.email}</span>
                <span>{titleCase(user.role)}</span>
                <span>{titleCase(user.state)}</span>
                <span>{user.created_at ? formatDate(user.created_at) : "Now"}</span>
                <span className="table-actions">
                  <button className="ghost-button" type="button" onClick={() => beginEdit(user)}>
                    Edit
                  </button>
                  <button
                    className="danger-button"
                    type="button"
                    onClick={() => handleDeleteUser(user)}
                    disabled={deletingId === user.id}
                  >
                    {deletingId === user.id ? "Deleting..." : "Delete"}
                  </button>
                </span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No users found" body="Create a user to begin exploring admin CRUD." />
        )}
      </SectionCard>
    </div>
  );
}
