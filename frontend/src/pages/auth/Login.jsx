import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthLayout from "../../components/layout/AuthLayout";
import {
  login,
} from "../../auth/authService";
import { useAuth } from "../../auth/AuthProvider";


export default function Login() {
  const navigate = useNavigate();
  const { refreshSession } = useAuth();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);


  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!form.username.trim()) {
      setError("Please enter your username.");
      return;
    }

    if (!form.password) {
      setError("Please enter your password.");
      return;
    }

    try {
      setLoading(true);

      const result = await login(form);

      if (result.status === "NEW_PASSWORD_REQUIRED") {
        navigate("/change-password", {
          state: {
            user: result.user,
            userAttributes: result.userAttributes,
          },
        });

        return;
      }

      await refreshSession();

      navigate("/dashboard");

    } catch (err) {
      setError(
        err?.message ||
        "Unable to sign in. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <AuthLayout>

      <div>
        <h1 className="text-3xl font-bold">
          Welcome back
        </h1>

        <p className="mt-2 text-slate-400">
          Sign in to continue to CareerForge.
        </p>
      </div>


      {error && (
        <div
          className="mt-6 rounded-lg border border-red-500/30
                     bg-red-500/10 p-3 text-sm text-red-300"
          role="alert"
        >
          {error}
        </div>
      )}


      <form
        onSubmit={handleSubmit}
        className="mt-8 space-y-5"
      >

        <div>
          <label
            htmlFor="username"
            className="mb-2 block text-sm font-medium"
          >
            Username
          </label>

          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            value={form.username}
            onChange={handleChange}
            placeholder="Enter your username"
            className="w-full rounded-xl border border-slate-700
                       bg-slate-900 px-4 py-3 outline-none
                       transition focus:border-white"
          />
        </div>


        <div>
          <div className="mb-2 flex items-center justify-between">
            <label
              htmlFor="password"
              className="text-sm font-medium"
            >
              Password
            </label>

            <Link
              to="/forgot-password"
              className="text-sm text-slate-400 hover:text-white"
            >
              Forgot password?
            </Link>
          </div>


          <div className="relative">
            <input
              id="password"
              name="password"
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="w-full rounded-xl border border-slate-700
                         bg-slate-900 px-4 py-3 pr-20 outline-none
                         transition focus:border-white"
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword((value) => !value)
              }
              className="absolute right-3 top-1/2
                         -translate-y-1/2 text-sm
                         text-slate-400 hover:text-white"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>


        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-white px-4 py-3
                     font-semibold text-slate-950
                     transition hover:bg-slate-200
                     disabled:cursor-not-allowed
                     disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>

      </form>


      <p className="mt-8 text-center text-sm text-slate-400">
        Don't have a CareerForge account?{" "}

        <Link
          to="/register"
          className="font-medium text-white hover:underline"
        >
          Create account
        </Link>
      </p>

    </AuthLayout>
  );
}