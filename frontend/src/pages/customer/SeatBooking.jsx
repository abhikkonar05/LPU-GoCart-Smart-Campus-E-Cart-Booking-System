import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../../services/api';
import { Car, Clock, ShieldCheck, Check, AlertCircle, ArrowRight, ArrowLeft, QrCode, Luggage } from 'lucide-react';

export default function SeatBooking() {
  const { cartId } = useParams();
  const navigate = useNavigate();

  const [cart, setCart] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [pickupStopId, setPickupStopId] = useState('');
  const [dropStopId, setDropStopId] = useState('');
  const [isFullCart, setIsFullCart] = useState(false);

  // Luggage states
  const [smallBags, setSmallBags] = useState(0);
  const [mediumBags, setMediumBags] = useState(0);
  const [largeBags, setLargeBags] = useState(0);

  // Lock state
  const [activeLock, setActiveLock] = useState(null);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [loading, setLoading] = useState(true);
  const [lockingSeat, setLockingSeat] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Payment & confirmation modal
  const [bookingConfirmed, setBookingConfirmed] = useState(null);
  const [processingPayment, setProcessingPayment] = useState(false);

  // Fetch cart detail and routes
  useEffect(() => {
    const fetchCartAndRoutes = async () => {
      try {
        const [cRes, rRes] = await Promise.all([
          api.get(`/carts/${cartId}`),
          api.get('/routes'),
        ]);
        setCart(cRes.data);
        setRoutes(rRes.data);

        // Pre-select pickup and drop from current route if available
        const currentRoute = rRes.data.find((r) => r.id === cRes.data.current_route_id);
        if (currentRoute && currentRoute.stops?.length >= 2) {
          setPickupStopId(currentRoute.stops[0].id);
          setDropStopId(currentRoute.stops[currentRoute.stops.length - 1].id);
        }
      } catch (err) {
        setError('Failed to load cart details. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchCartAndRoutes();
  }, [cartId]);

  // Countdown timer for atomic 5-minute seat lock
  useEffect(() => {
    if (!remainingSeconds || remainingSeconds <= 0) return;
    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setActiveLock(null);
          setSelectedSeat(null);
          setError('Seat lock expired. Please select a seat again.');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [remainingSeconds]);

  // Handle seat lock click
  const handleSelectSeat = async (seat) => {
    if (!seat.is_available) return;
    setError('');
    setLockingSeat(true);

    try {
      const res = await api.post('/bookings/lock-seat', {
        cart_id: cart.id,
        trip_id: 'auto',
        seat_id: seat.id,
      });

      setSelectedSeat(seat);
      setActiveLock(res.data);
      setRemainingSeconds(res.data.remaining_seconds || 300);
      setSuccessMsg(`Seat ${seat.seat_label} locked for 5 minutes! Complete your booking.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not lock seat. It may have just been taken.');
    } finally {
      setLockingSeat(false);
    }
  };

  // Pricing calculations
  const baseFare = isFullCart ? 60.0 : (cart?.current_route?.fare_amount || 10.0);
  const luggageFee = (mediumBags * 10) + (largeBags * 20);
  const totalAmount = baseFare + luggageFee;

  // Process Demo Payment & Confirm Reservation
  const handleProceedPayment = async () => {
    if (!isFullCart && !selectedSeat) {
      setError('Please select an available seat first.');
      return;
    }
    if (!pickupStopId || !dropStopId) {
      setError('Please select both pickup and drop-off campus stops.');
      return;
    }

    setProcessingPayment(true);
    setError('');

    try {
      // 1. Create pending booking
      const bookRes = await api.post('/bookings/create-pending', {
        lock_id: activeLock?.lock_id || null,
        trip_id: activeLock?.trip_id || 'auto',
        cart_id: cart.id,
        seat_id: isFullCart ? null : selectedSeat?.id,
        booking_type: isFullCart ? 'FULL_CART' : 'SEAT',
        pickup_stop_id: pickupStopId,
        drop_stop_id: dropStopId,
        fare_amount: baseFare,
        small_bags: smallBags,
        medium_bags: mediumBags,
        large_bags: largeBags,
        luggage_fee: luggageFee,
      });

      const pendingBooking = bookRes.data;

      // 2. Create payment intent
      const intentRes = await api.post('/payments/create-intent', {
        booking_id: pendingBooking.id,
        amount: totalAmount,
      });

      // 3. Confirm Demo Payment
      const payRes = await api.post('/payments/demo-confirm', {
        payment_id: intentRes.data.payment_id,
        booking_id: pendingBooking.id,
        simulate_status: 'SUCCESS',
      });

      // 4. Retrieve digital boarding ticket
      const ticketRes = await api.get(`/bookings/${pendingBooking.id}/ticket`);
      setBookingConfirmed(ticketRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment simulation failed.');
    } finally {
      setProcessingPayment(false);
    }
  };

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-500 font-bold">Loading seating configuration...</div>;
  }

  // Active route stops for pickup / drop
  const currentRoute = routes.find((r) => r.id === cart?.current_route_id) || routes[0];
  const stops = currentRoute?.stops || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-6">
      {/* Back button & Header */}
      <div className="flex items-center justify-between">
        <Link
          to="/customer/find-carts"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Carts
        </Link>
        <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
          Cart #{cart?.cart_number}
        </span>
      </div>

      {/* Confirmation Modal */}
      {bookingConfirmed && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-center space-y-4 animate-in fade-in zoom-in-95">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center">
              <Check className="w-8 h-8 stroke-[3]" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600">Booking Confirmed</span>
              <h2 className="text-2xl font-black text-slate-900 mt-1">Boarding Pass Issued!</h2>
              <p className="text-xs text-slate-500">Booking Code: {bookingConfirmed.booking_code}</p>
            </div>

            {/* QR Card */}
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
              <div className="w-36 h-36 bg-white mx-auto p-2 rounded-xl border border-slate-300 flex items-center justify-center">
                <QrCode className="w-28 h-28 text-slate-900" />
              </div>
              <span className="text-[11px] font-mono font-bold text-slate-500 block">
                {bookingConfirmed.qr_token}
              </span>
              <div className="text-xs text-slate-700 font-semibold pt-2 border-t border-slate-200 grid grid-cols-2 gap-2 text-left">
                <div>
                  <span className="text-[10px] text-slate-400 block">Passenger</span>
                  {bookingConfirmed.passenger_name}
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Seat / Type</span>
                  {bookingConfirmed.seat_label}
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Pickup</span>
                  {bookingConfirmed.pickup_stop}
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Drop</span>
                  {bookingConfirmed.drop_stop}
                </div>
              </div>
            </div>

            <button
              onClick={() => navigate('/customer/bookings')}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg transition text-sm"
            >
              Go to My Tickets
            </button>
          </div>
        </div>
      )}

      {/* Booking Form Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Seating Map & Options */}
        <div className="md:col-span-2 space-y-6">
          {/* Cart Header Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Electric Vehicle</span>
              <h2 className="text-xl font-black text-slate-900">{cart?.name}</h2>
              <p className="text-xs text-slate-500">Route: {cart?.route_name || 'Campus Loop'}</p>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block">Battery Level</span>
              <span className="text-lg font-black text-emerald-600">{cart?.battery_percentage}%</span>
            </div>
          </div>

          {/* Seat Map Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900">Select Individual Seat</h3>
                <p className="text-xs text-slate-500">Click any green seat to activate a 5-minute lock</p>
              </div>

              {/* 5-Min Timer Pill */}
              {remainingSeconds > 0 && (
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200 font-bold text-xs animate-pulse">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Held: {formatTimer(remainingSeconds)}</span>
                </div>
              )}
            </div>

            {/* Error / Success Alerts */}
            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-xl text-xs font-bold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}
            {successMsg && !error && (
              <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-xs font-bold flex items-center gap-2">
                <Check className="w-4 h-4 flex-shrink-0" />
                {successMsg}
              </div>
            )}

            {/* 6-Seat Visual E-Cart Diagram */}
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200 max-w-sm mx-auto">
              <div className="text-center pb-3 mb-4 border-b border-slate-200 text-xs font-extrabold text-slate-400 uppercase tracking-widest flex items-center justify-center gap-2">
                <Car className="w-4 h-4 text-slate-400" />
                Front (Driver's Cabin)
              </div>

              <div className="grid grid-cols-2 gap-4">
                {cart?.seats?.map((seat) => {
                  const isSelected = selectedSeat?.id === seat.id;
                  const isLocked = seat.is_locked && !isSelected;
                  const isAvailable = seat.is_available && !isLocked;

                  return (
                    <button
                      key={seat.id}
                      type="button"
                      disabled={!isAvailable || lockingSeat || isFullCart}
                      onClick={() => handleSelectSeat(seat)}
                      className={`p-4 rounded-xl border text-center font-extrabold text-sm transition flex flex-col items-center justify-center gap-1 ${
                        isSelected
                          ? 'bg-blue-600 text-white border-blue-700 shadow-md ring-2 ring-blue-400'
                          : isAvailable
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100 hover:shadow-sm cursor-pointer'
                          : 'bg-slate-200 text-slate-400 border-slate-300 cursor-not-allowed'
                      }`}
                    >
                      <span>{seat.seat_label}</span>
                      <span className="text-[10px] font-semibold">
                        {isSelected ? 'Your Seat' : isAvailable ? 'Available' : 'Booked'}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="text-center pt-4 mt-4 border-t border-slate-200 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                Rear Cargo / Luggage Area
              </div>
            </div>

            {/* Full Cart Booking Option */}
            <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200 flex items-center justify-between">
              <div>
                <span className="text-xs font-extrabold text-indigo-900 block">Reserve Entire Cart (Private Ride)</span>
                <span className="text-[11px] text-indigo-700">Reserves all 6 passenger seats for group travel</span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setIsFullCart(!isFullCart);
                  setSelectedSeat(null);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  isFullCart ? 'bg-indigo-600 text-white' : 'bg-white text-indigo-700 border border-indigo-300'
                }`}
              >
                {isFullCart ? 'Selected' : 'Select'}
              </button>
            </div>
          </div>

          {/* Luggage Capacity Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <Luggage className="w-5 h-5 text-blue-600" />
              <h3 className="text-base font-extrabold text-slate-900">Luggage Space Reservation</h3>
            </div>
            <p className="text-xs text-slate-500">
              Select optional baggage slots to ensure enough cargo space on the vehicle.
            </p>

            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-xl border border-slate-200 text-center">
                <span className="text-xs font-bold text-slate-800 block">Small (Backpack)</span>
                <span className="text-[11px] text-emerald-600 font-bold block mb-2">Free</span>
                <div className="flex items-center justify-center gap-2">
                  <button
                    type="button"
                    onClick={() => setSmallBags(Math.max(0, smallBags - 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    -
                  </button>
                  <span className="text-xs font-bold">{smallBags}</span>
                  <button
                    type="button"
                    onClick={() => setSmallBags(Math.min(4, smallBags + 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-xl border border-slate-200 text-center">
                <span className="text-xs font-bold text-slate-800 block">Medium (Cabin Bag)</span>
                <span className="text-[11px] text-blue-600 font-bold block mb-2">+₹10 each</span>
                <div className="flex items-center justify-center gap-2">
                  <button
                    type="button"
                    onClick={() => setMediumBags(Math.max(0, mediumBags - 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    -
                  </button>
                  <span className="text-xs font-bold">{mediumBags}</span>
                  <button
                    type="button"
                    onClick={() => setMediumBags(Math.min(3, mediumBags + 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-xl border border-slate-200 text-center">
                <span className="text-xs font-bold text-slate-800 block">Large (Trolley)</span>
                <span className="text-[11px] text-blue-600 font-bold block mb-2">+₹20 each</span>
                <div className="flex items-center justify-center gap-2">
                  <button
                    type="button"
                    onClick={() => setLargeBags(Math.max(0, largeBags - 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    -
                  </button>
                  <span className="text-xs font-bold">{largeBags}</span>
                  <button
                    type="button"
                    onClick={() => setLargeBags(Math.min(2, largeBags + 1))}
                    className="w-6 h-6 rounded bg-slate-100 font-bold text-xs"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: Trip Details & Checkout */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4 sticky top-20">
            <h3 className="text-base font-black text-slate-900 border-b border-slate-100 pb-3">
              Trip & Fare Summary
            </h3>

            {/* Stops Selection */}
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase mb-1">
                  Pickup Stop
                </label>
                <select
                  value={pickupStopId}
                  onChange={(e) => setPickupStopId(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
                >
                  {stops.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.sequence_order}. {s.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase mb-1">
                  Drop-off Stop
                </label>
                <select
                  value={dropStopId}
                  onChange={(e) => setDropStopId(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
                >
                  {stops.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.sequence_order}. {s.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Cost Breakdown */}
            <div className="space-y-2 py-3 border-y border-slate-100 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>{isFullCart ? 'Full Cart Fare' : `Seat Fare (${selectedSeat?.seat_label || 'None'})`}</span>
                <span className="font-bold text-slate-900">₹{baseFare.toFixed(2)}</span>
              </div>
              {luggageFee > 0 && (
                <div className="flex justify-between">
                  <span>Luggage Surcharge</span>
                  <span className="font-bold text-slate-900">₹{luggageFee.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between pt-2 border-t border-slate-100 text-sm font-black text-slate-900">
                <span>Total Amount</span>
                <span className="text-blue-600">₹{totalAmount.toFixed(2)}</span>
              </div>
            </div>

            <div className="p-2.5 bg-blue-50/60 rounded-xl text-[11px] text-blue-700 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-blue-600 flex-shrink-0" />
              <span>Instant Demo Payment (Zero fee demonstration)</span>
            </div>

            <button
              type="button"
              disabled={(!isFullCart && !selectedSeat) || processingPayment}
              onClick={handleProceedPayment}
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-600/30 transition text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processingPayment ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Pay ₹{totalAmount.toFixed(2)} & Get Ticket</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
