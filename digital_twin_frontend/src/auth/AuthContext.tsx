import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { getMe, login, type User } from "../api/auth";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  loginUser: (
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateCurrentUser: (
    user: User
  ) => void;
}

const AuthContext = createContext<
  AuthContextValue | undefined
>(undefined);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      setLoading(false);
      return;
    }

    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(
          "access_token"
        );
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const loginUser = async (
    email: string,
    password: string
  ) => {
    const result = await login({
      email,
      password,
    });

    localStorage.setItem(
      "access_token",
      result.access_token
    );

    setUser(result.user);
  };

  const logout = () => {
    localStorage.removeItem(
      "access_token"
    );

    setUser(null);
  };


  const refreshUser =
    async () => {

      const result =
        await getMe();

      setUser(
        result
      );
    };


  const updateCurrentUser =
    (
      nextUser: User
    ) => {

      setUser(
        nextUser
      );
    };


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        loginUser,
        logout,
        refreshUser,
        updateCurrentUser,
      }}
    >
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