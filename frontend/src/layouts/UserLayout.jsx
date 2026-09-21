import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import ChatButton from "../components/common/ChatButton";

export default function UserLayout() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("careerforge-theme") || "dark";
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("careerforge-theme", theme);
    } catch {
      // Theme persistence is a convenience; the UI still works without it.
    }
  }, [theme]);

  return (
    <div className={`cf-app ${theme === "light" ? "cf-light" : ""}`}>
      <Sidebar
        role="USER"
        theme={theme}
        onToggleTheme={() => setTheme((current) => current === "dark" ? "light" : "dark")}
      />

      <main className="cf-main">
        <Outlet />
        <footer className="cf-footer">
          <span>© {new Date().getFullYear()} CareerForge</span>
          <span>Build your career. Apply with confidence.</span>
        </footer>
      </main>

      <ChatButton />
    </div>
  );
}
