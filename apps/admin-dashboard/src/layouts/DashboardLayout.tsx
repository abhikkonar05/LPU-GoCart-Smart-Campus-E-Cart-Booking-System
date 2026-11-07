import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  Car,
  Route,
  Camera,
  Ticket,
  CreditCard,
  LogOut,
  Bell,
  ShieldCheck,
  Radio
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/tracking', label: 'Live Tracking', icon: MapPin },
  { to: '/carts', label: 'E-Cart Fleet', icon: Car },
  { to: '/routes', label: 'Routes & Stops', icon: Route },
  { to: '/cctv', label: 'CCTV Monitoring', icon: Camera },
  { to: '/bookings', label: 'Bookings', icon: Ticket },
  { to: '/payments', label: 'Payments', icon: CreditCard },
];

export const DashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('lpu_admin_user') || '{"full_name": "Fleet Dispatcher", "email": "admin@lpu.in"}');

  const handleLogout = () => {
    localStorage.removeItem('lpu_admin_token');
    localStorage.removeItem('lpu_admin_user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 select-none">
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-blue-500/20">
            LG
          </div>
          <div>
            <h1 className="font-extrabold text-white text-lg tracking-tight">LPU GoCart</h1>
            <p className="text-xs text-blue-400 font-semibold tracking-wider uppercase">Campus Fleet HQ</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'hover:bg-slate-800 hover:text-white text-slate-400'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Live System Indicator */}
        <div className="p-4 mx-4 mb-4 bg-slate-800/60 rounded-xl border border-slate-700/50">
          <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-400 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>TELEMETRY ONLINE</span>
          </div>
          <p className="text-[11px] text-slate-400">Lovely Professional University Campus Grid Active</p>
        </div>

        {/* User Card */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center font-bold text-sm">
              {user.full_name?.charAt(0) || 'A'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-white truncate">{user.full_name}</p>
              <p className="text-xs text-slate-500 truncate">{user.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between z-20">
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
              Phagwara Campus: Live (31.2536° N, 75.7037° E)
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-100 rounded-lg text-xs font-semibold text-slate-700">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>Admin Role</span>
            </div>
            <button className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500"></span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

