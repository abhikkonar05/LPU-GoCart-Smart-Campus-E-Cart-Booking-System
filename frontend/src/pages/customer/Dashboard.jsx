import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { Car, MapPin, Ticket, BatteryCharging, ArrowRight, Clock, ShieldCheck, Sparkles } from 'lucide-react';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const [carts, setCarts] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cartsRes, routesRes, bookingsRes] = await Promise.all([
          api.get('/carts'),
          api.get('/routes'),
          api.get('/bookings/my'),
        ]);
        setCarts(cartsRes.data);
        setRoutes(routesRes.data);
        setBookings(bookingsRes.data);
      } catch (err) {
        console.error('Failed to load customer dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8 py-4">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-700 via-indigo-700 to-slate-900 rounded-3xl p-8 text-white shadow-xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-blue-200 border border-white/15">
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            LPU Smart Campus Transit Active
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight">
            Welcome back, {user?.full_name?.split(' ')[0]}! 👋
          </h1>
          <p className="text-sm text-blue-100/90 leading-relaxed">
            Need a ride to class, UniMall, or the hostels? Choose an e-cart, pick your seat with a 5-minute guaranteed lock, and track your driver in real time.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/customer/find-carts"
              className="px-5 py-2.5 bg-white text-blue-700 hover:bg-blue-50 font-bold rounded-xl shadow-lg transition flex items-center gap-2 text-sm"
            >
              <Car className="w-4 h-4" /> Book E-Cart Now
            </Link>
            <Link
              to="/customer/tracking"
              className="px-5 py-2.5 bg-blue-800/60 hover:bg-blue-800 text-white font-bold rounded-xl border border-white/20 transition flex items-center gap-2 text-sm"
            >
              <MapPin className="w-4 h-4" /> View Live Campus Map
            </Link>
          </div>
        </div>
      </div>

      {/* Active Digital Tickets Banner (if any) */}
      {bookings.filter((b) => b.status === 'CONFIRMED').length > 0 && (
        <div className="p-5 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
              <Ticket className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-emerald-900">
                You have {bookings.filter((b) => b.status === 'CONFIRMED').length} active confirmed boarding pass(es)
              </h3>
              <p className="text-xs text-emerald-700">
                Show your QR boarding pass to the cart driver before boarding.
              </p>
            </div>
          </div>
          <Link
            to="/customer/bookings"
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition"
          >
            View Tickets →
          </Link>
        </div>
      )}

      {/* Available E-Carts Fleet */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-black text-slate-900">Active Campus Carts</h2>
            <p className="text-xs text-slate-500">Live seat availability updated in real-time</p>
          </div>
          <Link
            to="/customer/find-carts"
            className="text-xs font-bold text-blue-600 hover:underline flex items-center gap-1"
          >
            See all carts ({carts.length}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-44 bg-slate-100 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {carts.map((cart) => (
              <div
                key={cart.id}
                className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-black px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                      {cart.cart_number}
                    </span>
                    <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-600">
                      <BatteryCharging className="w-3.5 h-3.5" /> {cart.battery_percentage}%
                    </span>
                  </div>
                  <h3 className="font-extrabold text-slate-900 text-base">{cart.name || 'Campus Shuttle'}</h3>
                  <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-blue-500" />
                    {cart.route_name || 'Circular Campus Line'}
                  </p>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Available</span>
                    <span className="text-sm font-black text-blue-600">
                      {cart.available_seats} of {cart.total_seats} seats
                    </span>
                  </div>
                  <Link
                    to={`/customer/book/${cart.id}`}
                    className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition"
                  >
                    Select Seat
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Campus Shuttle Routes */}
      <div>
        <h2 className="text-xl font-black text-slate-900 mb-1">Official Campus Routes</h2>
        <p className="text-xs text-slate-500 mb-4">Standard stops and fixed Rs. 10 - 15 student fare</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {routes.map((r) => (
            <div key={r.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md">
                  {r.code}
                </span>
                <span className="text-xs font-black text-slate-800">₹{r.fare_amount}</span>
              </div>
              <h3 className="font-extrabold text-slate-900 text-sm">{r.name}</h3>
              <p className="text-xs text-slate-500 mt-1 mb-3">{r.description || 'Continuous campus shuttle service'}</p>
              
              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <span className="text-[10px] font-bold uppercase text-slate-400">Key Stops:</span>
                <div className="flex flex-wrap gap-1.5">
                  {r.stops?.slice(0, 3).map((s) => (
                    <span key={s.id} className="text-[11px] px-2 py-0.5 bg-slate-50 border border-slate-200 rounded text-slate-600 font-medium">
                      {s.name}
                    </span>
                  ))}
                  {r.stops?.length > 3 && (
                    <span className="text-[11px] px-1.5 py-0.5 text-slate-400 font-bold">
                      +{r.stops.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
