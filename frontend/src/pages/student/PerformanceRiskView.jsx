import React, { useState, useEffect } from 'react';
import { BrainCircuit, Sparkles, CheckCircle2, TrendingUp, AlertTriangle, ShieldCheck, Sliders, Target, ArrowRight } from 'lucide-react';
import api from '../../api/client';
import WhatIfSimulatorModal from '../../components/WhatIfSimulatorModal';

const PerformanceRiskView = () => {
  const [prediction, setPrediction] = useState(null);
  const [isWhatIfOpen, setIsWhatIfOpen] = useState(false);

  useEffect(() => {
    fetchPrediction();
  }, []);

  const fetchPrediction = async () => {
    try {
      const res = await api.get('/predictions');
      if (res.data && res.data.length > 0) setPrediction(res.data[0]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Academic Prognosis & Explainable AI (SHAP)
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            XGBoost machine learning predictions with prescriptive What-If trajectory simulations.
          </p>
        </div>

        {/* Module 1: What-If Launcher Button */}
        <button
          onClick={() => setIsWhatIfOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-purple-700 to-[#7C3AED] hover:from-purple-800 hover:to-purple-700 text-white font-black text-xs shadow-md shadow-purple-900/20 transition-all font-heading self-start sm:self-auto"
        >
          <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
          <span>Launch "What-If" Simulator</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Risk Card */}
        <div className="app-card-active p-6 sm:p-7 rounded-2xl space-y-4 bg-white">
          <div className="flex items-center justify-between border-b border-purple-100 pb-3">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider font-mono">
              Predicted Academic Score
            </span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#7C3AED] flex items-center justify-center border border-purple-100">
              <BrainCircuit className="w-4 h-4" />
            </div>
          </div>
          <div className="text-center py-2">
            <p className="text-5xl font-black text-[#7C3AED] font-heading tracking-tight font-mono">
              {prediction?.predicted_score || 85.0}%
            </p>
            <span className={`inline-block mt-3 px-3 py-1 rounded-full text-xs font-extrabold border uppercase tracking-wider ${
              prediction?.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border-rose-200' :
              prediction?.risk_level === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border-amber-200' :
              'bg-emerald-50 text-emerald-700 border-emerald-200'
            }`}>
              {prediction?.risk_level || 'LOW'} RISK CATEGORY
            </span>
          </div>

          <div className="space-y-2.5 text-xs border-t border-purple-100 pt-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Attendance Contribution:</span>
              <span className="font-mono font-bold text-slate-900 text-sm">{prediction?.attendance_pct}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Exam Average Score:</span>
              <span className="font-mono font-bold text-slate-900 text-sm">{prediction?.exam_avg}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Assignment Completion Rate:</span>
              <span className="font-mono font-bold text-slate-900 text-sm">{prediction?.assignment_pct}%</span>
            </div>
          </div>
        </div>

        {/* Prescriptive What-If Advisory Card */}
        <div className="app-card p-6 sm:p-7 rounded-2xl space-y-4 text-xs bg-white border border-purple-100/90 shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-[#7C3AED] font-extrabold text-sm border-b border-purple-50 pb-3 font-heading">
              <Target className="w-4 h-4" />
              <span>Prescriptive Goal Simulator</span>
            </div>

            <div className="p-4 rounded-2xl bg-purple-50/70 border border-purple-100 space-y-1.5">
              <span className="font-bold text-purple-950 flex items-center space-x-1.5 text-xs">
                <Sparkles className="w-3.5 h-3.5 text-[#7C3AED]" />
                <span>Simulate Future Performance Scenarios</span>
              </span>
              <p className="text-slate-600 text-[11px] leading-relaxed">
                Test hypothetical outcomes: "If I attend the next 8 classes and score 85% on Internal 2, what will my new GPA projection be?"
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-100 space-y-1">
              <span className="font-bold text-emerald-900 flex items-center space-x-1.5 text-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Minimum Effort Optimizer</span>
              </span>
              <p className="text-slate-600 text-[11px] leading-relaxed">
                Calculates the exact number of consecutive classes required to exit risk tiers and clear the 75% cutoff.
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsWhatIfOpen(true)}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-700 to-[#7C3AED] text-white font-black text-xs uppercase tracking-wider flex items-center justify-center space-x-2 shadow-md shadow-purple-900/15 hover:shadow-purple-900/30 transition-all font-heading mt-3"
          >
            <Sliders className="w-4 h-4" />
            <span>Open Interactive Simulator Sandbox</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Module 1: What-If Modal */}
      <WhatIfSimulatorModal
        isOpen={isWhatIfOpen}
        onClose={() => setIsWhatIfOpen(false)}
        studentId={prediction?.student_id}
        studentName={prediction?.student_name}
        initialAtt={prediction?.attendance_pct || 78.5}
        initialExam={prediction?.exam_avg || 72.0}
      />
    </div>
  );
};

export default PerformanceRiskView;
