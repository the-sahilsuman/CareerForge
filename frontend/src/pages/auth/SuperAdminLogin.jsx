import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../../auth/authService";

export default function SuperAdminLogin() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const result = await login(email, password);

      if (result?.challenge === "NEW_PASSWORD_REQUIRED") {
        navigate("/change-password", {
          state: {
            username: email,
            challengeUser: result.user,
            superAdminLogin: true,
          },
        });

        return;
      }

      navigate("/super-admin");
    } catch (error) {
      console.error(error);

      setError(
        error?.message ||
          "Unable to authenticate super administrator."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">

          <div className="mb-8">
            <p className="text-sm text-slate-400">
              CareerForge Control Plane
            </p>

            <h1 className="text-3xl font-bold text-white mt-2">
              Super Admin Login
            </h1>

            <p className="text-slate-400 text-sm mt-2">
              Restricted system administration access.
            </p>
          </div>

          {error && (
            <div className="mb-5 rounded-lg border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            <div>
              <label className="block text-sm text-slate-300 mb-2">
                Super Admin Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
                autoComplete="username"
                className="w-full rounded-lg bg-slate-950 border border-slate-700 px-4 py-3 text-white outline-none focus:border-purple-500"
                placeholder="superadmin@company.com"
              />
            </div>

            <div>
              <label className="block text-sm text-slate-300 mb-2">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
                autoComplete="current-password"
                className="w-full rounded-lg bg-slate-950 border border-slate-700 px-4 py-3 text-white outline-none focus:border-purple-500"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 px-4 py-3 text-white font-semibold transition"
            >
              {loading
                ? "Authenticating..."
                : "Super Admin Login"}
            </button>

          </form>

          <p className="text-xs text-slate-500 mt-6 text-center">
            This area is restricted to SUPER_ADMIN
            accounts.
          </p>

        </div>
      </div>
    </div>
  );
}