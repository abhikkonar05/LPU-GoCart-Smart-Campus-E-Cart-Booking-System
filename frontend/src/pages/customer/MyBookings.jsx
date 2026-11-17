import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { Ticket, QrCode, MapPin, Calendar, CheckCircle2, Car, ArrowRight } from 'lucide-react';

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const res = await api.get('/bookings/my');
        setBookings(res.data);
      } catch (err) {
        console.error('Error fetching bookings:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBookings();
  }, []);

  const openTicketModal = async (bookingId) => {
    try {
      const res = await api.get(`/bookings/${bookingId}/ticket`);
      setSelectedTicket(res.data);
    } catch (err) {
      alert('Unable to load digital ticket.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          My E-Cart Bookings & Tickets
        </h1>
        <p className="text-sm text-slate-500">
          Access your digital boarding passes and travel history across LPU campus.
        </p>
      </div>

      {/* Ticket Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 text-center space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs font-bold text-slate-400 uppercase">Boarding Pass</span>
              <span className="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                {selectedTicket.booking_code}
              </span>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200">
              <div className="w-40 h-40 bg-white mx-auto p-2 rounded-xl border border-slate-300 flex items-center justify-center mb-2">
                <QrCode className="w-32 h-32 text-slate-900" />
              </div>
              <span className="text-[11px] font-mono text-slate-500 block truncate">
                {selectedTicket.qr_token}
              </span>
            </div>

            <div className="text-xs text-slate-700 font-semibold space-y-1.5 text-left bg-slate-50 p-3 rounded-xl">
              <div className="flex justify-between">
                <span className="text-slate-400">Cart Number:</span>
                <span className="font-bold">{selectedTicket.cart_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Seat / Type:</span>
                <span className="font-bold text-blue-600">{selectedTicket.seat_label}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Pickup Stop:</span>
                <span className="font-bold">{selectedTicket.pickup_stop}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Drop Stop:</span>
                <span className="font-bold">{selectedTicket.drop_stop}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className="font-bold text-emerald-600">{selectedTicket.status}</span>
              </div>
            </div>

            <button
              onClick={() => setSelectedTicket(null)}
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition"
            >
              Close Pass
            </button>
          </div>
        </div>
      )}

      {/* Bookings List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-28 bg-slate-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 space-y-3">
          <Ticket className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-700">No bookings yet</h3>
          <p className="text-xs text-slate-400">You haven't reserved any campus e-cart rides yet.</p>
          <Link
            to="/customer/find-carts"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold shadow hover:bg-blue-700 transition"
          >
            <Car className="w-4 h-4" /> Book a Cart Now
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((b) => (
            <div
              key={b.id}
              className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-black px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                    {b.booking_code}
                  </span>
                  <span className="font-mono text-xs font-bold text-slate-600">
                    Cart: {b.cart_number}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    b.status === 'CONFIRMED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                    b.status === 'CHECKED_IN' || b.status === 'BOARDED' ? 'bg-blue-50 text-blue-700' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {b.status}
                  </span>
                </div>

                <div className="text-xs text-slate-600 flex flex-wrap items-center gap-x-4 gap-y-1">
                  <span className="flex items-center gap-1 font-semibold text-slate-800">
                    <MapPin className="w-3.5 h-3.5 text-blue-500" />
                    {b.pickup_stop_name} → {b.drop_stop_name}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span>Seat: <strong className="text-slate-800">{b.seat_label}</strong></span>
                  <span className="text-slate-400">•</span>
                  <span className="font-bold text-slate-800">₹{b.fare_amount}</span>
                </div>
              </div>

              <div>
                <button
                  type="button"
                  onClick={() => openTicketModal(b.id)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition flex items-center gap-2 w-full sm:w-auto justify-center"
                >
                  <QrCode className="w-3.5 h-3.5" />
                  <span>Show QR Pass</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
