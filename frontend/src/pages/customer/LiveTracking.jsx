import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import api from '../../services/api';
import { MapPin, BatteryCharging, Car, RefreshCw, Compass } from 'lucide-react';

// Custom LPU Cart Marker Icon
const cartIcon = L.divIcon({
  html: `<div style="background-color: #2563eb; color: white; border-radius: 9999px; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); border: 2px solid white; font-weight: bold; font-size: 14px;">🛺</div>`,
  className: 'lpu-cart-marker',
  iconSize: [34, 34],
  iconAnchor: [17, 17],
});

// Campus Center (Lovely Professional University, Phagwara, Punjab)
const LPU_CENTER = [31.2536, 75.7037];

export default function LiveTracking() {
  const [carts, setCarts] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLiveTelemetry = async () => {
    try {
      const [cRes, rRes] = await Promise.all([
        api.get('/carts'),
        api.get('/routes'),
      ]);
      setCarts(cRes.data);
      setRoutes(rRes.data);
    } catch (err) {
      console.error('Failed to load telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveTelemetry();
    // Poll telemetry every 4 seconds
    const interval = setInterval(fetchLiveTelemetry, 4000);
    return () => clearInterval(interval);
  }, []);

  // Collect all route stops for map markers
  const allStops = routes.flatMap((r) => r.stops || []);

  return (
    <div className="space-y-4 py-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Compass className="w-6 h-6 text-blue-600" />
            Live Campus Fleet Tracking
          </h1>
          <p className="text-xs text-slate-500">
            Real-time GPS telemetry from active e-carts across Lovely Professional University.
          </p>
        </div>

        <button
          onClick={fetchLiveTelemetry}
          className="px-3.5 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-xl shadow-sm transition flex items-center gap-1.5 self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Position</span>
        </button>
      </div>

      {/* Map Card */}
      <div className="bg-white rounded-3xl p-3 border border-slate-200 shadow-xl h-[520px]">
        <MapContainer
          center={LPU_CENTER}
          zoom={15}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%', borderRadius: '1.25rem' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Route Stops */}
          {allStops.map((stop) => (
            <CircleMarker
              key={stop.id}
              center={[stop.latitude, stop.longitude]}
              radius={6}
              pathOptions={{ color: '#6366f1', fillColor: '#a5b4fc', fillOpacity: 0.9, weight: 2 }}
            >
              <Popup>
                <div className="p-1 text-xs">
                  <strong className="block text-slate-900">{stop.name}</strong>
                  <span className="text-slate-500 text-[10px]">Campus Stop #{stop.sequence_order}</span>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* Operating Carts */}
          {carts.map((cart, idx) => {
            // If cart doesn't have live coords yet, place along LPU campus route offsets
            const lat = cart.current_latitude || (31.2536 + (idx * 0.002) - 0.001);
            const lng = cart.current_longitude || (75.7037 + (idx * 0.002) - 0.001);

            return (
              <Marker key={cart.id} position={[lat, lng]} icon={cartIcon}>
                <Popup>
                  <div className="p-1 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                      <span className="font-mono font-bold text-blue-600">{cart.cart_number}</span>
                      <span className="text-[10px] text-emerald-600 font-bold flex items-center gap-0.5">
                        <BatteryCharging className="w-3 h-3" /> {cart.battery_percentage}%
                      </span>
                    </div>
                    <strong className="block text-slate-900">{cart.name}</strong>
                    <span className="text-slate-500 block text-[11px]">
                      Route: {cart.route_name || 'Campus Shuttle'}
                    </span>
                    <span className="text-blue-700 font-bold block text-[11px]">
                      {cart.available_seats} of {cart.total_seats} seats free
                    </span>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
