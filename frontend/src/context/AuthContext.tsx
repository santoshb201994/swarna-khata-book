import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('user_info');
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.clear();
      }
    }
    setIsLoading(false);
  }, [token]);

  const login = async (username: string, password: string) => {
    const res = await api.post('/auth/token/', { username, password });
    const { access, refresh, user: userData } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user_info', JSON.stringify(userData));
    setToken(access);
    setUser(userData);
  };

  const logout = async () => {
    // If there is an active POS mobile scanner pairing, revoke it on server
    const activeSessionId = sessionStorage.getItem('pos_active_session_id');
    if (activeSessionId) {
      try {
        await api.post('/pos/pairing/revoke/', { session_id: activeSessionId });
      } catch {
        // ignore
      }
    }
    sessionStorage.removeItem('pos_active_session_id');
    localStorage.clear();
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
