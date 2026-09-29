import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

import { useAuth } from "./AuthContext";

export function ProtectedRoute({
  children,
}: {
  children: ReactNode;
}) {
  const {
    user,
    loading,
  } = useAuth();

  if (loading) {
    return (
      <div className="center-screen">
        Cargando...
      </div>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return <>{children}</>;
}