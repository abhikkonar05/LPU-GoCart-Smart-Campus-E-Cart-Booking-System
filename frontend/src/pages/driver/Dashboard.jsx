import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { Car, MapPin, Play, Square, QrCode, Users, Check, AlertCircle, Compass, BatteryCharging } from 'lucide-react';

export default function DriverDashboard() {
  const { user } = useAuth();
  const [driverData, setDriverData] = useState(null);
  const [passengers, setPassengers] = useState([]);
  const [qrInput, setQrInput] = useState('');
  const [verifyResult, setVerifyResult] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [isBroadcastingGPS, setIsBroadcastingGPS] = useState(false);
  const [watchId, setWatchId] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchDriverInfo = async () => {
    try {
      const res = await api.get('/drivers/assigned-cart');
      setDriverData(res.data);

      if (res.data.active_trip?.id) {
        const passRes = await api.get(`/drivers/passengers?trip_id=${res.data.active_trip.id}`);
        setPassengers(passRes.data);
      } else {
        setPassengers([]);
      }
    } catch (err) {
      console.error('Failed to load driver details:', err);
    }
  };

  useEffect(() => {
    fetchDriverInfo();
  }, []);

  // HTML5 Browser Geolocation Live Broadcast
  const toggleGPSBroadcasting = () => {
    if (isBroadcastingGPS) {
      if (watchId) navigator.geolocation.clearWatch(watchId);
      setIsBroadcastingGPS(false);
      setWatchId(null);
    } else {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
      }

      const id = navigator.geolocation.watchPosition(
        async (position) => {
          if (!driverData?.assigned_cart?.id) return;
          try {
            await api.post('/tracking/update', {
              cart_id: driverData.assigned_cart.id,
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              speed_kph: position.coords.speed ? position.coords.speed * 3.6 : 0.0,
              heading: position.coords.heading || null,
              accuracy_meters: position.coords.accuracy,
              trip_id: driverData.active_trip?.id || null,
            });
          } catch (err) {
            console.error('Error broadcasting telemetry:', err);
          }
        },
        (err) => console.warn('Geolocation watch error:', err),
        { enableHighAccuracy: true, maximumAge: 3000, timeout: 5000 }
      );

      setWatchId(id);
      setIsBroadcastingGPS(true);
    }
  };

  // Start Trip
  const handleStartTrip = async () => {
    if (!driverData?.assigned_cart?.id) return;
    setActionLoading(true);
    setError('');
    try {
      await api.post('/drivers/trips/start', {
        cart_id: driverData.assigned_cart.id,
        route_id: driverData.assigned_cart.current_route_id || null,
      });
      await fetchDriverInfo();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start trip.');
    } finally {
      setActionLoading(false);
    }
  };

  // End Trip
  const handleEndTrip = async () => {
    if (!driverData?.active_trip?.id) return;
    setActionLoading(true);
    setError('');
    try {
      await api.post('/drivers/trips/end', {
        trip_id: driverData.active_trip.id,
      });
      await fetchDriverInfo();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to end trip.');
    } finally {
      setActionLoading(false);
    }
  };

  // Verify QR Boarding Pass
  const handleVerifyQR = async (e) => {
    if (e) e.preventDefault();
    if (!qrInput.trim()) return;
    setVerifying(true);
    setVerifyResult(null);

    try {
      const res = await api.post('/drivers/verify-qr', {
        qr_token: qrInput.trim(),
      });
      setVerifyResult({ success: true, data: res.data });
      setQrInput('');
      fetchDriverInfo(); // refresh passenger manifest
    } catch (err) {
      setVerifyResult({
        success: false,
        message: err.response?.data?.detail || 'Verification failed. Invalid or already used ticket.',
      });
    } finally {
      setVerifying(false);
    }
  };

  const cart = driverData?.assigned_cart;
  const activeTrip = driverData?.active_trip;

  return (
    <div className="space-y-6 py-4">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              Driver On Shift
            </span>
            <span className="text-xs text-slate-400 font-medium">• LPU Transport Fleet</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Captain {user?.full_name}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage your assigned vehicle, broadcast GPS telemetry, and verify boarding passes.
          </p>
        </div>

        {/* Live GPS Broadcast Switch */}
        <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-200">
          <div className="text-right">
            <span className="text-xs font-bold text-slate-900 block">Mobile GPS Sharing</span>
            <span className="text-[11px] text-slate-500 font-medium">
              {isBroadcastingGPS ? 'Broadcasting coordinates' : 'Telemetry Paused'}
            </span>
          </div>
          <button
            type="button"
            onClick={toggleGPSBroadcasting}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm ${
              isBroadcastingGPS
                ? 'bg-emerald-600 text-white hover:bg-emerald-700 animate-pulse'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            <Compass className="w-4 h-4" />
            {isBroadcastingGPS ? 'Live ON' : 'Turn ON'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-2xl text-xs font-bold flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Grid: Cart Status & Trip Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Assigned Cart Details */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-xs font-bold uppercase text-slate-400">Assigned Vehicle</span>
            <span className="font-mono text-xs font-black px-2.5 py-0.5 rounded bg-blue-50 text-blue-700">
              {cart?.cart_number || 'Unassigned'}
            </span>
          </div>

          <div>
            <h3 className="text-lg font-black text-slate-900">{cart?.name || 'LPU E-Cart'}</h3>
            <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
              <MapPin className="w-3.5 h-3.5 text-blue-600" />
              Route: {cart?.route_name || 'Circular Campus Line'}
            </p>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <BatteryCharging className="w-4 h-4 text-emerald-600" /> Battery
            </span>
            <span className="text-sm font-extrabold text-emerald-600">
              {cart?.battery_percentage || 100}%
            </span>
          </div>

          {/* Start / Stop Trip Controls */}
          <div className="pt-2">
            {activeTrip ? (
              <button
                onClick={handleEndTrip}
                disabled={actionLoading}
                className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs shadow-md shadow-red-600/20 transition flex items-center justify-center gap-2"
              >
                <Square className="w-4 h-4" />
                <span>End Active Transit Trip</span>
              </button>
            ) : (
              <button
                onClick={handleStartTrip}
                disabled={actionLoading}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-md shadow-emerald-600/20 transition flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Start Campus Transit Trip</span>
              </button>
            )}
          </div>
        </div>

        {/* QR Ticket Verification Console */}
        <div className="md:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <QrCode className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-extrabold text-slate-900">Passenger QR Boarding Verification</h3>
          </div>

          <p className="text-xs text-slate-500">
            Scan or enter the student's digital booking code or QR token below to mark them as checked in.
          </p>

          <form onSubmit={handleVerifyQR} className="flex gap-2">
            <input
              type="text"
              value={qrInput}
              onChange={(e) => setQrInput(e.target.value)}
              placeholder="e.g. LPU-BK-981203 or paste QR token"
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={verifying}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition disabled:opacity-50"
            >
              {verifying ? 'Checking...' : 'Verify Ticket'}
            </button>
          </form>

          {/* Verification Results */}
          {verifyResult && (
            <div
              className={`p-4 rounded-xl text-xs font-semibold flex items-start gap-2.5 ${
                verifyResult.success
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {verifyResult.success ? (
                <>
                  <Check className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-extrabold block">{verifyResult.data.message}</span>
                    <span className="text-[11px] text-emerald-700 block mt-0.5">
                      Passenger: {verifyResult.data.passenger_name} • Seat: {verifyResult.data.seat_label}
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-extrabold block">{verifyResult.message}</span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Passenger Boarding Manifest */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-black text-slate-900">Current Trip Passenger Manifest</h3>
          </div>
          <span className="text-xs font-bold text-slate-400">
            {passengers.length} Booked Rider(s)
          </span>
        </div>

        {passengers.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            No passengers booked on this trip yet. Once students reserve seats, they will appear here.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {passengers.map((p) => (
              <div key={p.booking_id} className="py-3 flex items-center justify-between">
                <div>
                  <span className="font-bold text-xs text-slate-900 block">{p.passenger_name}</span>
                  <span className="text-[11px] text-slate-500">
                    {p.pickup} → {p.drop} • Seat {p.seat_label}
                  </span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  p.status === 'CHECKED_IN' || p.status === 'BOARDED'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  {p.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
