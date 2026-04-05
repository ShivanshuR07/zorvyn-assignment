import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { SectionCard } from "../components/SectionCard";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { formatCurrency, formatDate, titleCase } from "../lib/format";
import type { FinancialRecord, RecordCreatePayload, RecordType } from "../types/api";

const emptyRecordForm: RecordCreatePayload = {
  amount: "",
  type: "expense",
  category: "",
  record_date: new Date().toISOString().slice(0, 10),
  notes: "",
};

export function RecordsPage() {
  const { token, user } = useAuth();
  const [records, setRecords] = useState<FinancialRecord[]>([]);
  const [recordForm, setRecordForm] = useState<RecordCreatePayload>(emptyRecordForm);
  const [typeFilter, setTypeFilter] = useState<"all" | RecordType>("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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

  async function handleCreateRecord(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setSaving(true);
    setError(null);
    try {
      await api.createRecord(token, recordForm);
      setRecordForm(emptyRecordForm);
      await loadRecords(token, typeFilter);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to create record.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-grid">
      <div className="two-column-grid">
        <SectionCard
          title="Create record"
          subtitle="Available to admin users so we can immediately affect reports and activity."
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
              body="Only admin users can create records in the current backend policy."
            />
          )}
        </SectionCard>

        <SectionCard
          title="Filter records"
          subtitle="Quickly narrow the API list view by income or expense."
          actions={
            <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value as "all" | RecordType)}>
              <option value="all">All types</option>
              <option value="income">Income only</option>
              <option value="expense">Expense only</option>
            </select>
          }
        >
          <div className="info-block">
            <p>
              This page consumes `GET /financial-records` and `POST /financial-records` so we can
              explore both read and write flows from the frontend.
            </p>
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Financial records" subtitle="Latest 50 records from the API.">
        {error ? <p className="error-text">{error}</p> : null}
        {loading ? (
          <p>Loading records...</p>
        ) : records.length ? (
          <div className="table-grid records-table">
            <div className="table-head">
              <span>Category</span>
              <span>Type</span>
              <span>Date</span>
              <span>Amount</span>
              <span>Notes</span>
            </div>
            {records.map((record) => (
              <div className="table-row" key={record.id}>
                <span>{titleCase(record.category)}</span>
                <span>{titleCase(record.type)}</span>
                <span>{formatDate(record.record_date)}</span>
                <span>{formatCurrency(record.amount)}</span>
                <span>{record.notes ?? "No notes"}</span>
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
