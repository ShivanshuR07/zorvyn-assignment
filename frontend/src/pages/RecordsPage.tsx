import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { SectionCard } from "../components/SectionCard";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { formatCurrency, formatDate, titleCase } from "../lib/format";
import type {
  FinancialRecord,
  RecordCreatePayload,
  RecordType,
  RecordUpdatePayload,
} from "../types/api";

const buildEmptyRecordForm = (): RecordCreatePayload => ({
  amount: "",
  type: "expense",
  category: "",
  record_date: new Date().toISOString().slice(0, 10),
  notes: "",
});

export function RecordsPage() {
  const { token, user } = useAuth();
  const [records, setRecords] = useState<FinancialRecord[]>([]);
  const [recordForm, setRecordForm] = useState<RecordCreatePayload>(buildEmptyRecordForm());
  const [editRecordId, setEditRecordId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<RecordCreatePayload>(buildEmptyRecordForm());
  const [typeFilter, setTypeFilter] = useState<"all" | RecordType>("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadRecords(token, typeFilter);
  }, [token, typeFilter]);

  async function loadRecords(authToken: string, nextType: "all" | RecordType) {
    setLoading(true);
    setError(null);
    try {
      const query = nextType === "all" ? "?limit=50&offset=0" : `?type=${nextType}&limit=50&offset=0`;
      const response = await api.records(authToken, query);
      setRecords(response.items);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to load records.");
    } finally {
      setLoading(false);
    }
  }

  function beginEdit(record: FinancialRecord) {
    setEditRecordId(record.id);
    setEditForm({
      amount: record.amount,
      type: record.type,
      category: record.category,
      record_date: record.record_date,
      notes: record.notes ?? "",
    });
    setError(null);
  }

  function cancelEdit() {
    setEditRecordId(null);
    setEditForm(buildEmptyRecordForm());
  }

  async function handleCreateRecord(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setSaving(true);
    setError(null);
    try {
      await api.createRecord(token, recordForm);
      setRecordForm(buildEmptyRecordForm());
      await loadRecords(token, typeFilter);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to create record.");
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateRecord(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !editRecordId) {
      return;
    }

    setUpdating(true);
    setError(null);

    const payload: RecordUpdatePayload = {
      amount: editForm.amount,
      type: editForm.type,
      category: editForm.category,
      record_date: editForm.record_date,
      notes: editForm.notes,
    };

    try {
      await api.updateRecord(token, editRecordId, payload);
      cancelEdit();
      await loadRecords(token, typeFilter);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to update record.");
    } finally {
      setUpdating(false);
    }
  }

  async function handleDeleteRecord(record: FinancialRecord) {
    if (!token) {
      return;
    }

    const confirmed = window.confirm(`Delete the ${record.category} record from ${record.record_date}?`);
    if (!confirmed) {
      return;
    }

    setDeletingId(record.id);
    setError(null);

    try {
      await api.deleteRecord(token, record.id);
      if (editRecordId === record.id) {
        cancelEdit();
      }
      await loadRecords(token, typeFilter);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to delete record.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="page-grid">
      <div className="two-column-grid">
        <SectionCard
          title="Create record"
          subtitle="Admin can add income and expense items that immediately affect reporting."
        >
          {user?.role === "admin" ? (
            <form className="stack-form" onSubmit={handleCreateRecord}>
              <div className="inline-controls">
                <input
                  placeholder="Amount"
                  value={recordForm.amount}
                  onChange={(event) => setRecordForm({ ...recordForm, amount: event.target.value })}
                />
                <select
                  value={recordForm.type}
                  onChange={(event) =>
                    setRecordForm({ ...recordForm, type: event.target.value as RecordType })
                  }
                >
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                </select>
              </div>
              <input
                placeholder="Category"
                value={recordForm.category}
                onChange={(event) => setRecordForm({ ...recordForm, category: event.target.value })}
              />
              <input
                type="date"
                value={recordForm.record_date}
                onChange={(event) => setRecordForm({ ...recordForm, record_date: event.target.value })}
              />
              <textarea
                placeholder="Notes"
                rows={4}
                value={recordForm.notes}
                onChange={(event) => setRecordForm({ ...recordForm, notes: event.target.value })}
              />
              <button className="primary-button" type="submit" disabled={saving}>
                {saving ? "Saving..." : "Create record"}
              </button>
            </form>
          ) : (
            <EmptyState
              title="Read-only mode"
              body="Analyst users can inspect records here, while admin users can manage them."
            />
          )}
        </SectionCard>

        <SectionCard
          title={user?.role === "admin" ? "Edit record" : "Filter records"}
          subtitle={
            user?.role === "admin"
              ? "Pick a record from the table to update or remove it."
              : "Quickly narrow the API list view by income or expense."
          }
          actions={
            <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value as "all" | RecordType)}>
              <option value="all">All types</option>
              <option value="income">Income only</option>
              <option value="expense">Expense only</option>
            </select>
          }
        >
          {user?.role === "admin" ? (
            editRecordId ? (
              <form className="stack-form" onSubmit={handleUpdateRecord}>
                <div className="inline-controls">
                  <input
                    placeholder="Amount"
                    value={editForm.amount}
                    onChange={(event) => setEditForm({ ...editForm, amount: event.target.value })}
                  />
                  <select
                    value={editForm.type}
                    onChange={(event) => setEditForm({ ...editForm, type: event.target.value as RecordType })}
                  >
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                </div>
                <input
                  placeholder="Category"
                  value={editForm.category}
                  onChange={(event) => setEditForm({ ...editForm, category: event.target.value })}
                />
                <input
                  type="date"
                  value={editForm.record_date}
                  onChange={(event) => setEditForm({ ...editForm, record_date: event.target.value })}
                />
                <textarea
                  placeholder="Notes"
                  rows={4}
                  value={editForm.notes}
                  onChange={(event) => setEditForm({ ...editForm, notes: event.target.value })}
                />
                <div className="button-row">
                  <button className="primary-button" type="submit" disabled={updating}>
                    {updating ? "Saving..." : "Save changes"}
                  </button>
                  <button className="ghost-button" type="button" onClick={cancelEdit}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <EmptyState
                title="Select a record"
                body="Use the Edit action in the table to load a record into the admin update form."
              />
            )
          ) : (
            <div className="info-block">
              <p>
                This page consumes `GET /financial-records` for analysts and admins, while only admin
                can call the write endpoints.
              </p>
            </div>
          )}
        </SectionCard>
      </div>

      <SectionCard title="Financial records" subtitle="Latest 50 records from the API.">
        {error ? <p className="error-text">{error}</p> : null}
        {loading ? (
          <p>Loading records...</p>
        ) : records.length ? (
          <div className={`table-grid records-table${user?.role === "admin" ? " records-table-admin" : ""}`}>
            <div className="table-head">
              <span>Category</span>
              <span>Type</span>
              <span>Date</span>
              <span>Amount</span>
              <span>Notes</span>
              {user?.role === "admin" ? <span>Action</span> : null}
            </div>
            {records.map((record) => (
              <div className="table-row" key={record.id}>
                <span>{titleCase(record.category)}</span>
                <span>{titleCase(record.type)}</span>
                <span>{formatDate(record.record_date)}</span>
                <span>{formatCurrency(record.amount)}</span>
                <span>{record.notes ?? "No notes"}</span>
                {user?.role === "admin" ? (
                  <span className="table-actions">
                    <button className="ghost-button" type="button" onClick={() => beginEdit(record)}>
                      Edit
                    </button>
                    <button
                      className="danger-button"
                      type="button"
                      onClick={() => handleDeleteRecord(record)}
                      disabled={deletingId === record.id}
                    >
                      {deletingId === record.id ? "Deleting..." : "Delete"}
                    </button>
                  </span>
                ) : null}
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No records found" body="Create a record or widen the current filter." />
        )}
      </SectionCard>
    </div>
  );
}
