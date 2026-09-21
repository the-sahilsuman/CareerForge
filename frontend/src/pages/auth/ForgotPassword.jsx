import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthLayout from "../../components/layout/AuthLayout";
import {
  forgotPassword,
  confirmForgotPassword,
} from "../../auth/authService";


export default function ForgotPassword() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);

  const [username, setUsername] = useState("");

  const [form, setForm] = useState({
    code: "",
    password: "",
    confirmPassword: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };


  const sendCode = async (event) => {
    event.preventDefault();

    setError("");

    if (!username.trim()) {
      setError("Enter your username.");
      return;
    }

    try {
      setLoading(true);

      await forgotPassword({
        username: username.trim(),
      });

      setStep(2);

    } catch (err) {
      setError(
        err?.message ||
        "Unable to send password reset code."
      );
    } finally {
      setLoading(false);
    }
  };


  const resetPassword = async (event) => {
    event.preventDefault();

    setError("");

    if (!form.code.trim()) {
      setError("Enter the OTP.");
      return;
    }

    if (!form.password) {
      setError("Enter a new password.");
      return;
    }

    if (
      form.password !==
      form.confirmPassword
    ) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await confirmForgotPassword({
        username: username.trim(),
        code: form.code.trim(),
        newPassword: form.password,
      });

      navigate("/login");

    } catch (err) {
      setError(
        err?.message ||
        "Unable to reset your password."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <AuthLayout>

      <h1 className="text-3xl font-bold">
        Reset your password
      </h1>

      <p className="mt-3 text-slate-400">
        {step === 1
          ? "Enter your username to receive a verification code."
          : "Enter the code and create your new password."}
      </p>


      {error && (
        <div className="mt-6 rounded-lg border
                        border-red-500/30
                        bg-red-500/10 p-3
                        text-sm text-red-300">
          {error}
        </div>
      )}


      {step === 1 ? (
        <form
          onSubmit={sendCode}
          className="mt-8 space-y-5"
        >

          <div>
            <label className="mb-2 block text-sm">
              Username
            </label>

            <input
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Your CareerForge username"
              className="w-full rounded-xl border
                         border-slate-700 bg-slate-900
                         px-4 py-3 outline-none
                         focus:border-white"
            />
          </div>


          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-white
                       px-4 py-3 font-semibold
                       text-slate-950
                       disabled:opacity-50"
          >
            {loading
              ? "Sending code..."
              : "Send OTP"}
          </button>

        </form>
      ) : (
        <form
          onSubmit={resetPassword}
          className="mt-8 space-y-5"
        >

          <div>
            <label className="mb-2 block text-sm">
              Verification code
            </label>

            <input
              name="code"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={form.code}
              onChange={handleChange}
              placeholder="Enter OTP"
              className="w-full rounded-xl border
                         border-slate-700 bg-slate-900
                         px-4 py-3 outline-none
                         focus:border-white"
            />
          </div>


          <div>
            <label className="mb-2 block text-sm">
              New password
            </label>

            <input
              name="password"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={handleChange}
              placeholder="New password"
              className="w-full rounded-xl border
                         border-slate-700 bg-slate-900
                         px-4 py-3 outline-none
                         focus:border-white"
            />
          </div>


          <div>
            <label className="mb-2 block text-sm">
              Confirm password
            </label>

            <input
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={form.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm password"
              className="w-full rounded-xl border
                         border-slate-700 bg-slate-900
                         px-4 py-3 outline-none
                         focus:border-white"
            />
          </div>


          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-white
                       px-4 py-3 font-semibold
                       text-slate-950
                       disabled:opacity-50"
          >
            {loading
              ? "Resetting..."
              : "Reset password"}
          </button>

        </form>
      )}


      <p className="mt-8 text-center text-sm text-slate-400">
        Remember your password?{" "}

        <Link
          to="/login"
          className="text-white hover:underline"
        >
          Sign in
        </Link>
      </p>

    </AuthLayout>
  );
}