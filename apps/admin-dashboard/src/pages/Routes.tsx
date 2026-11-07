import React, { useEffect, useState } from 'react';
import { AdminAPI } from '../services/api';
import { Route, MapPin, Clock, IndianRupee, RefreshCw } from 'lucide-react';

export const Routes: React.FC = () => {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRoutes = async () => {
    try {
      setLoading(true);
      const data = await AdminAPI.getRoutes();
      setRoutes(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoutes();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Campus Shuttle Routes</h1>
          <p className="text-sm text-slate-500 font-medium">Designated transit loops, waypoints, and passenger stops</p>
        </div>
        <button
          onClick={fetchRoutes}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {routes.map((route) => (
          <div
            key={route.id}
            className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-black rounded-lg">
                  {route.code}
                </span>
                <span className="text-xs font-bold text-slate-600 flex items-center">
                  <IndianRupee className="w-3.5 h-3.5 mr-0.5 text-slate-400" />
                  {route.fare_amount} INR
                </span>
              </div>

              <h2 className="text-lg font-bold text-slate-900">{route.name}</h2>
              <p className="text-xs text-slate-500 leading-relaxed">{route.description}</p>
            </div>

            {/* Stops Sequence */}
            <div className="space-y-3 pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1 text-blue-600" />
                Stop Sequence ({route.stops?.length || 0})
              </h3>

              <div className="space-y-2">
                {route.stops?.map((stop: any, idx: number) => (
                  <div
                    key={stop.id}
                    className="flex items-center justify-between text-xs p-2.5 rounded-xl bg-slate-50 border border-slate-100"
                  >
                    <div className="flex items-center space-x-2.5">
                      <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[10px] flex items-center justify-center">
                        {stop.sequence_order}
                      </span>
                      <span className="font-semibold text-slate-800">{stop.name}</span>
                    </div>
                    <span className="text-[11px] text-slate-400 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      +{stop.estimated_minutes}m
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

