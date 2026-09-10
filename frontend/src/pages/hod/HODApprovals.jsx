import React, { useState, useEffect } from 'react';
import api from '../../api/client';

const HODApprovals = () => {
  const [leaves, setLeaves] = useState([]);
  const [corrections, setCorrections] = useState([]);
  const [loading, setLoading] = useState(true);

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
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveAction = async (id, action) => {
    try {
      await api.post('/leaves/approve', { request_id: id, action });
      fetchData();
    } catch (err) {
      alert("Failed to process request.");
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Department Approvals Queue</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Review escalated leave applications and attendance correction requests.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {leaves.filter(l => l.status === 'PENDING').length} Pending Requests
        </span>
      </div>

      <div className="app-card rounded-2xl p-5 sm:p-6 border border-purple-100/90 space-y-4 bg-white shadow-sm">
        <h3 className="text-sm font-black text-slate-900 font-heading uppercase tracking-wider">Department Leave Applications</h3>
        <div className="space-y-3 text-xs">
          {leaves.length === 0 ? <p className="text-slate-400 py-4 text-center">No leave requests found.</p> : (
            leaves.map(l => (
              <div key={l.id} className="p-4 rounded-xl bg-[#FAF8FE] border border-purple-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-purple-200 transition">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 font-heading">{l.student_name}</span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                      l.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                      (l.status === 'REJECTED' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200')
                    }`}>
                      {l.status}
                    </span>
                  </div>
                  <p className="text-slate-500 text-[11px] mt-1">Dates: {l.from_date} to {l.to_date} • Reason: {l.reason}</p>
                </div>
                {l.status === 'PENDING' && (
                  <div className="flex space-x-2">
                    <button onClick={() => handleLeaveAction(l.id, 'APPROVE')} className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-sm transition">Approve</button>
                    <button onClick={() => handleLeaveAction(l.id, 'REJECT')} className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold shadow-sm transition">Reject</button>
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

export default HODApprovals;
