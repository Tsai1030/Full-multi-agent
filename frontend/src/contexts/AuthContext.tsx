"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { authApi, setAccessToken, subscriptionApi } from "@/lib/api";
import type { BirthData, SubscriptionInfo, TokenResponse, User, ZiweiChart } from "@/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  subscription: SubscriptionInfo | null;
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
  refreshSubscription: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);

  const fetchSubscription = useCallback(async () => {
    try {
      const info = await subscriptionApi.me();
      setSubscription(info);
    } catch {
      setSubscription(null);
    }
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const ok = await authApi.refresh();
        if (ok && active) {
          const me = await authApi.me();
          if (active) {
            setUser(me);
            await fetchSubscription();
          }
        }
      } catch {
        /* not logged in */
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [fetchSubscription]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    setAccessToken(res.access_token);
    setUser(res.user);
    await fetchSubscription();
    return res;
  }, [fetchSubscription]);

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
      await fetchSubscription();
    },
    [fetchSubscription],
  );

  const googleLogin = useCallback(async (credential: string) => {
    const res = await authApi.google(credential);
    setAccessToken(res.access_token);
    setUser(res.user);
    await fetchSubscription();
    return res;
  }, [fetchSubscription]);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      setAccessToken(null);
      setUser(null);
      setSubscription(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, subscription, login, register, googleLogin, logout, refreshSubscription: fetchSubscription }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
