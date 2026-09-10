import React, { useState, useEffect } from 'react';
import { Users, Building, ShieldAlert, Cpu, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import api from '../../api/client';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/analytics');
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load admin stats:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-purple-600 text-sm font-semibold">Loading System Analytics...</div>;

  return (
    <div className="space-y-5 pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Institution Analytics & Governance</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Campus-wide biometric attendance tracking, student risk overview, and department comparisons.</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-bold flex items-center space-x-1.5 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>All Services Operational</span>
          </span>
        </div>
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="app-card p-5 rounded-2xl space-y-2 border border-purple-100/90">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Total Students</span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center border border-purple-100">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900 font-heading tracking-tight">{stats?.total_students || 0}</p>
          <span className="text-[10px] text-purple-700 font-bold px-2 py-0.5 rounded-full bg-purple-50 inline-block border border-purple-100">
            Across {stats?.total_departments || 2} Departments
          </span>
        </div>

        <div className="app-card-active p-5 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">Overall Attendance</span>
            <div className="w-8 h-8 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-600/30">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-[#7C3AED] font-heading tracking-tight">{stats?.overall_attendance_pct}%</p>
          <span className="text-[10px] text-purple-700 font-extrabold px-2 py-0.5 rounded-full bg-purple-100 inline-block border border-purple-200">
            Target Threshold: 75.0%
          </span>
        </div>

        <div className="app-card p-5 rounded-2xl space-y-2 border border-purple-100/90">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">At-Risk Students</span>
            <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-500 flex items-center justify-center border border-rose-100">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-rose-600 font-heading tracking-tight">{stats?.at_risk_students_count || 0}</p>
          <span className="text-[10px] text-rose-700 font-bold px-2 py-0.5 rounded-full bg-rose-50 inline-block border border-rose-200">
            Flagged by XGBoost ML
          </span>
        </div>

        <div className="app-card p-5 rounded-2xl space-y-2 border border-purple-100/90">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Faculty Mentors</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
              <Building className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-900 font-heading tracking-tight">{stats?.total_mentors || 0}</p>
          <span className="text-[10px] text-emerald-700 font-bold px-2 py-0.5 rounded-full bg-emerald-50 inline-block border border-emerald-200">
            Round-Robin Active
          </span>
        </div>
      </div>

      {/* Chart: Department Attendance Comparison */}
      <div className="app-card rounded-2xl p-5 sm:p-6 space-y-4 border border-purple-100/90">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-black text-slate-900 font-heading uppercase tracking-wider">
              Department Attendance Comparison (%)
            </h3>
            <p className="text-[11px] text-slate-500">Benchmark attendance aggregated across registered academic faculties.</p>
          </div>
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
            Academic Year 2025-2026
          </span>
        </div>

        <div className="h-64 sm:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats?.department_stats || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1EDFA" vertical={false} />
              <XAxis dataKey="department_name" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E9D5FF', borderRadius: '14px', boxShadow: '0 10px 25px -5px rgba(124, 58, 237, 0.15)', fontSize: '12px' }} />
              <Bar dataKey="attendance_pct" fill="#7C3AED" radius={[8, 8, 0, 0]} barSize={42} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
