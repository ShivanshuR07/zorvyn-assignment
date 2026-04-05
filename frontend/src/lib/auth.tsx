import {
  createContext,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";

import { api } from "./api";
import type { AuthUser, LoginResponse } from "../types/api";

const STORAGE_KEY = "zorvyn.auth";

interface AuthContextValue {
  token: string | null;
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => void;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readStoredAuth() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { token: null, user: null };
  }

  try {
    return JSON.parse(raw) as { token: string | null; user: AuthUser | null };
  } catch {
    return { token: null, user: null };
  }
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = readStoredAuth();
    setToken(stored.token);
    setUser(stored.user);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (token && user) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user }));
      return;
    }

    window.localStorage.removeItem(STORAGE_KEY);
  }, [token, user]);

  async function login(email: string, password: string) {
    const result = await api.login(email, password);
    setToken(result.access_token);
    setUser(result.user);
    return result;
  }

  function logout() {
    setToken(null);
    setUser(null);
    window.localStorage.removeItem(STORAGE_KEY);
  }

  async function refreshMe() {
    if (!token) {
      return;
    }

    try {
      const nextUser = await api.me(token);
      setUser(nextUser);
    } catch {
      logout();
    }
  }

  return (
    <AuthContext.Provider value={{ token, user, isLoading, login, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
