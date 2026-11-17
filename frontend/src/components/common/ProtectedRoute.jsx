import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to correct dashboard based on actual role
    if (role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
    if (role === 'DRIVER') return <Navigate to="/driver/dashboard" replace />;
    return <Navigate to="/customer/dashboard" replace />;
  }

  return children;
}
