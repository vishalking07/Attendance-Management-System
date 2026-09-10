import React, { useState, useEffect } from 'react';
import { Building, Plus, Users, Shield } from 'lucide-react';
import api from '../../api/client';

const DepartmentManagement = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDepts();
  }, []);

  const fetchDepts = async () => {
    try {
      const res = await api.get('/departments');
      setDepartments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Department Governance</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Manage academic departments, student allocations, and assigned HODs.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {departments.length} Departments Registered
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {departments.map((d) => (
          <div key={d.id} className="app-card p-5 sm:p-6 rounded-2xl border border-purple-100/90 space-y-4 bg-white shadow-sm hover:border-purple-200 transition">
            <div className="flex items-center justify-between border-b border-purple-50 pb-3">
              <div>
                <h3 className="font-black text-base text-slate-900 font-heading">{d.name}</h3>
                <span className="text-xs font-mono font-bold text-[#7C3AED]">Code: {d.code}</span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-[#F5F2FC] text-[#7C3AED] flex items-center justify-center border border-purple-100">
                <Building className="w-5 h-5" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#FAF8FE] border border-purple-100">
                <span className="text-slate-500 block text-[10px] font-medium">Head of Department (HOD)</span>
                <span className="font-bold text-slate-900 font-heading text-xs sm:text-sm">{d.hod_name || 'Unassigned'}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#FAF8FE] border border-purple-100">
                <span className="text-slate-500 block text-[10px] font-medium">Enrolled Students</span>
                <span className="font-extrabold text-[#7C3AED] font-heading text-xs sm:text-sm">{d.student_count || 0} Students</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DepartmentManagement;
