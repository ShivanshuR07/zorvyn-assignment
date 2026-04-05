import { useEffect, useState } from "react";

import { SectionCard } from "../components/SectionCard";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { titleCase } from "../lib/format";
import type { RoleDefinition } from "../types/api";

export function RolesPage() {
  const { token } = useAuth();
  const [roles, setRoles] = useState<RoleDefinition[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    const authToken = token;

    async function loadRoles() {
      try {
        setError(null);
        const nextRoles = await api.roles(authToken);
        setRoles(nextRoles);
      } catch (nextError) {
        setError(nextError instanceof Error ? nextError.message : "Failed to load roles.");
      }
    }

    void loadRoles();
  }, [token]);

  return (
    <div className="page-grid">
      <SectionCard title="Role catalog" subtitle="Static permissions exposed by the backend.">
        {error ? <p className="error-text">{error}</p> : null}
        <div className="role-grid">
          {roles.map((role) => (
            <article className="role-card" key={role.name}>
              <p className="eyebrow">{role.permissions.length} permissions</p>
              <h3>{titleCase(role.name)}</h3>
              <div className="pill-list">
                {role.permissions.map((permission) => (
                  <span className="pill" key={permission}>
                    {permission}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
