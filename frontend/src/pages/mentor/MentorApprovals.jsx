import React, { useState, useEffect } from 'react';
import api from '../../api/client';

const MentorApprovals = () => {
  const [leaves, setLeaves] = useState([]);
  const [corrections, setCorrections] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [lRes, cRes] = await Promise.all([
        api.get('/leaves'),
        api.get('/corrections')
      ]);
      setLeaves(lRes.data);
      setCorrections(cRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCorrection = async (id, action) => {
    try {
      await api.post('/corrections/approve', { request_id: id, action });
      fetchData();
    } catch (err) {
      alert("Error processing correction request.");
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Mentee Request Approvals</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Review attendance correction requests and medical leave notifications from your assigned mentees.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {corrections.filter(c => c.status === 'PENDING').length} Pending Review
        </span>
      </div>

      {/* Corrections Queue */}
      <div className="app-card rounded-2xl p-5 sm:p-6 border border-purple-100/90 space-y-4 bg-white shadow-sm">
        <h3 className="text-sm font-black text-slate-900 font-heading uppercase tracking-wider">Attendance Correction Queue</h3>
        <div className="space-y-3 text-xs">
          {corrections.length === 0 ? (
            <p className="text-slate-400 text-center py-6 text-xs">No pending attendance correction requests.</p>
          ) : (
            corrections.map((c) => (
              <div key={c.id} className="p-4 rounded-xl bg-[#FAF8FE] border border-purple-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-purple-200 transition">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 font-heading">{c.student_name}</span>
                    <span className="text-[#7C3AED] font-mono font-bold">Date: {c.date}</span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                      c.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>{c.status}</span>
                  </div>
                  <p className="text-slate-600 text-[11px] mt-1 font-medium">Reason: {c.reason} (Claimed Time: {c.claimed_time})</p>
                </div>
                {c.status === 'PENDING' && (
                  <div className="flex space-x-2 flex-shrink-0">
                    <button onClick={() => handleCorrection(c.id, 'APPROVE')} className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition">Approve</button>
                    <button onClick={() => handleCorrection(c.id, 'REJECT')} className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm transition">Reject</button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MentorApprovals;
