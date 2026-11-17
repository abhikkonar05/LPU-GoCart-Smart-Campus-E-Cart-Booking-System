import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { Shield, Car, Users, Ticket, IndianRupee, BatteryCharging, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [carts, setCarts] = useState([]);
  const [users, setUsers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [activeTab, setActiveTab] = useState('fleet'); // fleet, users, bookings
  const [loading, setLoading] = useState(true);

  const fetchAdminData = async () => {
    try {
      const [mRes, cRes, uRes, bRes] = await Promise.all([
        api.get('/admin/metrics'),
        api.get('/admin/carts'),
        api.get('/admin/users'),
        api.get('/admin/bookings'),
      ]);
      setMetrics(mRes.data);
      setCarts(cRes.data);
      setUsers(uRes.data);
      setBookings(bRes.data);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleUpdateCartStatus = async (cartId, newStatus) => {
    try {
      await api.put(`/admin/carts/${cartId}`, {
        cart_status: newStatus,
      });
      fetchAdminData();
    } catch (err) {
      alert('Failed to update cart status.');
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
              Fleet Dispatcher
            </span>
            <span className="text-xs text-slate-400 font-medium">• Lovely Professional University</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Central Fleet Administration
          </h1>
        </div>

        <button
          onClick={fetchAdminData}
          className="px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-xl shadow-sm transition flex items-center gap-1.5 self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Fleet Data</span>
        </button>
      </div>

      {/* KPI Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase">Total Carts</span>
            <Car className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{metrics?.total_carts || 0}</div>
          <span className="text-[11px] text-emerald-600 font-bold mt-1 block">
            {metrics?.active_carts || 0} currently operating
          </span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase">Available Seats</span>
            <Users className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{metrics?.available_seats || 0}</div>
          <span className="text-[11px] text-slate-500 font-medium mt-1 block">Across active fleet</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase">Today's Bookings</span>
            <Ticket className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{metrics?.total_bookings_today || 0}</div>
          <span className="text-[11px] text-slate-500 font-medium mt-1 block">Rides scheduled today</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase">Total Revenue</span>
            <IndianRupee className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">₹{metrics?.total_revenue_today || 0}</div>
          <span className="text-[11px] text-emerald-600 font-bold mt-1 block">Demo transit receipts</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-200 px-6 pt-4 gap-6 text-xs font-bold">
          <button
            onClick={() => setActiveTab('fleet')}
            className={`pb-4 border-b-2 transition ${
              activeTab === 'fleet' ? 'border-blue-600 text-blue-600 font-extrabold' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Vehicle Inventory ({carts.length})
          </button>
          <button
            onClick={() => setActiveTab('bookings')}
            className={`pb-4 border-b-2 transition ${
              activeTab === 'bookings' ? 'border-blue-600 text-blue-600 font-extrabold' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Passenger Bookings ({bookings.length})
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`pb-4 border-b-2 transition ${
              activeTab === 'users' ? 'border-blue-600 text-blue-600 font-extrabold' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Users & Drivers ({users.length})
          </button>
        </div>

        <div className="p-6">
          {/* Fleet Tab */}
          {activeTab === 'fleet' && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider font-extrabold">
                    <th className="pb-3">Cart Number</th>
                    <th className="pb-3">Name / Model</th>
                    <th className="pb-3">Battery</th>
                    <th className="pb-3">Assigned Driver</th>
                    <th className="pb-3">Route</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {carts.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-3 font-mono font-black text-blue-600">{c.cart_number}</td>
                      <td className="py-3">
                        <strong className="text-slate-900 block">{c.name}</strong>
                        <span className="text-[11px] text-slate-400">{c.model}</span>
                      </td>
                      <td className="py-3">
                        <span className="flex items-center gap-1 font-bold text-emerald-600">
                          <BatteryCharging className="w-3.5 h-3.5" /> {c.battery_percentage}%
                        </span>
                      </td>
                      <td className="py-3 font-medium text-slate-700">
                        {c.driver_name || <span className="text-slate-400 italic">Unassigned</span>}
                      </td>
                      <td className="py-3 font-medium text-slate-700">
                        {c.route_name || <span className="text-slate-400 italic">Loop Line</span>}
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          c.cart_status === 'AVAILABLE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                          c.cart_status === 'ON_TRIP' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                          'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                          {c.cart_status}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <select
                          value={c.cart_status}
                          onChange={(e) => handleUpdateCartStatus(c.id, e.target.value)}
                          className="px-2 py-1 rounded-lg border border-slate-200 text-[11px] font-bold text-slate-700 bg-white"
                        >
                          <option value="AVAILABLE">Set AVAILABLE</option>
                          <option value="ON_TRIP">Set ON_TRIP</option>
                          <option value="MAINTENANCE">Set MAINTENANCE</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Bookings Tab */}
          {activeTab === 'bookings' && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider font-extrabold">
                    <th className="pb-3">Code</th>
                    <th className="pb-3">Passenger</th>
                    <th className="pb-3">Cart</th>
                    <th className="pb-3">Type</th>
                    <th className="pb-3">Route Stops</th>
                    <th className="pb-3">Fare</th>
                    <th className="pb-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {bookings.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-3 font-mono font-bold text-blue-600">{b.booking_code}</td>
                      <td className="py-3 font-semibold text-slate-900">{b.passenger_name}</td>
                      <td className="py-3 font-mono text-slate-700">{b.cart_number}</td>
                      <td className="py-3 font-medium text-slate-600">{b.booking_type}</td>
                      <td className="py-3 text-slate-600">
                        {b.pickup} → {b.drop}
                      </td>
                      <td className="py-3 font-bold text-slate-900">₹{b.fare_amount}</td>
                      <td className="py-3 text-right">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          b.status === 'CONFIRMED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                          b.status === 'CHECKED_IN' || b.status === 'BOARDED' ? 'bg-blue-50 text-blue-700' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {b.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider font-extrabold">
                    <th className="pb-3">Full Name</th>
                    <th className="pb-3">Email Address</th>
                    <th className="pb-3">Phone</th>
                    <th className="pb-3">Role</th>
                    <th className="pb-3 text-right">Active</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-3 font-bold text-slate-900">{u.full_name}</td>
                      <td className="py-3 font-mono text-slate-600">{u.email}</td>
                      <td className="py-3 text-slate-600">{u.phone_number || 'N/A'}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          u.role === 'ADMIN' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                          u.role === 'DRIVER' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                          'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <span className="font-bold text-emerald-600">Active</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
