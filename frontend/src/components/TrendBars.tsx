import type { TrendPoint } from "../types/api";
import { formatCurrency, formatDate } from "../lib/format";

export function TrendBars({ items }: { items: TrendPoint[] }) {
  if (!items.length) {
    return <div className="empty-inline">No trend data available yet.</div>;
  }

  const maxValue = Math.max(...items.map((item) => Number(item.total_income) + Number(item.total_expense)), 1);

  return (
    <div className="trend-bars">
      {items.map((item) => {
        const incomeHeight = (Number(item.total_income) / maxValue) * 100;
        const expenseHeight = (Number(item.total_expense) / maxValue) * 100;

        return (
          <div className="trend-column" key={`${item.period}-${item.period_start}`}>
            <div className="trend-stack" title={`Income ${formatCurrency(item.total_income)} - Expense ${formatCurrency(item.total_expense)}`}>
              <div className="trend-income" style={{ height: `${incomeHeight}%` }} />
              <div className="trend-expense" style={{ height: `${expenseHeight}%` }} />
            </div>
            <strong>{formatDate(item.period_start)}</strong>
          </div>
        );
      })}
    </div>
  );
}
