import React, { useState } from 'react';
import { Ticket, Search, Filter, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export const Bookings: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Sample bookings for demonstration
  const [bookings] = useState([
    {
      id: 'bk-01',
      booking_code: 'LPU-BK-918234',
      student_name: 'Aman Sharma',
      reg_no: '12104599',
      cart_number: 'LPU-CART-01',
      seat_label: 'S2',
      pickup: 'Main Gate (Gate 1)',
      drop: 'UniMall & Food Court',
      fare: 10.0,
      status: 'CONFIRMED',
      created_at: 'Just now'
    },
    {
      id: 'bk-02',
      booking_code: 'LPU-BK-827103',
      student_name: 'Priya Verma',
      reg_no: '12108821',
      cart_number: 'LPU-CART-02',
      seat_label: 'S1 (Accessible)',
      pickup: 'Girls Hostels (GH 1-6)',
      drop: 'Central Library / Block 34',
      fare: 10.0,
      status: 'BOARDED',
      created_at: '12 mins ago'
    },
    {
      id: 'bk-03',
      booking_code: 'LPU-BK-736291',
      student_name: 'Rohan Mehra',
      reg_no: '12103314',
      cart_number: 'LPU-CART-03',
      seat_label: 'S4',
      pickup: 'Boys Hostels (BH 1-8)',
      drop: 'Block 32 (Engineering)',
      fare: 10.0,
      status: 'CONFIRMED',
      created_at: '25 mins ago'
    },
  ]);

  const filtered = bookings.filter(
    (b) =>
      b.booking_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      b.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      b.reg_no.includes(searchTerm)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Passenger Bookings</h1>
          <p className="text-sm text-slate-500 font-medium">Verified seat reservations, digital QR boarding tickets, and travel history</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Search Bar */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="relative w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by student, reg no, or code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs font-medium outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-100"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="px-6 py-4">Booking Code</th>
                <th className="px-6 py-4">Student</th>
                <th className="px-6 py-4">Vehicle & Seat</th>
                <th className="px-6 py-4">Route Leg</th>
                <th className="px-6 py-4">Fare</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filtered.map((b) => (
                <tr key={b.id} className="hover:bg-slate-50/80 transition">
                  <td className="px-6 py-4 font-mono font-bold text-blue-600">{b.booking_code}</td>
                  <td className="px-6 py-4">
                    <p className="font-bold text-slate-900">{b.student_name}</p>
                    <p className="text-xs text-slate-400">Reg: {b.reg_no}</p>
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-bold text-slate-800">{b.cart_number}</p>
                    <p className="text-xs text-emerald-600 font-semibold">Seat: {b.seat_label}</p>
                  </td>
                  <td className="px-6 py-4 text-xs">
                    <span className="text-slate-600 font-semibold">{b.pickup}</span>
                    <span className="text-slate-400 block">→ {b.drop}</span>
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-800">₹{b.fare}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        b.status === 'BOARDED'
                          ? 'bg-purple-50 text-purple-700'
                          : 'bg-emerald-50 text-emerald-700'
                      }`}
                    >
                      {b.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-400">{b.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

