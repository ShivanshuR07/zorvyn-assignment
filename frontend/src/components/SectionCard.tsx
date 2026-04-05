import type { PropsWithChildren, ReactNode } from "react";

export function SectionCard({
  title,
  subtitle,
  actions,
  children,
}: PropsWithChildren<{ title: string; subtitle?: string; actions?: ReactNode }>) {
  return (
    <section className="section-card">
      <div className="section-card-header">
        <div>
          <h3>{title}</h3>
          {subtitle ? <p className="muted">{subtitle}</p> : null}
        </div>
        {actions ? <div className="section-actions">{actions}</div> : null}
      </div>
      {children}
    </section>
  );
}
