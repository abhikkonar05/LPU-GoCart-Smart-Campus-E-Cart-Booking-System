import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('lpu_gocart_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('lpu_gocart_token') || null;
  });

  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', {
        email: email.trim().toLowerCase(),
        password,
      });

      const data = response.data;
      const userObj = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role, // ADMIN, DRIVER, CUSTOMER
      };

      setToken(data.access_token);
      setUser(userObj);

      localStorage.setItem('lpu_gocart_token', data.access_token);
      localStorage.setItem('lpu_gocart_user', JSON.stringify(userObj));

      return { success: true, role: data.role };
    } catch (err) {
      const detail = err.response?.data?.detail || 'Authentication failed. Please check credentials.';
      return { success: false, error: detail };
    } finally {
      setLoading(false);
    }
  };

  const register = async (formData) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/register', formData);
      const data = response.data;
      const userObj = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role,
      };

      setToken(data.access_token);
      setUser(userObj);

      localStorage.setItem('lpu_gocart_token', data.access_token);
      localStorage.setItem('lpu_gocart_user', JSON.stringify(userObj));

      return { success: true, role: data.role };
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed.';
      return { success: false, error: detail };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('lpu_gocart_token');
    localStorage.removeItem('lpu_gocart_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role || null,
        isAuthenticated: !!token && !!user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
