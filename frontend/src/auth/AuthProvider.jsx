import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getCurrentUser,
  getSession,
  getUserRole,
  logoutUser,
} from "./authService";

import {
  bootstrapCurrentUser,
} from "../services/api/authApi";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [role, setRole] = useState(null);

  const [backendUser, setBackendUser] =
    useState(null);

  const [loading, setLoading] =
    useState(true);


  /*
  |--------------------------------------------------------------------------
  | Load Cognito session + CareerForge user
  |--------------------------------------------------------------------------
  */

  const loadSession = async () => {
    try {
      const currentUser =
        getCurrentUser();

      if (!currentUser) {
        setUser(null);
        setSession(null);
        setRole(null);
        setBackendUser(null);

        return;
      }


      /*
       * Restore the Cognito session.
       */
      const currentSession =
        await getSession();


      /*
       * Get the Cognito role/group.
       *
       * This is currently kept for frontend
       * navigation/authorization.
       */
      const currentRole =
        await getUserRole();


      /*
       * Cognito authentication succeeded.
       *
       * Now bootstrap the user in the
       * CareerForge PostgreSQL database.
       *
       * POST /api/v1/users/me
       */
      const localUser =
        await bootstrapCurrentUser();


      setUser(currentUser);
      setSession(currentSession);
      setRole(currentRole);

      setBackendUser(
        localUser?.data || localUser
      );

    } catch (error) {
      console.error(
        "Unable to restore authenticated session:",
        error
      );

      setUser(null);
      setSession(null);
      setRole(null);
      setBackendUser(null);
    }
  };


  /*
  |--------------------------------------------------------------------------
  | Restore session on application startup
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    loadSession().finally(() => {
      setLoading(false);
    });
  }, []);


  /*
  |--------------------------------------------------------------------------
  | Logout
  |--------------------------------------------------------------------------
  */

  const logout = () => {
    logoutUser();

    setUser(null);
    setSession(null);
    setRole(null);
    setBackendUser(null);
  };


  /*
  |--------------------------------------------------------------------------
  | Context value
  |--------------------------------------------------------------------------
  */

  const value = {
    user,
    session,
    role,

    /*
     * CareerForge database user.
     *
     * Example:
     *
     * backendUser.id
     * backendUser.user_id
     * backendUser.login_email
     * backendUser.role
     */
    backendUser,

    loading,

    isAuthenticated:
      Boolean(user && session),

    logout,

    refreshSession:
      loadSession,
  };


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}