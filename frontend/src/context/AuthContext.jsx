import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('bioxai_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('bioxai_token');
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('bioxai_user', JSON.stringify(res.data));
        } catch (err) {
          console.error("Session verification failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('bioxai_token', access_token);
    localStorage.setItem('bioxai_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('bioxai_token');
    localStorage.removeItem('bioxai_user');
    setUser(null);
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) return roles.includes(user.role);
    return user.role === roles;
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      hasRole,
      isAdmin: user?.role === 'ADMIN',
      isHOD: user?.role === 'HOD',
      isMentor: user?.role === 'MENTOR',
      isStudent: user?.role === 'STUDENT',
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
