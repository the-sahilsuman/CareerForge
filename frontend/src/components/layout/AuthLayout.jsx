import { Link } from "react-router-dom";

export default function AuthLayout({ children }) {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="grid min-h-screen lg:grid-cols-2">

        {/* Branding section */}
        <section className="hidden lg:flex flex-col justify-between p-12 bg-slate-900">
          <div>
            <Link
              to="/login"
              className="text-2xl font-bold tracking-tight"
            >
              CareerForge
            </Link>

            <p className="mt-4 max-w-md text-slate-400">
              Build your professional profile, manage
              applications and use AI to accelerate your
              job search.
            </p>
          </div>

          <p className="text-sm text-slate-500">
            Your career. Your profile. Your opportunities.
          </p>
        </section>

        {/* Form section */}
        <section className="flex items-center justify-center p-6 sm:p-10">
          <div className="w-full max-w-md">
            <div className="mb-8 lg:hidden">
              <Link
                to="/login"
                className="text-2xl font-bold"
              >
                CareerForge
              </Link>
            </div>

            {children}
          </div>
        </section>

      </div>
    </main>
  );
}
