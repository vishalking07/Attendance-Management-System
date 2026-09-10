import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, CheckCircle2, XCircle } from 'lucide-react';
import api from '../../api/client';

const AttendanceCalendar = () => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get('/attendance/history');
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Attendance Log & Calendar</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Complete record of your daily biometric, OTP, and manual attendance marks.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {history.length} Sessions Logged
        </span>
      </div>

      <div className="app-card rounded-2xl overflow-hidden border border-purple-100/90 shadow-sm bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-4">Date</th>
                <th className="p-4">Marked Status</th>
                <th className="p-4">Biometric Confidence</th>
                <th className="p-4">Verification Method</th>
                <th className="p-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
              {history.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-slate-400 text-xs">
                    No attendance records found. Check in via biometric capture to generate logs.
                  </td>
                </tr>
              ) : (
                history.map((h) => (
                  <tr key={h.id} className="hover:bg-purple-50/40 transition">
                    <td className="p-4 font-mono font-bold text-slate-900">{h.date}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                        h.status === 'PRESENT' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
                      }`}>
                        {h.status}
                      </span>
                    </td>
                    <td className="p-4 font-mono font-bold text-[#7C3AED]">{(h.confidence_score * 100).toFixed(1)}%</td>
                    <td className="p-4 font-mono text-slate-600 font-medium">{h.verification_method}</td>
                    <td className="p-4 text-slate-400 text-[11px] font-mono">{new Date(h.marked_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AttendanceCalendar;
