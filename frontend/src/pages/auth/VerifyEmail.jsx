import { useState } from "react";
import {
    Link,
    useLocation,
    useNavigate,
} from "react-router-dom";

import AuthLayout from "../../components/layout/AuthLayout";

import {
    confirmRegistration,
} from "../../auth/authService";

import {
    provisionUser,
} from "../../services/api/authApi";


export default function VerifyEmail() {
    const location = useLocation();
    const navigate = useNavigate();

    const username =
        location.state?.username || "";

    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");

        if (!username) {
            setError(
                "Verification session is missing. Please register again."
            );
            return;
        }

        if (!code.trim()) {
            setError(
                "Please enter the verification code."
            );
            return;
        }

        try {
            setLoading(true);

            /*
             * STEP 1
             *
             * Confirm the Cognito user.
             */
            await confirmRegistration({
                username,
                code: code.trim(),
            });


            /*
             * STEP 2
             *
             * Cognito confirmation succeeded.
             *
             * Now create the corresponding
             * CareerForge PostgreSQL user.
             */
            await provisionUser(
                username
            );


            /*
             * STEP 3
             *
             * Both Cognito and PostgreSQL
             * provisioning succeeded.
             */
            navigate(
                "/login",
                {
                    replace: true,
                    state: {
                        username,
                        message:
                            "Email verified successfully. Your CareerForge account is ready.",
                    },
                }
            );

        } catch (err) {
            console.error(
                "EMAIL VERIFICATION ERROR:",
                err
            );

            /*
             * Axios error structure:
             *
             * err.response.data.detail
             */
            const backendMessage =
                err?.response?.data?.detail;

            setError(
                backendMessage ||
                err?.message ||
                "Unable to verify your email."
            );

        } finally {
            setLoading(false);
        }
    };


    return (
        <AuthLayout>

            <h1 className="text-3xl font-bold">
                Verify your email
            </h1>


            <p className="mt-3 text-slate-400">
                Enter the verification code sent to
                your account email.
            </p>


            {error && (
                <div
                    className="
                        mt-6
                        rounded-lg
                        border
                        border-red-500/30
                        bg-red-500/10
                        p-3
                        text-sm
                        text-red-300
                    "
                    role="alert"
                >
                    {error}
                </div>
            )}


            <form
                onSubmit={handleSubmit}
                className="mt-8 space-y-5"
            >

                <input
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    value={code}
                    onChange={(event) =>
                        setCode(
                            event.target.value
                        )
                    }
                    placeholder="Enter verification code"
                    disabled={loading}
                    className="
                        w-full
                        rounded-xl
                        border
                        border-slate-700
                        bg-slate-900
                        px-4
                        py-3
                        text-center
                        tracking-[0.3em]
                        outline-none
                        focus:border-white
                        disabled:opacity-50
                    "
                />


                <button
                    type="submit"
                    disabled={loading}
                    className="
                        w-full
                        rounded-xl
                        bg-white
                        px-4
                        py-3
                        font-semibold
                        text-slate-950
                        hover:bg-slate-200
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                    "
                >
                    {loading
                        ? "Verifying..."
                        : "Verify email"}
                </button>

            </form>


            <p className="mt-8 text-center text-sm text-slate-400">
                Already verified?{" "}

                <Link
                    to="/login"
                    className="
                        text-white
                        hover:underline
                    "
                >
                    Sign in
                </Link>
            </p>

        </AuthLayout>
    );
}