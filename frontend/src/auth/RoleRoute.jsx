import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthProvider";


export default function RoleRoute({
  allowedRoles,
}) {
  const {
    role,
    isAuthenticated,
    loading,
  } = useAuth();


  if (loading) {
    return (
      <div>
        Loading CareerForge...
      </div>
    );
  }


  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  if (!role || !allowedRoles.includes(role)) {
    return (
      <Navigate
        to="/unauthorized"
        replace
      />
    );
  }


  return <Outlet />;
}