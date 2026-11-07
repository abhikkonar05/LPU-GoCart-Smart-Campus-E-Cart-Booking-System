import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { AdminAPI } from '../services/api';
import {
  Car,
  Battery,
  Navigation,
  RefreshCw,
  Play,
  Pause,
  MapPin,
  Shield,
  Radio
} from 'lucide-react';

// Lovely Professional University Center Coordinates
const LPU_CENTER = [31.2536, 75.7037] as [number, number];

// LPU Campus Key Landmarks
const CAMPUS_STOPS = [
  { name: 'Gate 1 (Main Entrance)', lat: 31.2538, lng: 75.7012 },
  { name: 'Block 32 (Engineering)', lat: 31.2545, lng: 75.7040 },
  { name: 'UniMall & Food Court', lat: 31.2529, lng: 75.7048 },
  { name: 'Central Library / Block 34', lat: 31.2552, lng: 75.7058 },
  { name: 'Girls Hostels (GH 1-6)', lat: 31.2515, lng: 75.7075 },
  { name: 'Boys Hostels (BH 1-8)', lat: 31.2568, lng: 75.7082 },
  { name: 'Unipolis / Stadium', lat: 31.2530, lng: 75.7025 },
];

// Custom Leaflet Icons using SVG
const createCartIcon = (color: string, label: string) => {
  return L.divIcon({
    className: 'custom-cart-marker',
    html: `
      <div style="background-color: ${color}; width: 36px; height: 36px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 11px;">
        ${label}
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

const stopIcon = L.divIcon({
  className: 'custom-stop-marker',
  html: `
    <div style="background-color: #64748B; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
  `,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

// Map recenter helper component
const RecenterMap = ({ coords }: { coords: [number, number] | null }) => {
  const map = useMap();
  useEffect(() => {
    if (coords) {
      map.flyTo(coords, 16, { duration: 1.5 });
    }
  }, [coords, map]);
  return null;
};

export const LiveTracking: React.FC = () => {
  const [carts, setCarts] = useState<any[]>([]);
  const [selectedCart, setSelectedCart] = useState<any | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedCoords, setSelectedCoords] = useState<[number, number] | null>(null);
  const simStepRef = useRef(0);

  // Initial cart positions at LPU campus
  const [cartPositions, setCartPositions] = useState<Record<string, { lat: number; lng: number; speed: number }>>({
    'LPU-CART-01': { lat: 31.2538, lng: 75.7012, speed: 18 },
    'LPU-CART-02': { lat: 31.2530, lng: 75.7035, speed: 14 },
    'LPU-CART-03': { lat: 31.2552, lng: 75.7058, speed: 20 },
    'LPU-CART-04': { lat: 31.2568, lng: 75.7082, speed: 0 },
  });

  const loadCarts = async () => {
    try {
      const data = await AdminAPI.getCarts();
      setCarts(data);
      if (data.length > 0 && !selectedCart) {
        setSelectedCart(data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadCarts();
  }, []);

  // Live Simulation Loop (Moves carts in a loop around campus every 2 seconds)
  useEffect(() => {
    let timer: any;
    if (isSimulating) {
      timer = setInterval(() => {
        simStepRef.current += 1;
        const step = simStepRef.current;
        
        // Smooth orbital movement around LPU landmarks
        setCartPositions((prev) => ({
          'LPU-CART-01': {
            lat: 31.2538 + Math.sin(step * 0.1) * 0.0018,
            lng: 75.7012 + Math.cos(step * 0.1) * 0.0025,
            speed: 16 + Math.round(Math.sin(step) * 4),
          },
          'LPU-CART-02': {
            lat: 31.2530 + Math.cos(step * 0.08) * 0.0015,
            lng: 75.7035 + Math.sin(step * 0.08) * 0.0022,
            speed: 14 + Math.round(Math.cos(step) * 3),
          },
          'LPU-CART-03': {
            lat: 31.2552 + Math.sin(step * 0.12) * 0.0014,
            lng: 75.7058 + Math.cos(step * 0.12) * 0.0020,
            speed: 19,
          },
          'LPU-CART-04': prev['LPU-CART-04'],
        }));
      }, 2000);
    }
    return () => clearInterval(timer);
  }, [isSimulating]);

  const handleLocateCart = (cart: any) => {
    setSelectedCart(cart);
    const pos = cartPositions[cart.cart_number] || { lat: 31.2536, lng: 75.7037 };
    setSelectedCoords([pos.lat, pos.lng]);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Live Fleet GPS Telemetry</h1>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700">
              <Radio className="w-3 h-3 mr-1 animate-pulse" />
              Live Feed
            </span>
          </div>
          <p className="text-sm text-slate-500 font-medium">Real-time smartphone GPS coordinates from Lovely Professional University drivers</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-bold shadow-sm transition ${
              isSimulating
                ? 'bg-amber-500 hover:bg-amber-600 text-white shadow-amber-500/20'
                : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-600/20'
            }`}
          >
            {isSimulating ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Pause GPS Simulation</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Simulate Live Movement</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Map + Sidebar Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[650px]">
        {/* Map Container */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden relative">
          <MapContainer
            center={LPU_CENTER}
            zoom={15}
            scrollWheelZoom={true}
            className="w-full h-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <RecenterMap coords={selectedCoords} />

            {/* Campus Landmark Stops */}
            {CAMPUS_STOPS.map((stop, idx) => (
              <Marker key={`stop-${idx}`} position={[stop.lat, stop.lng]} icon={stopIcon}>
                <Popup>
                  <div className="p-1 font-sans">
                    <p className="font-bold text-xs text-slate-900">{stop.name}</p>
                    <p className="text-[10px] text-slate-500">Official E-Cart Pickup Stop</p>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Live Moving E-Carts */}
            {carts.map((cart) => {
              const pos = cartPositions[cart.cart_number] || { lat: 31.2536, lng: 75.7037, speed: 0 };
              const color = cart.status === 'ACTIVE' ? '#2563EB' : cart.status === 'CHARGING' ? '#059669' : '#94A3B8';
              const label = cart.cart_number.replace('LPU-CART-', 'C');

              return (
                <Marker
                  key={cart.id}
                  position={[pos.lat, pos.lng]}
                  icon={createCartIcon(color, label)}
                  eventHandlers={{
                    click: () => handleLocateCart(cart),
                  }}
                >
                  <Popup>
                    <div className="p-2 font-sans min-w-[180px]">
                      <div className="flex items-center justify-between border-b pb-1.5 mb-2">
                        <span className="font-bold text-sm text-slate-900">{cart.cart_number}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded font-bold bg-blue-50 text-blue-700">
                          {cart.status}
                        </span>
                      </div>
                      <div className="space-y-1 text-xs text-slate-600">
                        <p className="flex justify-between">
                          <span>Battery:</span>
                          <span className="font-bold text-slate-800">{cart.battery_percentage}%</span>
                        </p>
                        <p className="flex justify-between">
                          <span>Current Speed:</span>
                          <span className="font-bold text-slate-800">{pos.speed} km/h</span>
                        </p>
                        <p className="flex justify-between">
                          <span>Seats:</span>
                          <span className="font-bold text-emerald-600">{cart.available_seats} / {cart.total_seats} free</span>
                        </p>
                        <p className="flex justify-between">
                          <span>Route:</span>
                          <span className="font-bold text-slate-800">{cart.route_code || 'Express'}</span>
                        </p>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>

          {/* Map Overlay Badge */}
          <div className="absolute top-4 right-4 z-[400] bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 shadow-md flex items-center space-x-2 text-xs font-bold text-slate-700">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
            <span>Lovely Professional University (600+ Acres)</span>
          </div>
        </div>

        {/* Carts List Sidebar */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 flex flex-col overflow-hidden">
          <div className="mb-4 pb-3 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-900">Fleet Units ({carts.length})</h2>
            <span className="text-xs text-slate-500 font-semibold">Click to track</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {carts.map((cart) => {
              const pos = cartPositions[cart.cart_number] || { speed: 0 };
              const isSelected = selectedCart?.id === cart.id;

              return (
                <div
                  key={cart.id}
                  onClick={() => handleLocateCart(cart)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                      : 'border-slate-100 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-slate-900">{cart.cart_number}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        cart.status === 'ACTIVE'
                          ? 'bg-emerald-100 text-emerald-800'
                          : cart.status === 'CHARGING'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {cart.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
                    <div>
                      <span className="block text-[10px] text-slate-400 uppercase font-semibold">Speed</span>
                      <span className="font-bold text-slate-800">{pos.speed} km/h</span>
                    </div>
                    <div>
                      <span className="block text-[10px] text-slate-400 uppercase font-semibold">Battery</span>
                      <span className="font-bold text-slate-800">{cart.battery_percentage}%</span>
                    </div>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-slate-100/60 flex items-center justify-between text-xs">
                    <span className="text-slate-400">{cart.route_code || 'Unassigned'}</span>
                    <span className="text-blue-600 font-semibold hover:underline flex items-center">
                      <MapPin className="w-3 h-3 mr-0.5" />
                      Center on map
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

