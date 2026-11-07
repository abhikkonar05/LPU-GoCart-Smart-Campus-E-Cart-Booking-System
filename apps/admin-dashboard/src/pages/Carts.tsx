import React, { useEffect, useState } from 'react';
import { AdminAPI } from '../services/api';
import {
  Car,
  Battery,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Plus,
  RefreshCw,
  X
} from 'lucide-react';

export const Carts: React.FC = () => {
  const [carts, setCarts] = useState<any[]>([]);
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCart, setSelectedCart] = useState<any | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cartsData, routesData] = await Promise.all([
        AdminAPI.getCarts(),
        AdminAPI.getRoutes().catch(() => [])
      ]);
      setCarts(cartsData);
      setRoutes(routesData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openSeatModal = async (cart: any) => {
    try {
      const detail = await AdminAPI.getCartDetail(cart.id);
      setSelectedCart(detail);
      setModalOpen(true);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStatusChange = async (cartId: string, newStatus: string) => {
    try {
      await AdminAPI.updateCart(cartId, { status: newStatus });
      fetchData();
      if (selectedCart && selectedCart.id === cartId) {
        setSelectedCart({ ...selectedCart, status: newStatus });
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Electric Cart Fleet</h1>
          <p className="text-sm text-slate-500 font-medium">Inventory, 8-seat configuration, and route deployment</p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Carts Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {carts.map((cart) => (
          <div
            key={cart.id}
            className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                  {cart.route_code || 'Unassigned Line'}
                </span>
                <h3 className="text-lg font-black text-slate-900">{cart.cart_number}</h3>
                <p className="text-xs text-slate-500">{cart.model}</p>
              </div>

              <select
                value={cart.status}
                onChange={(e) => handleStatusChange(cart.id, e.target.value)}
                className={`text-xs font-bold px-2.5 py-1 rounded-lg border outline-none cursor-pointer ${
                  cart.status === 'ACTIVE'
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : cart.status === 'CHARGING'
                    ? 'bg-blue-50 text-blue-700 border-blue-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}
              >
                <option value="ACTIVE">ACTIVE</option>
                <option value="CHARGING">CHARGING</option>
                <option value="MAINTENANCE">MAINTENANCE</option>
                <option value="OFFLINE">OFFLINE</option>
              </select>
            </div>

            {/* Battery Indicator */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-500 flex items-center">
                  <Battery className="w-4 h-4 mr-1 text-slate-400" />
                  Battery Level
                </span>
                <span className="text-slate-800 font-bold">{cart.battery_percentage}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    cart.battery_percentage > 50
                      ? 'bg-emerald-500'
                      : cart.battery_percentage > 20
                      ? 'bg-amber-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${cart.battery_percentage}%` }}
                ></div>
              </div>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] font-bold uppercase">Open Seats</span>
                <span className="font-extrabold text-emerald-600 text-sm">
                  {cart.available_seats} / {cart.total_seats}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] font-bold uppercase">CCTV Status</span>
                <span className="font-semibold text-slate-700">
                  {cart.has_cctv ? 'Active HD Cam' : 'Not installed'}
                </span>
              </div>
            </div>

            {/* Inspect Seats Button */}
            <button
              onClick={() => openSeatModal(cart)}
              className="w-full py-2 bg-slate-50 hover:bg-blue-50 hover:text-blue-600 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 transition"
            >
              View 8-Seat Configuration →
            </button>
          </div>
        ))}
      </div>

      {/* Seat Layout Modal */}
      {modalOpen && selectedCart && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-lg text-slate-900">{selectedCart.cart_number} Seating Grid</h3>
                <p className="text-xs text-slate-500">Atomic real-time seat lock visualization</p>
              </div>
              <button
                onClick={() => setModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Driver & Steerage */}
            <div className="bg-slate-100 rounded-xl p-3 text-center text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center justify-center space-x-2">
              <span>Driver Seat:</span>
              <span className="text-slate-800">{selectedCart.assigned_driver_name || 'Assigned Driver'}</span>
            </div>

            {/* 2x4 Passenger Grid */}
            <div className="grid grid-cols-2 gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-200">
              {selectedCart.seats?.map((seat: any) => {
                const isBooked = !seat.is_available && !seat.is_locked;
                const isLocked = seat.is_locked;
                const isFree = seat.is_available;

                return (
                  <div
                    key={seat.id}
                    className={`p-3.5 rounded-xl border text-center font-bold text-xs transition ${
                      isFree
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                        : isLocked
                        ? 'bg-amber-50 border-amber-300 text-amber-800'
                        : 'bg-red-50 border-red-200 text-red-700'
                    }`}
                  >
                    <p className="text-sm font-black">{seat.seat_label}</p>
                    <p className="text-[10px] mt-0.5">
                      {isFree ? 'AVAILABLE' : isLocked ? 'LOCKED (5m)' : 'BOOKED'}
                    </p>
                    {seat.is_accessible && (
                      <span className="inline-block mt-1 text-[9px] px-1.5 py-0.2 rounded bg-white/70 font-semibold text-slate-600">
                        Accessible
                      </span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-around text-xs text-slate-600 font-semibold pt-2">
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-emerald-500 mr-1.5"></span> Available
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-amber-500 mr-1.5"></span> Locked (Cart Hold)
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-red-500 mr-1.5"></span> Booked
              </span>
            </div>

            <button
              onClick={() => setModalOpen(false)}
              className="w-full py-2.5 bg-slate-900 text-white font-bold text-sm rounded-xl hover:bg-slate-800 transition"
            >
              Close Inspector
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

