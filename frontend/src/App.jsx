import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Navbar from './components/layout/Navbar';

// Public Pages
import Login from './pages/public/Login';
import Register from './pages/public/Register';

// Customer Pages
import CustomerDashboard from './pages/customer/Dashboard';
import FindCarts from './pages/customer/FindCarts';
import SeatBooking from './pages/customer/SeatBooking';
import MyBookings from './pages/customer/MyBookings';
import LiveTracking from './pages/customer/LiveTracking';

// Driver Pages
import DriverDashboard from './pages/driver/Dashboard';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';

import { Car, MapPin, ShieldCheck, ArrowRight, Sparkles } from 'lucide-react';

function LandingPage() {
  return (
    <div className="py-12 px-4 max-w-5xl mx-auto space-y-12">
      {/* Hero */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>LPU GoCart Official Smart Transit Portal</span>
        </div>
        <h1 className="text-4xl md:text-6xl font-black text-slate-900 tracking-tight max-w-3xl mx-auto">
          Smart Campus E-Cart Booking & Live Tracking
        </h1>
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Reserve your electric shuttle seats in advance, lock your seat with a guaranteed 5-minute atomic hold, carry luggage with ease, and track cart arrivals in real time across Lovely Professional University.
        </p>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <Link
            to="/login"
            className="px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-extrabold rounded-2xl shadow-xl shadow-blue-600/30 transition flex items-center gap-2 text-sm"
          >
            <span>Sign In to GoCart</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/register"
            className="px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-extrabold rounded-2xl shadow-sm transition text-sm"
          >
            Create Student Account
          </Link>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Car className="w-5 h-5" />
          </div>
          <h3 className="font-extrabold text-slate-900 text-base">Atomic 5-Min Seat Locking</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Pick your exact seat (S1 through S6). Our backend locks the seat exclusively for you for 5 minutes during checkout.
          </p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <MapPin className="w-5 h-5" />
          </div>
          <h3 className="font-extrabold text-slate-900 text-base">Real-Time GPS Tracking</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Continuous browser geolocation telemetry streams cart locations right to OpenStreetMap Leaflet live view.
          </p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="font-extrabold text-slate-900 text-base">QR Boarding Pass Verification</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Instant digital ticket generation with cryptographic QR token verification for safe, verified boarding.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
          <Navbar />

          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Customer Routes */}
              <Route
                path="/customer/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}>
                    <CustomerDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/customer/find-carts"
                element={
                  <ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}>
                    <FindCarts />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/customer/book/:cartId"
                element={
                  <ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}>
                    <SeatBooking />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/customer/bookings"
                element={
                  <ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}>
                    <MyBookings />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/customer/tracking"
                element={
                  <ProtectedRoute allowedRoles={['CUSTOMER', 'ADMIN']}>
                    <LiveTracking />
                  </ProtectedRoute>
                }
              />

              {/* Driver Routes */}
              <Route
                path="/driver/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['DRIVER', 'ADMIN']}>
                    <DriverDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Admin Routes */}
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 font-medium mt-12">
            Lovely Professional University, Phagwara, Punjab • LPU GoCart Transportation Platform
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
