import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "../auth/ProtectedRoute";
import RoleRoute from "../auth/RoleRoute";

import LoginUser from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import VerifyEmail from "../pages/auth/VerifyEmail";
import ForgotPassword from "../pages/auth/ForgotPassword";
import ChangePassword from "../pages/auth/ChangePassword";

import Unauthorized from "../pages/Unauthorized";

import UserDashboard from "../pages/user/UserDashboard";
import Profile from "../pages/user/Profile";
import ProfileEdit from "../pages/user/ProfileEdit";
import CareerAssistant from "../pages/user/CareerAssistant";
import About from "../pages/user/About";

import AdminDashboard from "../pages/admin/AdminDashboard";
import SuperAdminDashboard from "../pages/super-admin/SuperAdminDashboard";

import AdminLogin from "../pages/auth/AdminLogin";
import SuperAdminLogin from "../pages/auth/SuperAdminLogin";

import UserLayout from "../layouts/UserLayout";
import AdminLayout from "../layouts/AdminLayout";
import SuperAdminLayout from "../layouts/SuperAdminLayout";

export default function AppRoutes() {
  return (
    <Routes>

      {/* =========================
          PUBLIC AUTH
      ========================== */}

      <Route
        path="/login"
        element={<LoginUser />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      <Route
        path="/verify-email"
        element={<VerifyEmail />}
      />

      <Route
        path="/forgot-password"
        element={<ForgotPassword />}
      />

      <Route
        path="/change-password"
        element={<ChangePassword />}
      />

      <Route
        path="/unauthorized"
        element={<Unauthorized />}
      />


      {/* =========================
          USER
      ========================== */}

      <Route element={<ProtectedRoute />}>

        <Route element={<UserLayout />}>

          <Route
            path="/dashboard"
            element={<UserDashboard />}
          />

          <Route
            path="/profile"
            element={<Profile />}
          />

          <Route
            path="/profile/edit"
            element={<ProfileEdit />}
          />

          <Route
            path="/career-assistant"
            element={<CareerAssistant />}
          />

          <Route
            path="/about"
            element={<About />}
          />

        </Route>

      </Route>


      {/* =========================
          ADMIN
      ========================== */}

      <Route
        element={
          <RoleRoute
            allowedRoles={[
              "ADMIN",
              "SUPER_ADMIN",
            ]}
          />
        }
      >
        <Route element={<AdminLayout />}>

          <Route
            path="/admin"
            element={<AdminDashboard />}
          />

        </Route>
      </Route>


      {/* =========================
          SUPER ADMIN
      ========================== */}

      <Route
        element={
          <RoleRoute
            allowedRoles={["SUPER_ADMIN"]}
          />
        }
      >
        <Route element={<SuperAdminLayout />}>

          <Route
            path="/super-admin"
            element={<SuperAdminDashboard />}
          />

        </Route>
      </Route>


      {/* =========================
          DEFAULT
      ========================== */}

      <Route
        path="/"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />


      {/* =========================
          ADMIN LOGIN
      ========================== */}

      <Route
        path="/admin/login"
        element={<AdminLogin />}
      />

      <Route
        path="/super-admin/login"
        element={<SuperAdminLogin />}
      />

    </Routes>
  );
}