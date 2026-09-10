import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { GraduationCap, KeyRound, Mail, ArrowRight, UserCheck, ShieldCheck } from 'lucide-react';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await login(email, password);
      setLoading(false);
      
      switch (user.role) {
        case 'ADMIN': navigate('/admin'); break;
        case 'HOD': navigate('/hod'); break;
        case 'MENTOR': navigate('/mentor'); break;
        case 'STUDENT': default: navigate('/student'); break;
      }
    } catch (err) {
      setLoading(false);
      setError(err.response?.data?.detail || "Invalid login credentials");
    }
  };

  const handleQuickLogin = (demoEmail, demoPw) => {
    setEmail(demoEmail);
    setPassword(demoPw);
  };

  return (
    <div className="h-screen w-screen bg-[#ECE6F8] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Decorative Soft Purple Blurs */}
      <div className="absolute top-10 left-10 w-96 h-96 bg-purple-300/30 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-indigo-300/30 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md app-card rounded-[2rem] p-7 sm:p-8 border border-purple-100 shadow-2xl relative z-10 space-y-6 bg-white">
        {/* Branding Emblem */}
        <div className="text-center space-y-1.5">
          <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center mx-auto shadow-xl shadow-purple-600/30 mb-3 text-white">
            <GraduationCap className="w-8 h-8 sm:w-9 sm:h-9" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight font-heading">Bio-XAI Portal</h1>
          <p className="text-xs text-slate-500 font-medium">Smart Attendance & Explainable Risk System</p>
        </div>

        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs text-center font-bold">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-purple-400 absolute left-3.5 top-3.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarah.jenkins@student.bioxai.edu"
                className="w-full bg-purple-50/40 border border-purple-100 rounded-2xl py-2.5 pl-10 pr-4 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400"
                required
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Password</label>
            <div className="relative">
              <KeyRound className="w-4 h-4 text-purple-400 absolute left-3.5 top-3.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-purple-50/40 border border-purple-100 rounded-2xl py-2.5 pl-10 pr-4 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xs shadow-lg shadow-purple-600/30 hover:opacity-95 transition flex items-center justify-center space-x-2"
          >
            <span>{loading ? "Authenticating..." : "Sign In to Portal"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* DEMO 1-CLICK QUICK-FILL BUTTONS */}
        <div className="border-t border-purple-100 pt-5 space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-600">
            <UserCheck className="w-4 h-4 text-purple-600" />
            <span>1-Click Demo Quick-Fill Roles:</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <button
              onClick={() => handleQuickLogin('admin@bioxai.edu', 'Admin@123')}
              className="px-3 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 text-left transition font-semibold truncate"
            >
              👑 Admin
            </button>
            <button
              onClick={() => handleQuickLogin('hod.cs@bioxai.edu', 'Hod@123')}
              className="px-3 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 text-left transition font-semibold truncate"
            >
              🎓 HOD (CS)
            </button>
            <button
              onClick={() => handleQuickLogin('mentor1.cs@bioxai.edu', 'Mentor@123')}
              className="px-3 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 text-left transition font-semibold truncate"
            >
              👨‍🏫 Mentor
            </button>
            <button
              onClick={() => handleQuickLogin('sarah.jenkins@student.bioxai.edu', 'Student@123')}
              className="px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white border border-purple-600 text-left transition font-bold truncate shadow-sm"
            >
              👨‍🎓 Student (Sarah)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
