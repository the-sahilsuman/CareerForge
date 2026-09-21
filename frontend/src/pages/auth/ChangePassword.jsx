
import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import AuthLayout from "../../components/layout/AuthLayout";
import {
  changeTemporaryPassword,
} from "../../auth/authService";
import { useAuth } from "../../auth/AuthProvider";


export default function ChangePassword() {
  const location = useLocation();
  const navigate = useNavigate();
  const { refreshSession } = useAuth();

  const user = location.state?.user;
  const userAttributes =
    location.state?.userAttributes || {};

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!user) {
      setError(
        "Your password-change session has expired. Please login again."
      );
      return;
    }

    if (!password) {
      setError("Enter a new password.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      /*
       * Cognito may return attributes that should not
       * be sent back during the challenge.
       *
       * We only pass attributes that are actually
       * required by the challenge.
       */
      const requiredAttributes = {};

      if (userAttributes.email) {
        requiredAttributes.email =
          userAttributes.email;
      }

      await changeTemporaryPassword({
        user,
        newPassword: password,
        requiredAttributes,
      });

      await refreshSession();

      navigate("/dashboard");

    } catch (err) {
      setError(
        err?.message ||
        "Unable to set your new password."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <AuthLayout>

      <h1 className="text-3xl font-bold">
        Create your password
      </h1>

      <p className="mt-3 text-slate-400">
        This is your first login. Please replace
        the temporary password with a permanent one.
      </p>


      {error && (
        <div className="mt-6 rounded-lg border
                        border-red-500/30
                        bg-red-500/10 p-3
                        text-sm text-red-300">
          {error}
        </div>
      )}


      <form
        onSubmit={handleSubmit}
        className="mt-8 space-y-5"
      >

        <div>
          <label className="mb-2 block text-sm">
            New password
          </label>

          <input
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            placeholder="Create your permanent password"
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
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) =>
              setConfirmPassword(event.target.value)
            }
            placeholder="Repeat your password"
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
            ? "Updating..."
            : "Set permanent password"}
        </button>

      </form>

    </AuthLayout>
  );
}