"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { authApi, setAccessToken } from "@/lib/api";
import type { BirthData, TokenResponse, User, ZiweiChart } from "@/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean; // 初次嘗試 refresh 中
  login: (email: string, password: string) => Promise<TokenResponse>;
  register: (
    email: string,
    password: string,
    displayName: string,
    birthData: BirthData,
    chart: ZiweiChart,
  ) => Promise<void>;
  googleLogin: (credential: string) => Promise<TokenResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 載入時用 httpOnly refresh cookie 嘗試恢復登入
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const ok = await authApi.refresh();
        if (ok && active) {
          const me = await authApi.me();
          if (active) setUser(me);
        }
      } catch {
        /* 未登入，忽略 */
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    setAccessToken(res.access_token);
    setUser(res.user);
    return res;
  }, []);

  const register = useCallback(
    async (
      email: string,
      password: string,
      displayName: string,
      birthData: BirthData,
      chart: ZiweiChart,
    ) => {
      const res = await authApi.register(email, password, displayName, birthData, chart);
      setAccessToken(res.access_token);
      setUser(res.user);
    },
    [],
  );

  const googleLogin = useCallback(async (credential: string) => {
    const res = await authApi.google(credential);
    setAccessToken(res.access_token);
    setUser(res.user);
    return res;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, googleLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
