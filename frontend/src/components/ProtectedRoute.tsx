import { Navigate, useLocation } from "react-router-dom";
import type { PropsWithChildren } from "react";

import { useAuth } from "../lib/auth";
import type { Role } from "../types/api";

export function ProtectedRoute({
  children,
  allowedRoles,
}: PropsWithChildren<{ allowedRoles?: Role[] }>) {
  const { token, user } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (allowedRoles && (!user || !allowedRoles.includes(user.role))) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
