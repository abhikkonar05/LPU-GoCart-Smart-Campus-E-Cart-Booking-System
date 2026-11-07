import React from 'react';
import { CreditCard, CheckCircle2, Clock, ShieldCheck } from 'lucide-react';

export const Payments: React.FC = () => {
  const transactions = [
    {
      id: 'tx-01',
      booking_code: 'LPU-BK-918234',
      student: 'Aman Sharma',
      amount: 10.0,
      gateway: 'Demo Gateway (Simulated)',
      ref: 'demo_txn_49fa81920',
      status: 'COMPLETED',
      date: 'Today, 01:45 AM'
    },
    {
      id: 'tx-02',
      booking_code: 'LPU-BK-827103',
      student: 'Priya Verma',
      amount: 10.0,
      gateway: 'Demo Gateway (Simulated)',
      ref: 'demo_txn_21ef90312',
      status: 'COMPLETED',
      date: 'Today, 01:32 AM'
    },
    {
      id: 'tx-03',
      booking_code: 'LPU-BK-736291',
      student: 'Rohan Mehra',
      amount: 10.0,
      gateway: 'Demo Gateway (Simulated)',
      ref: 'demo_txn_18bc72910',
      status: 'COMPLETED',
      date: 'Today, 01:20 AM'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Financial & Payment Ledger</h1>
          <p className="text-sm text-slate-500 font-medium">Reconciled fare payments via Demo and Razorpay gateways</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="px-6 py-4">Transaction Ref</th>
                <th className="px-6 py-4">Booking Code</th>
                <th className="px-6 py-4">Student</th>
                <th className="px-6 py-4">Gateway</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {transactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-slate-50/80 transition">
                  <td className="px-6 py-4 font-mono text-xs text-slate-600 font-bold">{tx.ref}</td>
                  <td className="px-6 py-4 font-mono font-bold text-blue-600">{tx.booking_code}</td>
                  <td className="px-6 py-4 font-bold text-slate-900">{tx.student}</td>
                  <td className="px-6 py-4 text-xs text-slate-500">{tx.gateway}</td>
                  <td className="px-6 py-4 font-extrabold text-slate-900">₹{tx.amount}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      {tx.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-400">{tx.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

