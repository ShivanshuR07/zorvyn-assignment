import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../lib/auth";
import type { Role } from "../types/api";

const navItems: Array<{ to: string; label: string; roles: Role[] }> = [
  { to: "/", label: "Dashboard", roles: ["viewer", "analyst", "admin"] },
  { to: "/records", label: "Records", roles: ["analyst", "admin"] },
  { to: "/users", label: "Users", roles: ["admin"] },
  { to: "/roles", label: "Roles", roles: ["admin"] },
];

export function AppShell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const visibleNavItems = navItems.filter((item) => (user ? item.roles.includes(user.role) : false));

  return (
    <div className="app-frame">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="eyebrow">Zorvyn</p>
          <h1>Finance Console</h1>
          <p className="muted">
            REST-backed admin cockpit for auth, reporting, users, roles, and ledger records.
          </p>
        </div>

        <nav className="nav-list" aria-label="Primary">
          {visibleNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            >
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            <div>
              <strong>{user?.full_name}</strong>
              <p>
                {user?.role} - {user?.state}
              </p>
            </div>
          </div>
          <button className="ghost-button" type="button" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Live Workspace</p>
            <h2>{pageTitle(location.pathname, user?.role)}</h2>
          </div>
          <div className="topbar-badge">API: {import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}</div>
        </header>

        <Outlet />
      </main>
    </div>
  );
}

function pageTitle(pathname: string, role?: Role) {
  if (pathname === "/users") return "User Management";
  if (pathname === "/roles") return "Role Catalog";
  if (pathname === "/records") return "Financial Records";
  if (role === "viewer") return "Dashboard Overview";
  return "Dashboard";
}
