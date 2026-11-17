import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, MapPin, Ticket, LogOut, User, Car } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDashboardLink = () => {
    if (role === 'ADMIN') return '/admin/dashboard';
    if (role === 'DRIVER') return '/driver/dashboard';
    return '/customer/dashboard';
  };

  return (
    <header className="bg-slate-900 text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to={isAuthenticated ? getDashboardLink() : "/"} className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-black text-xl shadow-md">
            LG
          </div>
          <div>
            <span className="font-extrabold text-lg tracking-tight flex items-center gap-1.5">
              LPU GoCart
              {role && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                  role === 'ADMIN' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                  role === 'DRIVER' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                  'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                }`}>
                  {role}
                </span>
              )}
            </span>
            <span className="block text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
              Lovely Professional University
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center space-x-4 sm:space-x-6 text-sm font-semibold">
          {isAuthenticated ? (
            <>
              {role === 'CUSTOMER' && (
                <>
                  <Link to="/customer/dashboard" className="text-slate-300 hover:text-white transition flex items-center gap-1.5">
                    <Car className="w-4 h-4" /> Book Cart
                  </Link>
                  <Link to="/customer/bookings" className="text-slate-300 hover:text-white transition flex items-center gap-1.5">
                    <Ticket className="w-4 h-4" /> My Tickets
                  </Link>
                  <Link to="/customer/tracking" className="text-slate-300 hover:text-white transition flex items-center gap-1.5">
                    <MapPin className="w-4 h-4" /> Live Map
                  </Link>
                </>
              )}

              {role === 'DRIVER' && (
                <>
                  <Link to="/driver/dashboard" className="text-slate-300 hover:text-white transition flex items-center gap-1.5">
                    <Car className="w-4 h-4" /> Driver Console
                  </Link>
                </>
              )}

              {role === 'ADMIN' && (
                <>
                  <Link to="/admin/dashboard" className="text-slate-300 hover:text-white transition flex items-center gap-1.5">
                    <Shield className="w-4 h-4" /> Admin Console
                  </Link>
                </>
              )}

              {/* User badge & Logout */}
              <div className="flex items-center gap-3 pl-2 border-l border-slate-700">
                <span className="text-xs text-slate-300 hidden md:inline-block font-medium">
                  {user?.full_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-red-600/80 rounded-lg text-xs font-bold transition flex items-center gap-1 text-slate-200 hover:text-white"
                  title="Sign Out"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/" className="text-slate-300 hover:text-white transition">Home</Link>
              <Link
                to="/login"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-xl text-white font-bold transition shadow-md shadow-blue-600/20"
              >
                Sign In
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
