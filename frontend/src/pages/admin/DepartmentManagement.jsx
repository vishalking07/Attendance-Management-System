import React, { useState, useEffect } from 'react';
import { Building, Plus, Users, Shield, Search, X, CheckCircle2, Sparkles, GraduationCap } from 'lucide-react';
import api from '../../api/client';

const DepartmentManagement = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', code: '' });
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

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

  const handleCreateDepartment = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.code) return;
    setSubmitting(true);
    try {
      await api.post('/departments', {
        name: formData.name,
        code: formData.code.toUpperCase()
      });
      setFormData({ name: '', code: '' });
      setIsAddOpen(false);
      setSuccessMsg('New department created successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
      fetchDepts();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredDepts = departments.filter(d => 
    d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.hod_name && d.hod_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const totalStudents = departments.reduce((acc, d) => acc + (d.student_count || 0), 0);

  return (
    <div className="space-y-5 pb-2">
      {/* Header with Title & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Academic Department Governance
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Manage institutional engineering disciplines, HOD leadership allocations, and student roll strengths.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <span className="text-[10px] font-mono font-bold px-3 py-1.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
            {departments.length} Departments • {totalStudents} Enrolled
          </span>
          <button
            onClick={() => setIsAddOpen(true)}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-[#7C3AED] hover:bg-purple-700 text-white font-bold text-xs shadow-md shadow-purple-900/15 transition font-heading"
          >
            <Plus className="w-4 h-4" />
            <span>Add Department</span>
          </button>
        </div>
      </div>

      {/* Success Notification */}
      {successMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center space-x-2 animate-scaleUp">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span className="font-bold">{successMsg}</span>
        </div>
      )}

      {/* Search & Stats Bar */}
      <div className="flex items-center space-x-3 bg-white p-2 rounded-2xl border border-purple-100 shadow-sm">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search departments by name, code (e.g. AI-DS, CS, CYS), or HOD name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-50/70 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/20 focus:border-[#7C3AED] transition"
          />
        </div>
      </div>

      {/* Departments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredDepts.map((d) => (
          <div
            key={d.id}
            className="app-card p-5 rounded-2xl border border-purple-100/90 space-y-4 bg-white shadow-sm hover:border-purple-300 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-start justify-between border-b border-purple-50 pb-3">
              <div className="space-y-1 max-w-[78%]">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded-md bg-purple-100/80 text-purple-900 font-mono font-black text-[10px]">
                    {d.code}
                  </span>
                  <span className="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md font-bold font-mono">
                    Zone Active
                  </span>
                </div>
                <h3 className="font-black text-sm sm:text-base text-slate-900 font-heading leading-tight">
                  {d.name}
                </h3>
              </div>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-50 to-purple-100 text-[#7C3AED] flex items-center justify-center border border-purple-200/60 shadow-inner flex-shrink-0">
                <Building className="w-5 h-5" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#FAF8FE] border border-purple-100/80 space-y-0.5">
                <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider font-mono">
                  Head of Department
                </span>
                <span className="font-bold text-slate-900 font-heading text-xs truncate block" title={d.hod_name}>
                  {d.hod_name || 'Unassigned'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-purple-50/50 border border-purple-100/80 space-y-0.5">
                <span className="text-purple-600 block text-[10px] font-bold uppercase tracking-wider font-mono">
                  Student Cohort
                </span>
                <span className="font-mono font-black text-[#7C3AED] text-xs sm:text-sm block">
                  {d.student_count || 1} Enrolled
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDepts.length === 0 && (
        <div className="p-8 text-center text-xs text-slate-400 bg-white rounded-2xl border border-purple-100">
          No departments found matching "{searchTerm}".
        </div>
      )}

      {/* Add Department Modal */}
      {isAddOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-purple-100 overflow-hidden">
            <div className="px-6 py-4 bg-gradient-to-r from-purple-900 via-[#7C3AED] to-purple-800 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Building className="w-5 h-5" />
                <h3 className="text-sm font-black font-heading tracking-wider uppercase">
                  Add Academic Department
                </h3>
              </div>
              <button
                onClick={() => setIsAddOpen(false)}
                className="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateDepartment} className="p-6 space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Department Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Chemical & Bio-Process Engineering"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-[#7C3AED] text-xs"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Department Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CHE"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-[#7C3AED] text-xs uppercase font-mono font-bold"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsAddOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-[#7C3AED] text-white font-bold hover:bg-purple-700 transition shadow-md text-xs font-heading"
                >
                  {submitting ? 'Creating...' : 'Create Department'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DepartmentManagement;
