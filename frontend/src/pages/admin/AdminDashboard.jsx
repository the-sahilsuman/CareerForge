import { useAuth } from "../../auth/AuthProvider";

export default function AdminDashboard() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">

        <p className="text-slate-400 text-sm">
          CareerForge Administration
        </p>

        <h1 className="text-3xl font-bold mt-2">
          Admin Dashboard
        </h1>

        <p className="text-slate-400 mt-2">
          {user?.email}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">

          <AdminCard
            title="Users"
            description="Manage platform users"
          />

          <AdminCard
            title="Applications"
            description="Monitor job applications"
          />

          <AdminCard
            title="Analytics"
            description="Platform usage and application metrics"
          />

          <AdminCard
            title="Monitoring"
            description="Monitor CareerForge services"
          />

        </div>
      </div>
    </div>
  );
}

function AdminCard({ title, description }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold">
        {title}
      </h2>

      <p className="text-slate-400 mt-2 text-sm">
        {description}
      </p>
    </div>
  );
}