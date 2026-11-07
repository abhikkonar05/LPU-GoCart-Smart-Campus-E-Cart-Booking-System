import React, { useEffect, useState } from 'react';
import { AdminAPI } from '../services/api';
import { Camera, Radio, Shield, AlertCircle, RefreshCw, Eye } from 'lucide-react';

export const CCTV: React.FC = () => {
  const [devices, setDevices] = useState<any[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCCTV = async () => {
    try {
      setLoading(true);
      const data = await AdminAPI.getCCTVDevices();
      setDevices(data);
      if (data.length > 0 && !selectedDevice) {
        setSelectedDevice(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCCTV();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Onboard CCTV Surveillance</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 flex items-center">
              <Shield className="w-3 h-3 mr-1" />
              Authorized Campus Security Only
            </span>
          </div>
          <p className="text-sm text-slate-500 font-medium">Real-time connectivity monitoring for electric carts equipped with camera hardware</p>
        </div>
        <button
          onClick={fetchCCTV}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Video Stream + Devices Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stream Player Window */}
        <div className="lg:col-span-2 bg-slate-950 rounded-2xl p-6 text-white shadow-xl flex flex-col justify-between h-[520px] relative overflow-hidden border border-slate-800">
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-red-600 animate-ping"></div>
              <span className="text-xs font-bold tracking-wider uppercase text-red-400">LIVE FEED</span>
              <span className="text-xs text-slate-400 font-mono">
                {selectedDevice ? `${selectedDevice.cart_number} [${selectedDevice.device_serial}]` : 'Select Device'}
              </span>
            </div>
            <span className="text-xs font-bold px-2 py-0.5 bg-slate-800 rounded text-slate-300">
              1080p @ 30FPS • HLS
            </span>
          </div>

          {/* Video Placeholder Simulation */}
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 z-10">
            <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-blue-500 mb-4 shadow-inner">
              <Camera className="w-10 h-10 animate-pulse" />
            </div>
            <h3 className="text-lg font-bold text-white mb-1">
              {selectedDevice?.cart_number || 'LPU-CART-01'} Onboard Cabin Stream
            </h3>
            <p className="text-xs text-slate-400 max-w-sm">
              Live streaming channel connected to University Transportation NVR Gateway. Security authenticated.
            </p>
            <div className="mt-4 px-3 py-1 bg-slate-900 rounded-full border border-slate-800 text-[11px] text-emerald-400 font-mono">
              STATUS: {selectedDevice?.is_online ? 'ONLINE (0.2s Latency)' : 'CONNECTING...'}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-3 border-t border-slate-800/80 z-10">
            <span>Stream Source: {selectedDevice?.stream_url || 'https://demo-cctv.lpu.in/live/cart01.m3u8'}</span>
            <span>Lovely Professional University Security Division</span>
          </div>
        </div>

        {/* Registered Devices List */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h2 className="font-bold text-slate-900 text-sm uppercase tracking-wider">
            Connected Units ({devices.length})
          </h2>

          <div className="space-y-3">
            {devices.map((dev) => {
              const isSelected = selectedDevice?.id === dev.id;
              return (
                <div
                  key={dev.id}
                  onClick={() => setSelectedDevice(dev)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    isSelected
                      ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                      : 'border-slate-100 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-sm text-slate-900">{dev.cart_number}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        dev.is_online ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {dev.is_online ? 'ONLINE' : 'OFFLINE'}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-slate-500 mb-2">{dev.device_serial}</p>
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Protocol: {dev.stream_protocol}</span>
                    <span className="text-blue-600 font-semibold flex items-center">
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      View Stream
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-amber-600 mt-0.5" />
            <p>
              In accordance with university compliance, camera streams are strictly accessible to authorized campus dispatchers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

