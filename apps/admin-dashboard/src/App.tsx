import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { LiveTracking } from './pages/LiveTracking';
import { Carts } from './pages/Carts';
import { Routes as RoutesPage } from './pages/Routes';
import { CCTV } from './pages/CCTV';
import { Bookings } from './pages/Bookings';
import { Payments } from './pages/Payments';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('lpu_admin_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="tracking" element={<LiveTracking />} />
          <Route path="carts" element={<Carts />} />
          <Route path="routes" element={<RoutesPage />} />
          <Route path="cctv" element={<CCTV />} />
          <Route path="bookings" element={<Bookings />} />
          <Route path="payments" element={<Payments />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;

