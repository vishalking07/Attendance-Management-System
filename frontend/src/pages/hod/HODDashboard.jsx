import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Users, AlertTriangle, TrendingUp, Lock, ShieldCheck, BarChart2, CheckCircle2, Award, FileText } from 'lucide-react';
import api from '../../api/client';
import LedgerIntegrityModal from '../../components/LedgerIntegrityModal';
import AICounselingDossierModal from '../../components/AICounselingDossierModal';

const HODDashboard = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isLedgerOpen, setIsLedgerOpen] = useState(false);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [sRes, pRes] = await Promise.all([
        api.get('/users?role=STUDENT'),
        api.get('/predictions')
      ]);
      setStudents(sRes.data);
      setPredictions(pRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const highRiskStudents = predictions.filter(p => p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM');

  return (
    <div className="space-y-5 pb-2">
      {/* Header with Ledger Verification Quick Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Department Overview (Computer Science)
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Departmental student cohort oversight, cross-batch momentum barometers & cryptographic ledger defense.
          </p>
        </div>

        {/* Module 6: Ledger Integrity Audit Launcher */}
        <button
          onClick={() => setIsLedgerOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-slate-950 via-purple-950 to-slate-900 hover:from-slate-900 hover:to-purple-900 text-white font-black text-xs shadow-md shadow-purple-900/20 transition-all font-heading self-start sm:self-auto border border-purple-800/40"
        >
          <Lock className="w-4 h-4 text-purple-300" />
          <span>Verify Ledger Integrity</span>
        </button>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="app-card p-5 rounded-2xl space-y-1.5 border border-purple-100/90">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Department Students</span>
          <p className="text-3xl font-black text-slate-900 font-heading tracking-tight">{students.length}</p>
          <span className="text-[10px] text-purple-700 font-bold px-2 py-0.5 rounded-full bg-purple-50 inline-block border border-purple-100">
            Enrolled in CS Cohort
          </span>
        </div>
        <div className="app-card-active p-5 rounded-2xl space-y-1.5">
          <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">At-Risk Students</span>
          <p className="text-3xl font-black text-rose-600 font-heading tracking-tight">{highRiskStudents.length}</p>
          <span className="text-[10px] text-rose-700 font-bold px-2 py-0.5 rounded-full bg-rose-50 inline-block border border-rose-200">
            Requires Faculty Counseling
          </span>
        </div>
        <div className="app-card p-5 rounded-2xl space-y-1.5 border border-purple-100/90">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Average Attendance</span>
          <p className="text-3xl font-black text-slate-900 font-heading tracking-tight">82.4%</p>
          <span className="text-[10px] text-emerald-700 font-bold px-2 py-0.5 rounded-full bg-emerald-50 inline-block border border-emerald-200">
            Above 75.0% Mandatory Target
          </span>
        </div>
      </div>

      {/* Module 4: Department Attendance Momentum Barometer */}
      <div className="app-card p-5 rounded-2xl border border-purple-100/90 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BarChart2 className="w-4 h-4 text-[#7C3AED]" />
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-800 font-heading">
              Cross-Batch Attendance Momentum Barometer
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            Weekly Velocity Differential
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-slate-800">Final Year (Batch 2026)</span>
              <span className="font-mono font-black text-emerald-600">+2.4%/wk</span>
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-lg font-black text-slate-900 font-mono">86.2%</span>
              <span className="text-[10px] text-emerald-700 font-medium">Strong Consistency</span>
            </div>
            <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: '86%' }}></div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-slate-800">Third Year (Batch 2027)</span>
              <span className="font-mono font-black text-purple-700">+0.8%/wk</span>
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-lg font-black text-slate-900 font-mono">81.4%</span>
              <span className="text-[10px] text-purple-700 font-medium">Stable Operating Range</span>
            </div>
            <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-[#7C3AED] rounded-full" style={{ width: '81%' }}></div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-rose-50/60 border border-rose-200 space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-rose-950">Second Year (Batch 2028)</span>
              <span className="font-mono font-black text-rose-700">-2.1%/wk</span>
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-lg font-black text-rose-950 font-mono">75.8%</span>
              <span className="text-[10px] text-rose-700 font-bold">Near Cutoff Boundary</span>
            </div>
            <div className="w-full h-1.5 bg-rose-200 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full" style={{ width: '75%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Module 5: Escalated Interventions Queue Notice */}
      <div className="p-4 rounded-2xl bg-purple-50/90 border border-purple-200 text-xs flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-purple-100 text-[#7C3AED] flex items-center justify-center flex-shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-xs text-purple-950 font-heading block">
              1 Escalated Mentoring Dossier Awaiting HOD Endorsement
            </span>
            <p className="text-purple-800 text-[11px] mt-0.5">
              Dr. Alan Turing submitted an AI counseling recovery plan for <strong>Vishal (CS Department)</strong>.
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            setSelectedStudent({ id: 'usr_student_1', name: 'Vishal' });
            setIsDossierOpen(true);
          }}
          className="px-3.5 py-1.5 rounded-xl bg-[#7C3AED] hover:bg-purple-700 text-white font-bold text-xs transition shadow-sm font-heading flex-shrink-0"
        >
          Review & Sign Off
        </button>
      </div>

      {/* At Risk Table */}
      <div className="app-card rounded-2xl p-5 sm:p-6 space-y-4 border border-purple-100/90">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-500 flex items-center justify-center border border-rose-100">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900 font-heading uppercase tracking-wider">
                Department Student Performance & Risk Monitor
              </h3>
              <p className="text-[11px] text-slate-500">Live ML telemetry evaluating student drop-off risk factors.</p>
            </div>
          </div>
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
            {predictions.length} Total Monitored
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-3.5 rounded-l-xl">Student Name</th>
                <th className="p-3.5">Risk Level</th>
                <th className="p-3.5">Predicted Score</th>
                <th className="p-3.5">Attendance %</th>
                <th className="p-3.5">Primary Factor (SHAP)</th>
                <th className="p-3.5 rounded-r-xl text-right">Intervention</th>
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
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => {
                        setSelectedStudent({ id: p.student_id, name: p.student_name });
                        setIsDossierOpen(true);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-purple-50 text-[#7C3AED] hover:bg-purple-100 font-bold text-[11px] transition font-heading"
                    >
                      Dossier
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Module 6: Ledger Integrity Modal */}
      <LedgerIntegrityModal
        isOpen={isLedgerOpen}
        onClose={() => setIsLedgerOpen(false)}
      />

      {/* Module 5: AI Counseling Dossier Modal */}
      <AICounselingDossierModal
        isOpen={isDossierOpen}
        onClose={() => setIsDossierOpen(false)}
        studentId={selectedStudent?.id}
        studentName={selectedStudent?.name}
        userRole="HOD"
      />
    </div>
  );
};

export default HODDashboard;
