import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, Lock, Mail, ArrowRight, CheckCircle2, AlertCircle, Car, User } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('customer@lpu.in');
  const [password, setPassword] = useState('customer123');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLoginSubmit = async (e) => {
    if (e) e.preventDefault();
    setError('');
    setIsSubmitting(true);

    const res = await login(email, password);
    setIsSubmitting(false);

    if (res.success) {
      // Redirect based on role
      if (res.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else if (res.role === 'DRIVER') {
        navigate('/driver/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } else {
      setError(res.error || 'Authentication failed. Please verify credentials.');
    }
  };

  const quickLoginAs = (roleEmail, rolePassword) => {
    setEmail(roleEmail);
    setPassword(rolePassword);
    setError('');
    // Submit with selected credentials
    setIsSubmitting(true);
    login(roleEmail, rolePassword).then((res) => {
      setIsSubmitting(false);
      if (res.success) {
        if (res.role === 'ADMIN') navigate('/admin/dashboard');
        else if (res.role === 'DRIVER') navigate('/driver/dashboard');
        else navigate('/customer/dashboard');
      } else {
        setError(res.error || 'Authentication failed.');
      }
    });
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950">
      <div className="max-w-md w-full space-y-6">
        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 border border-slate-100">
          <div className="text-center space-y-2 mb-6">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-500/30">
              <Shield className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">
              LPU GoCart
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Smart Campus E-Cart Transit & Booking Portal
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. customer@lpu.in"
                  required
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm font-medium text-slate-900 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm font-medium text-slate-900 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In to Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* One-Click Quick Logins */}
          <div className="mt-6 pt-6 border-t border-slate-100">
            <span className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center mb-3">
              ⚡ 1-Click Demo Login
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => quickLoginAs('customer@lpu.in', 'customer123')}
                className="p-2.5 rounded-xl border border-blue-200 bg-blue-50/60 hover:bg-blue-100 text-blue-800 transition text-center flex flex-col items-center gap-1"
              >
                <User className="w-4 h-4 text-blue-600" />
                <span className="text-[11px] font-bold">Student</span>
              </button>
              <button
                type="button"
                onClick={() => quickLoginAs('driver@lpu.in', 'driver123')}
                className="p-2.5 rounded-xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100 text-emerald-800 transition text-center flex flex-col items-center gap-1"
              >
                <Car className="w-4 h-4 text-emerald-600" />
                <span className="text-[11px] font-bold">Driver</span>
              </button>
              <button
                type="button"
                onClick={() => quickLoginAs('admin@lpu.in', 'admin123')}
                className="p-2.5 rounded-xl border border-amber-200 bg-amber-50/60 hover:bg-amber-100 text-amber-800 transition text-center flex flex-col items-center gap-1"
              >
                <Shield className="w-4 h-4 text-amber-600" />
                <span className="text-[11px] font-bold">Admin</span>
              </button>
            </div>
          </div>

          <div className="mt-4 text-center">
            <span className="text-xs text-slate-500">Don't have an account? </span>
            <Link to="/register" className="text-xs font-bold text-blue-600 hover:underline">
              Create Student Account
            </Link>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400">
          Lovely Professional University, Phagwara, Punjab
        </p>
      </div>
    </div>
  );
}
