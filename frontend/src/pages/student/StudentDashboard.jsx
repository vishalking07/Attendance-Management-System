import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  CheckSquare, BrainCircuit, ArrowRight, Laptop, Database, BarChart3,
  Coins, CreditCard, ShieldCheck, AlertTriangle, Sparkles, QrCode, TrendingUp, Gauge, Users, Camera
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import WhatIfSimulatorModal from '../../components/WhatIfSimulatorModal';
import SmartPassModal from '../../components/SmartPassModal';
import BiometricEnrollModal from '../../components/BiometricEnrollModal';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [prediction, setPrediction] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isWhatIfOpen, setIsWhatIfOpen] = useState(false);
  const [isSmartPassOpen, setIsSmartPassOpen] = useState(false);
  const [isEnrollOpen, setIsEnrollOpen] = useState(false);
  const [velocity, setVelocity] = useState({
    velocity_rate_per_week: 1.8,
    velocity_status: 'STABLE',
    bunk_budget_75_pct: 3,
    bunk_budget_80_pct: 1,
    summary: 'You can safely miss up to 3 classes while remaining strictly above the 75% cutoff.'
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [pRes, aRes, vRes] = await Promise.all([
        api.get('/predictions'),
        api.get('/attendance/history'),
        api.get(`/attendance/velocity/${user?.id || 'usr_student_2'}`).catch(() => null)
      ]);
      if (pRes.data && pRes.data.length > 0) setPrediction(pRes.data[0]);
      setAttendanceRecords(aRes.data);
      if (vRes && vRes.data) setVelocity(vRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const attPct = prediction?.attendance_pct || 78.5;
  const isShortage = attPct < 75.0;
  const todayFormatted = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const firstName = user?.name?.split(' ')[0] || 'John';

  return (
    <div className="space-y-5 pb-2">
      {/* 1. HERO WELCOME BANNER MATCHING MODERN EXECUTIVE DASHBOARD */}
      <div className="relative overflow-hidden rounded-[1.75rem] sm:rounded-[2rem] bg-gradient-to-r from-[#8B5CF6] via-[#7C3AED] to-[#5B21B6] text-white px-6 py-5 sm:px-7 sm:py-6 shadow-xl shadow-purple-900/15">
        {/* Soft background glow circles */}
        <div className="absolute -top-10 right-1/4 w-48 h-48 bg-white/15 rounded-full blur-2xl pointer-events-none"></div>
        <div className="absolute -bottom-10 right-10 w-40 h-40 bg-purple-400/20 rounded-full blur-xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
          <div className="space-y-1.5 max-w-xl">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full bg-white/15 backdrop-blur-md text-[10px] font-bold tracking-wider text-purple-100 uppercase border border-white/20">
                {todayFormatted}
              </span>
              <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-200 text-[10px] font-bold border border-emerald-400/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Dual-Signal GPS + WiFi</span>
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-black tracking-tight text-white font-heading">
              Welcome back, {firstName}!
            </h2>
            <p className="text-xs text-purple-100/90 font-medium leading-relaxed">
              Real-time biometric validation, prescriptive What-If modeling & smart attendance telemetry.
            </p>
            <div className="pt-2 flex flex-wrap gap-2.5">
              <Link
                to="/student/checkin"
                className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-white text-[#6D28D9] font-black text-xs shadow-md hover:bg-purple-50 transition-all hover:scale-[1.02] duration-150 font-heading"
              >
                <CheckSquare className="w-4 h-4 text-[#7C3AED]" />
                <span>Mark Attendance</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              
              {/* Module 1: What-If Launcher */}
              <button
                onClick={() => setIsWhatIfOpen(true)}
                className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-purple-900/40 hover:bg-purple-900/60 text-white font-bold text-xs backdrop-blur-md border border-white/20 transition-all"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>"What-If" Prognosis</span>
              </button>

              {/* Module 10: Smart Pass Launcher */}
              <button
                onClick={() => setIsSmartPassOpen(true)}
                className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-white/15 hover:bg-white/25 text-white font-bold text-xs backdrop-blur-md border border-white/20 transition-all"
              >
                <QrCode className="w-3.5 h-3.5 text-purple-200" />
                <span>Digital Smart Pass</span>
              </button>

              {/* Biometric Face Registration Launcher */}
              <button
                onClick={() => setIsEnrollOpen(true)}
                className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-purple-900/40 hover:bg-purple-900/60 text-white font-bold text-xs backdrop-blur-md border border-white/20 transition-all"
              >
                <Camera className="w-3.5 h-3.5 text-purple-200" />
                <span>Register Face Biometric</span>
              </button>
            </div>
          </div>

          {/* Right Student Portrait Avatar */}
          <div className="hidden md:flex items-center space-x-3 pr-2">
            <div className="relative">
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white/15 backdrop-blur-md p-1.5 flex items-center justify-center border border-white/25 shadow-inner">
                <img
                  src={user?.profile_photo?.includes('dicebear') ? "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80" : (user?.profile_photo || "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80")}
                  alt="Student Portrait"
                  className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl object-cover drop-shadow-md"
                />
              </div>
              <div className="absolute -bottom-2 -right-1 bg-white text-[#6D28D9] rounded-full px-2.5 py-0.5 text-[9px] font-black shadow-md border border-purple-200 uppercase tracking-wider">
                GPS Verified
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SHORTAGE ALERT IF ATTENDANCE < 75% */}
      {isShortage && (
        <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200/90 text-rose-800 text-xs flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-rose-500 flex-shrink-0 animate-pulse" />
            <div>
              <span className="font-bold text-xs block text-rose-900 font-heading">Attendance Shortage Warning!</span>
              <p className="text-rose-700 text-[11px] leading-tight mt-0.5">
                Your overall attendance is currently <strong className="font-extrabold">{attPct}%</strong> (under 75.0% mandatory requirement). File a correction or medical leave request.
              </p>
            </div>
          </div>
          <Link to="/student/corrections" className="px-3 py-1.5 rounded-xl bg-rose-600 text-white font-bold text-xs hover:bg-rose-700 shadow-sm flex-shrink-0 ml-3">
            Submit Correction
          </Link>
        </div>
      )}

      {/* 2. MAIN LAYOUT: LEFT CONTENT + RIGHT COLUMN */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* LEFT 2 COLUMNS: STATUS METRICS & ENROLLED COURSES */}
        <div className="lg:col-span-2 space-y-5">
          {/* Section: 3 Cards ("Finance" style from reference image) */}
          <div>
            <div className="flex items-center justify-between mb-2.5 px-0.5">
              <h3 className="font-black text-xs uppercase tracking-wider text-slate-800 font-heading">
                Attendance & Performance Metrics
              </h3>
              <Link to="/student/performance" className="text-xs font-bold text-[#7C3AED] hover:underline">
                See analytics →
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
              {/* Card 1: Normal White Card */}
              <div className="app-card p-4 sm:p-5 rounded-2xl flex flex-col items-center justify-center text-center space-y-2.5 relative">
                <div className="w-11 h-11 rounded-2xl bg-[#F5F2FC] text-[#7C3AED] flex items-center justify-center border border-purple-100">
                  <Coins className="w-5 h-5 text-[#8B5CF6]" />
                </div>
                <div>
                  <h4 className="text-2xl sm:text-3xl font-black text-slate-900 font-heading tracking-tight">{attPct}%</h4>
                  <p className="text-xs text-slate-500 font-semibold mt-0.5">Total Recorded</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${
                  attPct >= 75 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
                }`}>
                  {attPct >= 75 ? 'Above Threshold' : 'Shortage Alert'}
                </span>
              </div>

              {/* Card 2: HIGHLIGHT ACTIVE CARD matching reference image (purple double-border!) */}
              <div className="app-card-active p-4 sm:p-5 rounded-2xl flex flex-col items-center justify-center text-center space-y-2.5 relative">
                <div className="w-11 h-11 rounded-2xl bg-[#EDE9FE] text-[#7C3AED] flex items-center justify-center shadow-inner">
                  <CreditCard className="w-5 h-5 text-[#7C3AED]" />
                </div>
                <div>
                  <h4 className="text-2xl sm:text-3xl font-black text-[#7C3AED] font-heading tracking-tight">
                    {prediction?.predicted_score || 85.0}%
                  </h4>
                  <p className="text-xs text-purple-900 font-bold mt-0.5">Predicted Performance</p>
                </div>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200 uppercase tracking-wider">
                  AI Projected Score
                </span>
              </div>

              {/* Card 3: Normal White Card */}
              <div className="app-card p-4 sm:p-5 rounded-2xl flex flex-col items-center justify-center text-center space-y-2.5 relative">
                <div className="w-11 h-11 rounded-2xl bg-[#F5F2FC] text-[#8B5CF6] flex items-center justify-center border border-purple-100">
                  <BarChart3 className="w-5 h-5 text-[#8B5CF6]" />
                </div>
                <div>
                  <h4 className="text-2xl sm:text-3xl font-black text-slate-900 font-heading tracking-tight">
                    {prediction?.risk_level || 'LOW'}
                  </h4>
                  <p className="text-xs text-slate-500 font-semibold mt-0.5">Risk Assessment</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${
                  prediction?.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                  prediction?.risk_level === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                  'bg-emerald-50 text-emerald-700 border-emerald-200'
                }`}>
                  {prediction?.risk_level || 'LOW'} Risk Tier
                </span>
              </div>
            </div>

            {/* Module 4: Dynamic Attendance Velocity & Bunk Budget Card */}
            <div className="mt-3.5 app-card p-4 rounded-2xl border border-purple-200/90 bg-gradient-to-r from-purple-50/70 via-white to-purple-50/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-purple-100 text-[#7C3AED] flex items-center justify-center flex-shrink-0">
                  <Gauge className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono font-extrabold uppercase tracking-wider text-purple-800">
                      Attendance Velocity & Bunk Budget
                    </span>
                    <span className={`px-2 py-0.5 rounded-md text-[9px] font-black uppercase font-mono ${
                      velocity.velocity_rate_per_week >= 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                    }`}>
                      {velocity.velocity_rate_per_week >= 0 ? `+${velocity.velocity_rate_per_week}%/wk` : `${velocity.velocity_rate_per_week}%/wk`}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-0.5">
                    {velocity.summary}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2 flex-shrink-0">
                <div className="px-3 py-1.5 rounded-xl bg-white border border-purple-200 text-center">
                  <span className="text-[10px] font-bold text-slate-500 font-mono block">Safe Absences</span>
                  <span className="text-base font-black text-[#7C3AED] font-mono">{velocity.bunk_budget_75_pct} Classes</span>
                </div>
                <button
                  onClick={() => setIsWhatIfOpen(true)}
                  className="px-3 py-1.5 rounded-xl bg-[#7C3AED] hover:bg-purple-700 text-white font-bold text-xs transition shadow-sm font-heading"
                >
                  Simulate
                </button>
              </div>
            </div>
          </div>

          {/* Section: Enrolled Courses matching reference image */}
          <div>
            <div className="flex items-center justify-between mb-2.5 px-0.5">
              <h3 className="font-black text-xs uppercase tracking-wider text-slate-800 font-heading">
                Enrolled Courses
              </h3>
              <span className="text-xs font-bold text-[#7C3AED] hover:underline cursor-pointer">
                View all (4)
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* Course Card 1: Highlighted border matching reference image */}
              <div className="app-card p-4 sm:p-5 rounded-2xl border-2 border-purple-300 flex items-center justify-between hover:shadow-md transition">
                <div className="space-y-2.5">
                  <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider px-2 py-0.5 rounded-md bg-purple-50 border border-purple-100">
                    CS-301 • 4 Credits
                  </span>
                  <h4 className="font-black text-xs sm:text-[13px] text-slate-900 leading-snug font-heading max-w-[160px]">
                    Object oriented programming
                  </h4>
                  <Link
                    to="/student/checkin"
                    className="inline-block px-4 py-1.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white font-bold text-xs shadow-sm transition text-center"
                  >
                    Check In
                  </Link>
                </div>
                <div className="w-13 h-13 sm:w-14 sm:h-14 rounded-2xl bg-[#FAF8FE] border border-purple-100 flex items-center justify-center text-[#8B5CF6]">
                  <Laptop className="w-7 h-7" />
                </div>
              </div>

              {/* Course Card 2: Soft lavender tinted matching reference image */}
              <div className="app-card p-4 sm:p-5 rounded-2xl bg-[#FAF8FE] border border-purple-100 flex items-center justify-between hover:shadow-md transition">
                <div className="space-y-2.5">
                  <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider px-2 py-0.5 rounded-md bg-purple-50 border border-purple-100">
                    CS-304 • 3 Credits
                  </span>
                  <h4 className="font-black text-xs sm:text-[13px] text-slate-900 leading-snug font-heading max-w-[160px]">
                    Fundamentals of database systems
                  </h4>
                  <Link
                    to="/student/checkin"
                    className="inline-block px-4 py-1.5 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] text-white font-bold text-xs shadow-sm transition text-center"
                  >
                    Check In
                  </Link>
                </div>
                <div className="w-13 h-13 sm:w-14 sm:h-14 rounded-2xl bg-white border border-purple-100 flex items-center justify-center text-[#8B5CF6]">
                  <Database className="w-7 h-7" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: PROJECT TEAMMATES & DAILY NOTICE */}
        <div className="space-y-5">
          {/* Section: Project Teammates */}
          <div>
            <div className="flex items-center justify-between mb-2.5 px-0.5">
              <h3 className="font-black text-xs uppercase tracking-wider text-slate-800 font-heading flex items-center space-x-1.5">
                <Users className="w-3.5 h-3.5 text-[#7C3AED]" />
                <span>Project Teammates</span>
              </h3>
              <span className="text-[10px] font-bold text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded-full">
                Bio-XAI Core Team
              </span>
            </div>

            <div className="app-card p-4 rounded-2xl grid grid-cols-2 gap-3 border border-purple-100/90 shadow-sm bg-white">
              <div className="text-center space-y-1.5 p-3 rounded-2xl bg-gradient-to-b from-purple-50/50 to-white border border-purple-100 hover:border-purple-300 transition">
                <div className="w-14 h-14 rounded-full ring-2 ring-[#7C3AED] p-0.5 mx-auto bg-purple-100 overflow-hidden shadow-md">
                  <img
                    src="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80"
                    alt="Vishal"
                    className="w-full h-full rounded-full object-cover"
                  />
                </div>
                <div>
                  <p className="text-xs font-black text-slate-900 font-heading leading-tight">Vishal</p>
                  <p className="text-[10px] text-[#7C3AED] font-bold mt-0.5 uppercase tracking-wider">Team Lead</p>
                </div>
              </div>

              <div className="text-center space-y-1.5 p-3 rounded-2xl bg-gradient-to-b from-purple-50/50 to-white border border-purple-100 hover:border-purple-300 transition">
                <div className="w-14 h-14 rounded-full ring-2 ring-[#7C3AED] p-0.5 mx-auto bg-purple-100 overflow-hidden shadow-md">
                  <img
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80"
                    alt="Nithishkumar"
                    className="w-full h-full rounded-full object-cover"
                  />
                </div>
                <div>
                  <p className="text-xs font-black text-slate-900 font-heading leading-tight">Nithishkumar</p>
                  <p className="text-[10px] text-[#7C3AED] font-bold mt-0.5 uppercase tracking-wider">Teammate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Section: Daily Notice matching reference card */}
          <div>
            <div className="flex items-center justify-between mb-2.5 px-0.5">
              <h3 className="font-black text-xs uppercase tracking-wider text-slate-800 font-heading">
                Daily Notices
              </h3>
              <Link to="/student/calendar" className="text-xs font-bold text-[#7C3AED] hover:underline">
                View log
              </Link>
            </div>

            <div className="app-card p-4 sm:p-5 rounded-2xl space-y-3.5 shadow-sm border border-purple-100/90">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-black text-xs text-slate-900 font-heading">Morning Biometric Cutoff</h4>
                  <span className="text-[9px] font-bold text-purple-700 px-2 py-0.5 rounded bg-purple-50">09:30 AM</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Daily biometric cutoff is enforced at 09:30 AM. Auto-absence alerts trigger for unrecorded students.
                </p>
                <Link to="/student/calendar" className="text-[11px] font-bold text-[#7C3AED] hover:underline inline-flex items-center space-x-1 pt-0.5">
                  <span>See calendar log</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="pt-3 border-t border-purple-100/70 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-black text-xs text-slate-900 font-heading">Midterm Eligibility Status</h4>
                  <span className="text-[9px] font-bold text-emerald-700 px-2 py-0.5 rounded bg-emerald-50">75% Req.</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Midterm examination eligibility requires a minimum of 75.0% validated biometric attendance.
                </p>
                <Link to="/student/performance" className="text-[11px] font-bold text-[#7C3AED] hover:underline inline-flex items-center space-x-1 pt-0.5">
                  <span>Check eligibility status</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </div>

          {/* Section: Module 8 Peer Percentile Benchmark */}
          <div>
            <div className="flex items-center justify-between mb-2.5 px-0.5">
              <h3 className="font-black text-xs uppercase tracking-wider text-slate-800 font-heading flex items-center">
                <Users className="w-3.5 h-3.5 mr-1.5 text-[#7C3AED]" />
                Peer Percentile Radar
              </h3>
              <span className="text-[10px] text-purple-700 font-bold font-mono">
                Anonymous CSE Cohort
              </span>
            </div>

            <div className="app-card p-4 rounded-2xl space-y-3 shadow-sm border border-purple-100/90">
              <div className="space-y-1 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 font-medium">Attendance Consistency</span>
                  <span className="font-mono font-black text-purple-700">Top 22% (78th %tile)</span>
                </div>
                <div className="w-full h-1.5 bg-purple-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#7C3AED] rounded-full" style={{ width: '78%' }}></div>
                </div>
              </div>

              <div className="space-y-1 text-xs pt-1">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 font-medium">Assignment Punctuality</span>
                  <span className="font-mono font-black text-purple-700">Top 15% (85th %tile)</span>
                </div>
                <div className="w-full h-1.5 bg-purple-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#8B5CF6] rounded-full" style={{ width: '85%' }}></div>
                </div>
              </div>

              <div className="space-y-1 text-xs pt-1">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 font-medium">Biometric Fidelity</span>
                  <span className="font-mono font-black text-emerald-600">Top 8% (92nd %tile)</span>
                </div>
                <div className="w-full h-1.5 bg-emerald-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Module 1: What-If Scenario Simulator Modal */}
      <WhatIfSimulatorModal
        isOpen={isWhatIfOpen}
        onClose={() => setIsWhatIfOpen(false)}
        studentId={user?.id}
        studentName={user?.name}
        initialAtt={attPct}
        initialExam={prediction?.exam_avg || 72.0}
      />

      {/* Module 10: Dynamic Digital Smart Pass Modal */}
      <SmartPassModal
        isOpen={isSmartPassOpen}
        onClose={() => setIsSmartPassOpen(false)}
        student={user}
      />

      {/* Biometric Face Registration Modal */}
      <BiometricEnrollModal
        isOpen={isEnrollOpen}
        onClose={() => setIsEnrollOpen(false)}
        studentId={user?.id}
        studentName={user?.name}
        onEnrolled={fetchData}
      />
    </div>
  );
};

export default StudentDashboard;
