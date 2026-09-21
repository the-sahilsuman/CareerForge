import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";

const userItems = [
  { label: "Dashboard", path: "/dashboard", icon: GridIcon },
  { label: "Profile", path: "/profile", icon: UserIcon },
  { label: "Career Assistant", path: "/career-assistant", icon: SparkIcon },
  { label: "About Me", path: "/about", icon: InfoIcon },
];

const roleConfig = {
  USER: { title: "CareerForge", items: userItems, loginPath: "/login" },
  ADMIN: {
    title: "CareerForge Admin",
    items: [
      { label: "Dashboard", path: "/admin", icon: GridIcon },
      { label: "Users", path: "/admin/users", icon: UserIcon },
      { label: "Applications", path: "/admin/applications", icon: BriefcaseIcon },
      { label: "Analytics", path: "/admin/analytics", icon: ChartIcon },
      { label: "Monitoring", path: "/admin/monitoring", icon: ActivityIcon },
    ],
    loginPath: "/admin/login",
  },
  SUPER_ADMIN: {
    title: "CareerForge Control",
    items: [
      { label: "Dashboard", path: "/super-admin", icon: GridIcon },
      { label: "Users", path: "/super-admin/users", icon: UserIcon },
      { label: "Administrators", path: "/super-admin/admins", icon: ShieldIcon },
      { label: "AI / RAG", path: "/super-admin/ai", icon: SparkIcon },
      { label: "Evaluations", path: "/super-admin/evaluations", icon: ChartIcon },
      { label: "Audit Logs", path: "/super-admin/audit-logs", icon: ActivityIcon },
    ],
    loginPath: "/super-admin/login",
  },
};

export default function Sidebar({ role, theme = "dark", onToggleTheme }) {
  const config = roleConfig[role];
  const navigate = useNavigate();
  const { logout } = useAuth();

  if (!config) return null;

  const handleLogout = () => {
    logout();
    navigate(config.loginPath, { replace: true });
  };

  const isUser = role === "USER";

  return (
    <>
      <aside className="cf-sidebar">
        <button type="button" className="cf-brand" onClick={() => navigate(isUser ? "/dashboard" : config.items[0]?.path || "/")}>
          <span className="cf-brand-mark"><LogoMark /></span>
          <span>
            <strong>{config.title}</strong>
            {isUser && <small>Build. Apply. Grow.</small>}
          </span>
        </button>

        <nav className="cf-nav" aria-label="Primary navigation">
          {config.items.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/dashboard" || path === "/admin" || path === "/super-admin"}
              className={({ isActive }) => `cf-nav-item ${isActive ? "active" : ""}`}
            >
              <Icon />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="cf-sidebar-bottom">
          {isUser && (
            <button type="button" className="cf-nav-item cf-action-button" onClick={onToggleTheme}>
              {theme === "dark" ? <SunIcon /> : <MoonIcon />}
              <span>{theme === "dark" ? "Light mode" : "Dark mode"}</span>
              <span className="cf-mode-pill">{theme === "dark" ? "Dark" : "Light"}</span>
            </button>
          )}

          <button type="button" className="cf-nav-item cf-logout" onClick={handleLogout}>
            <LogoutIcon />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {isUser && (
        <nav className="cf-mobile-nav" aria-label="Mobile navigation">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""}>
            <GridIcon /><span>Home</span>
          </NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>
            <UserIcon /><span>Profile</span>
          </NavLink>
          <NavLink to="/about" className={({ isActive }) => isActive ? "active" : ""}>
            <InfoIcon /><span>About</span>
          </NavLink>
        </nav>
      )}
    </>
  );
}

function LogoMark() {
  return <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M7 23.5 13.5 17l4.5 4.5L25 14.5" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 23.5V9h18v5.5" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"/><circle cx="13.5" cy="17" r="2" fill="currentColor"/><circle cx="25" cy="14.5" r="2" fill="currentColor"/></svg>;
}
function GridIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>; }
function UserIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>; }
function SparkIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z"/></svg>; }
function InfoIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 10v6"/><path d="M12 7.5h.01"/></svg>; }
function BriefcaseIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/></svg>; }
function ChartIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 2 5-6"/></svg>; }
function ActivityIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h4l2-6 4 12 2-6h6"/></svg>; }
function ShieldIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/></svg>; }
function SunIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>; }
function MoonIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5Z"/></svg>; }
function LogoutIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5"/><path d="M14 8l4 4-4 4M18 12H8"/></svg>; }
