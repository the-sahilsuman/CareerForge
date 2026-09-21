import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthLayout from "../../components/layout/AuthLayout";
import {
  register,
} from "../../auth/authService";


export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


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

    if (
      !form.username.trim() ||
      !form.email.trim() ||
      !form.password
    ) {
      setError("Please complete all required fields.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
      });

      navigate("/verify-email", {
        state: {
          username: form.username.trim(),
        },
      });

    } catch (err) {
      setError(
        err?.message ||
        "Unable to create your account."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <AuthLayout>

      <div>
        <h1 className="text-3xl font-bold">
          Create your account
        </h1>

        <p className="mt-2 text-slate-400">
          Start building your career profile with CareerForge.
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
            placeholder="Choose a unique username"
            className="w-full rounded-xl border border-slate-700
                       bg-slate-900 px-4 py-3 outline-none
                       focus:border-white"
          />

          <p className="mt-2 text-xs text-slate-500">
            This username will be used to sign in.
          </p>
        </div>


        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-sm font-medium"
          >
            Account email
          </label>

          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={handleChange}
            placeholder="you@example.com"
            className="w-full rounded-xl border border-slate-700
                       bg-slate-900 px-4 py-3 outline-none
                       focus:border-white"
          />

          <p className="mt-2 text-xs text-slate-500">
            Used for verification and password recovery.
          </p>
        </div>


        <div>
          <label
            htmlFor="password"
            className="mb-2 block text-sm font-medium"
          >
            Password
          </label>

          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={handleChange}
            placeholder="Create a strong password"
            className="w-full rounded-xl border border-slate-700
                       bg-slate-900 px-4 py-3 outline-none
                       focus:border-white"
          />
        </div>


        <div>
          <label
            htmlFor="confirmPassword"
            className="mb-2 block text-sm font-medium"
          >
            Confirm password
          </label>

          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            autoComplete="new-password"
            value={form.confirmPassword}
            onChange={handleChange}
            placeholder="Repeat your password"
            className="w-full rounded-xl border border-slate-700
                       bg-slate-900 px-4 py-3 outline-none
                       focus:border-white"
          />
        </div>


        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-white px-4 py-3
                     font-semibold text-slate-950
                     hover:bg-slate-200
                     disabled:cursor-not-allowed
                     disabled:opacity-50"
        >
          {loading
            ? "Creating account..."
            : "Create account"}
        </button>

      </form>


      <p className="mt-8 text-center text-sm text-slate-400">
        Already have an account?{" "}

        <Link
          to="/login"
          className="font-medium text-white hover:underline"
        >
          Sign in
        </Link>
      </p>

    </AuthLayout>
  );
}