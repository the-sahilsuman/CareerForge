import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";

export default function AdminLayout() {
  return (
    <div className="min-h-screen bg-slate-900">

      <Sidebar role="ADMIN" />

      <main className="ml-64 min-h-screen">
        <Outlet />
      </main>

    </div>
  );
}