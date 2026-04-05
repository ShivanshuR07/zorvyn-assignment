import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./lib/auth";
import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { RecordsPage } from "./pages/RecordsPage";
import { RolesPage } from "./pages/RolesPage";
import { UsersPage } from "./pages/UsersPage";

export default function App() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return <div className="screen-center">Loading workspace...</div>;
  }

  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route
          path="users"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <UsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="roles"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <RolesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="records"
          element={
            <ProtectedRoute allowedRoles={["analyst", "admin"]}>
              <RecordsPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to={token ? "/" : "/login"} replace />} />
    </Routes>
  );
}
