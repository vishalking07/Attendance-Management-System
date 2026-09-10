import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus } from 'lucide-react';
import api from '../../api/client';

const CorrectionRequests = () => {
  const [corrections, setCorrections] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ date: '', claimed_time: '09:15 AM', reason: '' });

  useEffect(() => {
    fetchCorrections();
  }, []);

  const fetchCorrections = async () => {
    try {
      const res = await api.get('/corrections');
      setCorrections(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/corrections', form);
      setShowModal(false);
      fetchCorrections();
    } catch (err) {
      alert("Failed to submit correction request.");
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Attendance Correction Requests</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Submit manual override claims with timestamp details for faculty advisor review.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-bold shadow-md shadow-purple-600/20 flex items-center space-x-2 transition font-heading"
        >
          <Plus className="w-4 h-4" />
          <span>Raise Correction</span>
        </button>
      </div>

      <div className="app-card rounded-2xl overflow-hidden border border-purple-100/90 shadow-sm bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-4">Date & Claimed Time</th>
                <th className="p-4">Reason / Glitch Details</th>
                <th className="p-4">Approval Status</th>
                <th className="p-4">Submitted On</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
              {corrections.length === 0 ? (
                <tr>
                  <td colSpan="4" className="p-8 text-center text-slate-400 text-xs">
                    No correction requests filed yet.
                  </td>
                </tr>
              ) : (
                corrections.map((c) => (
                  <tr key={c.id} className="hover:bg-purple-50/40 transition">
                    <td className="p-4 font-mono font-bold text-[#7C3AED]">{c.date} ({c.claimed_time})</td>
                    <td className="p-4 text-slate-800 font-medium">{c.reason}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                        c.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                        (c.status === 'REJECTED' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200')
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-500 font-mono text-[11px]">{new Date(c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="app-card rounded-3xl p-6 border border-purple-100 max-w-md w-full space-y-4 bg-white shadow-2xl">
            <h3 className="font-black text-base text-slate-900">Raise Attendance Correction</h3>
            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-700 font-bold block mb-1">Date</label>
                  <input type="date" required value={form.date} onChange={(e) => setForm({...form, date: e.target.value})} className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
                <div>
                  <label className="text-slate-700 font-bold block mb-1">Claimed Check-in Time</label>
                  <input type="text" required value={form.claimed_time} onChange={(e) => setForm({...form, claimed_time: e.target.value})} className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-bold block mb-1">Reason (e.g., Camera or Lighting Glitch)</label>
                <textarea required value={form.reason} onChange={(e) => setForm({...form, reason: e.target.value})} className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400 h-20" placeholder="Webcam lighting issue in room 302, low network signal during OTP..." />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-purple-100">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 font-semibold hover:bg-slate-200">Cancel</button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-[#7C3AED] text-white font-bold hover:bg-[#6D28D9] shadow-sm">Submit Correction</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CorrectionRequests;
