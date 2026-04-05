import { formatCurrency } from "../lib/format";

export function StatCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "positive" | "negative";
}) {
  return (
    <article className={`stat-card ${tone}`}>
      <p>{label}</p>
      <strong>{formatCurrency(value)}</strong>
    </article>
  );
}
