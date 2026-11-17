import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { Car, MapPin, BatteryCharging, ArrowRight, ShieldCheck, Filter, Users } from 'lucide-react';

export default function FindCarts() {
  const [carts, setCarts] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCartsAndRoutes = async () => {
      try {
        const [cRes, rRes] = await Promise.all([
          api.get('/carts'),
          api.get('/routes')
        ]);
        setCarts(cRes.data);
        setRoutes(rRes.data);
      } catch (err) {
        console.error('Error fetching carts:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCartsAndRoutes();
  }, []);

  const filteredCarts = selectedRoute === 'ALL'
    ? carts
    : carts.filter((c) => c.current_route_id === selectedRoute);

  return (
    <div className="space-y-6 py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Find Nearby Campus E-Carts
          </h1>
          <p className="text-sm text-slate-500">
            View live operating carts, real-time seat counts, and reserve your ride.
          </p>
        </div>

        {/* Route Filter Dropdown */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          >
            <option value="ALL">All Campus Routes</option>
            {routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.code} - {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid of Carts */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-56 bg-slate-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filteredCarts.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 space-y-3">
          <Car className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-700">No Carts Available on Selected Route</h3>
          <p className="text-xs text-slate-400">Please choose "All Campus Routes" or try again shortly.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCarts.map((cart) => (
            <div
              key={cart.id}
              className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-sm font-black px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-100">
                    {cart.cart_number}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg">
                    <BatteryCharging className="w-4 h-4" />
                    <span>{cart.battery_percentage}%</span>
                  </div>
                </div>

                <h3 className="text-lg font-extrabold text-slate-900">{cart.name}</h3>
                <span className="text-xs text-slate-400 font-medium block mb-3">{cart.model}</span>

                <div className="space-y-2 py-3 border-y border-slate-100 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-blue-600" /> Current Route:
                    </span>
                    <span className="font-bold text-slate-800">{cart.route_name || 'Campus Loop'}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-400" /> Available Capacity:
                    </span>
                    <span className="font-black text-blue-600">
                      {cart.available_seats} of {cart.total_seats} seats free
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-5 flex gap-2">
                <Link
                  to={`/customer/book/${cart.id}`}
                  className="flex-1 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-600/20 transition flex items-center justify-center gap-2"
                >
                  <span>Book Seat</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <Link
                  to="/customer/tracking"
                  className="py-2.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center justify-center"
                  title="Track Live on Map"
                >
                  <MapPin className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
