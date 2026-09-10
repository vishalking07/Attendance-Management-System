import React, { useState, useEffect } from 'react';
import { MapPin, Wifi, Radio, ShieldCheck, Plus, CheckCircle2, Lock } from 'lucide-react';
import api from '../../api/client';

const GeofenceConfig = () => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dualSignalMode, setDualSignalMode] = useState('STRICT'); // 'STRICT' | 'ADAPTIVE'
  const [wifiNetworks, setWifiNetworks] = useState([
    { ssid: 'EduNet-Secure-5G', bssid: '00:14:22:01:23:45', department: 'CS Building' },
    { ssid: 'CS-Lab-Mesh', bssid: '00:14:22:01:23:46', department: 'CS AI Labs' },
    { ssid: 'Campus-Mesh-IoT', bssid: '00:14:22:01:23:99', department: 'Main Academic Quad' }
  ]);

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const res = await api.get('/geofence');
      setZones(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Dual-Signal Geofence & Campus Network Hub
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Configure GPS polygon perimeters combined with campus WiFi BSSID signatures for spoof-proof attendance.
          </p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100 self-start sm:self-auto font-mono">
          {zones.length} Active Zones • Dual-Signal Active
        </span>
      </div>

      {/* Module 3: Dual-Signal Sensor Fusion Settings */}
      <div className="app-card p-5 rounded-2xl border border-purple-200/90 bg-gradient-to-r from-purple-50/80 via-white to-purple-50/50 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-purple-600 text-white flex items-center justify-center">
              <Wifi className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-black uppercase tracking-wider text-purple-950 font-heading">
                Campus WiFi BSSID & BLE Signature Fusion
              </h3>
              <p className="text-xs text-slate-600">
                Attendance check-in enforces matching campus subnet signature alongside GPS satellite fix.
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-bold text-slate-600">Policy:</span>
            <span className="px-2.5 py-1 rounded-lg bg-emerald-100 text-emerald-800 text-xs font-black uppercase font-mono">
              STRICT DUAL-LOCK
            </span>
          </div>
        </div>

        {/* Registered Authorized Networks */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          {wifiNetworks.map((net, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-white border border-purple-100 shadow-xs space-y-1 text-xs">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-900 truncate">{net.ssid}</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
              <p className="text-[10px] font-mono text-purple-700">{net.bssid}</p>
              <p className="text-[10px] text-slate-400 font-medium">{net.department}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Geofence Zones Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {zones.map((z) => (
          <div key={z.id} className="app-card p-5 sm:p-6 rounded-2xl border border-purple-100/90 space-y-4 bg-white shadow-sm hover:border-purple-200 transition">
            <div className="flex items-center justify-between border-b border-purple-50 pb-3">
              <div>
                <h3 className="font-black text-sm sm:text-base text-slate-900 font-heading">{z.name}</h3>
                <span className="text-xs font-mono font-bold text-[#7C3AED]">Zone ID: {z.id}</span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-[#F5F2FC] text-[#7C3AED] flex items-center justify-center border border-purple-100">
                <MapPin className="w-5 h-5" />
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Center Coordinates:</span>
                <span className="font-mono font-bold text-slate-900">{z.center_lat}, {z.center_lng}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Radius Boundary:</span>
                <span className="font-bold text-emerald-700 font-mono">{z.radius_meters} meters</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Polygon Vertices:</span>
                <span className="font-bold text-[#7C3AED]">{z.coordinates?.length || 4} Coordinate Points</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Network Pairing:</span>
                <span className="font-bold text-purple-800 font-mono">EduNet-Secure-5G</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#FAF8FE] border border-purple-100 font-mono text-[11px] text-slate-600 space-y-1">
              <span className="text-slate-400 block text-[10px] font-sans font-bold">Boundary GPS Perimeters:</span>
              {z.coordinates?.map((c, i) => (
                <div key={i} className="flex justify-between">
                  <span>P{i+1}: ({c.lat}, {c.lng})</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeofenceConfig;
