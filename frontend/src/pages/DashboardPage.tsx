import { useEffect, useState } from "react";

import { SectionCard } from "../components/SectionCard";
import { StatCard } from "../components/StatCard";
import { TrendBars } from "../components/TrendBars";
import { EmptyState } from "../components/EmptyState";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { formatCurrency, formatDate, titleCase } from "../lib/format";
import type {
  CategoryBreakdownResponse,
  RecentActivityResponse,
  SummaryReport,
  TrendPeriod,
  TrendResponse,
  TrendTypeFilter,
} from "../types/api";

export function DashboardPage() {
  const { token, user, refreshMe } = useAuth();
  const [summary, setSummary] = useState<SummaryReport | null>(null);
  const [breakdown, setBreakdown] = useState<CategoryBreakdownResponse | null>(null);
  const [trends, setTrends] = useState<TrendResponse | null>(null);
  const [recent, setRecent] = useState<RecentActivityResponse | null>(null);
  const [period, setPeriod] = useState<TrendPeriod>("monthly");
  const [trendType, setTrendType] = useState<TrendTypeFilter>("all");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      return;
    }
    void refreshMe();
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    const authToken = token;

    async function loadDashboard() {
      setLoading(true);
      setError(null);

      try {
        const [nextSummary, nextBreakdown, nextTrends, nextRecent] = await Promise.all([
          api.summary(authToken),
          api.categoryBreakdown(authToken),
          api.trends(authToken, period, trendType),
          user?.role === "viewer" ? Promise.resolve(null) : api.recentActivity(authToken),
        ]);
        setSummary(nextSummary);
        setBreakdown(nextBreakdown);
        setTrends(nextTrends);
        setRecent(nextRecent);
      } catch (nextError) {
        setError(nextError instanceof Error ? nextError.message : "Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, [period, token, trendType, user?.role]);

  return (
    <div className="page-grid">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Signed in as {user?.role}</p>
          <h2>{user?.full_name}, the backend is ready for exploration.</h2>
          <p>
            This dashboard pulls directly from the seeded finance API and gives us a live place to
            inspect totals, activity, access, and reporting before we expand the frontend further.
          </p>
        </div>
        <div className="hero-highlight">
          <span>Workspace status</span>
          <strong>{error ? "Needs attention" : "Operational"}</strong>
          <p>{error ?? "FastAPI reports, users, and role endpoints are connected."}</p>
        </div>
      </section>

      {loading ? (
        <div className="section-card">Loading dashboard data...</div>
      ) : error ? (
        <SectionCard title="Dashboard error" subtitle="The API call failed.">
          <p className="error-text">{error}</p>
        </SectionCard>
      ) : (
        <>
          <div className="stats-grid">
            <StatCard label="Total income" value={summary?.total_income ?? "0"} tone="positive" />
            <StatCard label="Total expense" value={summary?.total_expense ?? "0"} tone="negative" />
            <StatCard label="Net balance" value={summary?.net_balance ?? "0"} tone="neutral" />
          </div>

          <SectionCard
            title="Trend view"
            subtitle="Switch between weekly and monthly slices without leaving the dashboard."
            actions={
              <div className="inline-controls">
                <select value={period} onChange={(event) => setPeriod(event.target.value as TrendPeriod)}>
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                </select>
                <select
                  value={trendType}
                  onChange={(event) => setTrendType(event.target.value as TrendTypeFilter)}
                >
                  <option value="all">All</option>
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                </select>
              </div>
            }
          >
            <TrendBars items={trends?.items ?? []} />
          </SectionCard>

          <div className="two-column-grid">
            <SectionCard
              title="Category breakdown"
              subtitle="Highest value categories across the current dataset."
            >
              {breakdown?.items.length ? (
                <div className="list-table">
                  {breakdown.items.slice(0, 8).map((item) => (
                    <div className="list-row" key={`${item.category}-${item.type}`}>
                      <div>
                        <strong>{titleCase(item.category)}</strong>
                        <p className="muted">{titleCase(item.type)}</p>
                      </div>
                      <strong>{formatCurrency(item.total)}</strong>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="No categories yet" body="Create records to populate breakdowns." />
              )}
            </SectionCard>

            {user?.role === "viewer" ? (
              <SectionCard
                title="Viewer access"
                subtitle="Viewer accounts are intentionally limited to dashboard data only."
              >
                <div className="info-block">
                  <p>You can inspect summary cards, category mix, and trends from here.</p>
                  <p>Access to record listings, users, and role management is reserved for higher roles.</p>
                </div>
              </SectionCard>
            ) : (
              <SectionCard title="Recent activity" subtitle="Latest seeded or newly created records.">
                {recent?.items.length ? (
                  <div className="list-table">
                    {recent.items.map((item) => (
                      <div className="list-row" key={item.id}>
                        <div>
                          <strong>{titleCase(item.category)}</strong>
                          <p className="muted">
                            {titleCase(item.type)} - {formatDate(item.record_date)}
                          </p>
                        </div>
                        <strong>{formatCurrency(item.amount)}</strong>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No activity" body="Recent activity appears here once records exist." />
                )}
              </SectionCard>
            )}
          </div>
        </>
      )}
    </div>
  );
}
