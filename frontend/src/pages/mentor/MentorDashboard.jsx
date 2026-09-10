import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Users, AlertTriangle, CheckSquare, Bell, BrainCircuit, Scan, Flame, ShieldAlert, Sparkles, TrendingDown } from 'lucide-react';
import api from '../../api/client';
import FacultyScannerModal from '../../components/FacultyScannerModal';

const MentorDashboard = () => {
  const { user } = useAuth();
  const [mentees, setMentees] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isScannerOpen, setIsScannerOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [mRes, pRes] = await Promise.all([
        api.get('/users?role=STUDENT'),
        api.get('/predictions')
      ]);
      setMentees(mRes.data);
      setPredictions(pRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const highRiskCount = predictions.filter(p => p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM').length;

  return (
    <div className="space-y-5 pb-2">
      {/* Header with Quick Action Scanner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Faculty Advisor Dashboard
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Advisement for assigned mentees, velocity burn-rate alerts & dynamic classroom verification.
          </p>
        </div>

        {/* Module 10: Faculty Smart Pass Scanner Launcher */}
        <button
          onClick={() => setIsScannerOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-purple-700 to-[#7C3AED] hover:from-purple-800 hover:to-purple-700 text-white font-black text-xs shadow-md shadow-purple-900/20 transition-all font-heading self-start sm:self-auto"
        >
          <Scan className="w-4 h-4" />
          <span>Launch Smart Pass Scanner</span>
        </button>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="app-card p-5 rounded-2xl space-y-1.5 border border-purple-100/90">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Assigned Mentees</span>
          <p className="text-3xl font-black text-slate-900 font-heading tracking-tight">{mentees.length}</p>
          <span className="text-[10px] text-purple-700 font-bold px-2 py-0.5 rounded-full bg-purple-50 inline-block border border-purple-100">
            Active Advisement
          </span>
        </div>
        <div className="app-card-active p-5 rounded-2xl space-y-1.5">
          <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">Medium / High Risk</span>
          <p className="text-3xl font-black text-[#7C3AED] font-heading tracking-tight">{highRiskCount}</p>
          <span className="text-[10px] text-rose-700 font-bold px-2 py-0.5 rounded-full bg-rose-50 inline-block border border-rose-200">
            Flagged by XGBoost ML
          </span>
        </div>
        <div className="app-card p-5 rounded-2xl space-y-1.5 border border-purple-100/90">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Pending Approvals</span>
          <p className="text-3xl font-black text-emerald-600 font-heading tracking-tight">2 Requests</p>
          <span className="text-[10px] text-emerald-700 font-bold px-2 py-0.5 rounded-full bg-emerald-50 inline-block border border-emerald-200">
            Leave & Corrections
          </span>
        </div>
      </div>

      {/* Module 4: High-Burn Velocity Drop Alert Banner */}
      <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-950 text-xs flex items-start space-x-3 shadow-sm">
        <div className="w-8 h-8 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Flame className="w-4 h-4 animate-pulse" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-rose-950 font-heading">
              Critical Velocity Burn-Rate Alert (Velocity &lt; -3.0%/wk)
            </span>
            <span className="text-[10px] font-mono font-bold text-rose-700 bg-rose-200/70 px-2 py-0.5 rounded">
              High Priority
            </span>
          </div>
          <p className="text-rose-800 text-[11px] mt-0.5 leading-relaxed">
            Mentee <strong>Sarah Jenkins (-3.4%/wk)</strong> and <strong>Marcus Vance (-4.2%/wk)</strong> have accelerating absence momentum. Risk of semester debarment within 14 days without active intervention.
          </p>
        </div>
      </div>

      {/* Module 7: Unsupervised Anomaly & Proxy Radar Preview */}
      <div className="app-card p-4 rounded-2xl border border-purple-200/80 bg-purple-50/50 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-[#7C3AED]" />
            <h3 className="text-xs font-black uppercase tracking-wider text-purple-950 font-heading">
              Proxy & Spatial-Temporal Anomaly Radar
            </h3>
          </div>
          <span className="text-[10px] font-mono font-bold text-purple-700">
            Isolation Forest Engine
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-white border border-purple-100 flex items-start justify-between">
            <div>
              <span className="font-bold text-slate-800 block">Marcus Vance (usr_stu_002)</span>
              <span className="text-[11px] text-slate-500">Perimeter Proximity: 492m / 500m geofence edge</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 font-mono">
              74.5% Anomaly
            </span>
          </div>
          <div className="p-3 rounded-xl bg-white border border-purple-100 flex items-start justify-between">
            <div>
              <span className="font-bold text-slate-800 block">Elena Rostova (usr_stu_003)</span>
              <span className="text-[11px] text-slate-500">GPS Jitter detected on mobile client</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 font-mono">
              42.0% Moderate
            </span>
          </div>
        </div>
      </div>

      {/* Mentee List Table */}
      <div className="app-card rounded-2xl p-5 sm:p-6 space-y-4 border border-purple-100/90">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-black text-slate-900 font-heading uppercase tracking-wider">
              Mentee Risk Overview & SHAP Explainability
            </h3>
            <p className="text-[11px] text-slate-500">Real-time attendance projection and key influencing feature vectors.</p>
          </div>
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
            {predictions.length} Total Monitored
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-3.5 rounded-l-xl">Mentee Name</th>
                <th className="p-3.5">Risk Category</th>
                <th className="p-3.5">Predicted Score</th>
                <th className="p-3.5">Attendance %</th>
                <th className="p-3.5 rounded-r-xl">Primary Factor (SHAP)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
              {predictions.map((p) => (
                <tr key={p.student_id} className="hover:bg-purple-50/40 transition">
                  <td className="p-3.5 font-bold text-slate-900">{p.student_name}</td>
                  <td className="p-3.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                      p.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                      p.risk_level === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}>
                      {p.risk_level} RISK
                    </span>
                  </td>
                  <td className="p-3.5 font-mono font-black text-[#7C3AED] text-sm">{p.predicted_score}%</td>
                  <td className="p-3.5 font-mono font-bold text-slate-800">{p.attendance_pct}%</td>
                  <td className="p-3.5 text-slate-600 font-medium">{p.shap_top_features?.[0]?.description || 'Normal Attendance Distribution'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Module 10: Faculty Scanner Modal */}
      <FacultyScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onAttendanceMarked={fetchData}
      />
    </div>
  );
};

export default MentorDashboard;
