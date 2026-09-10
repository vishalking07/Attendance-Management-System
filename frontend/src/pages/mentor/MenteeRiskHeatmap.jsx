import React, { useState, useEffect } from 'react';
import { BrainCircuit, Info, AlertTriangle, CheckCircle, TrendingDown, TrendingUp } from 'lucide-react';
import api from '../../api/client';

const MenteeRiskHeatmap = () => {
  const [predictions, setPredictions] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      const res = await api.get('/predictions');
      setPredictions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Mentee Academic Risk Heatmap & XAI Explainers</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Explainable AI (SHAP) feature attribution explaining why a student is categorized as At-Risk.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {predictions.length} Monitored
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {predictions.map((p) => (
          <div 
            key={p.student_id} 
            className={`p-5 rounded-2xl border cursor-pointer transition hover:scale-[1.01] bg-white app-card ${
              p.risk_level === 'HIGH' ? 'border-rose-300 shadow-md shadow-rose-500/5' :
              p.risk_level === 'MEDIUM' ? 'border-amber-300 shadow-md shadow-amber-500/5' :
              'border-purple-100/90 shadow-sm'
            }`}
            onClick={() => setSelectedStudent(p)}
          >
            <div className="flex items-center justify-between border-b border-purple-50 pb-3 mb-3">
              <div>
                <h3 className="font-black text-sm text-slate-900 font-heading">{p.student_name}</h3>
                <span className="text-xs text-slate-500 font-medium">Predicted Score: <strong className="text-[#7C3AED] font-heading font-black">{p.predicted_score}%</strong></span>
              </div>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border uppercase tracking-wider ${
                p.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                p.risk_level === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                'bg-emerald-50 text-emerald-700 border-emerald-200'
              }`}>
                {p.risk_level} RISK
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Attendance Rate:</span>
                <span className={`font-mono font-bold text-sm ${p.attendance_pct < 75 ? 'text-rose-600' : 'text-emerald-700'}`}>{p.attendance_pct}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Exam Average:</span>
                <span className="font-mono font-bold text-slate-900 text-sm">{p.exam_avg}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Primary Risk Driver (SHAP):</span>
                <span className="font-bold text-amber-800">{p.shap_top_features?.[0]?.description || 'Normal'}</span>
              </div>
            </div>

            <div className="mt-4 text-[11px] text-[#7C3AED] font-extrabold flex items-center space-x-1">
              <Info className="w-3.5 h-3.5" />
              <span>Click for SHAP Feature Attribution Breakdown →</span>
            </div>
          </div>
        ))}
      </div>

      {/* SHAP EXPLAINABILITY MODAL */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="app-card rounded-3xl p-7 border border-purple-100 max-w-lg w-full space-y-4 max-h-[90vh] overflow-y-auto bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-purple-100 pb-3">
              <div>
                <h3 className="font-black text-lg text-slate-900">SHAP Explainable AI Breakdown</h3>
                <p className="text-xs font-bold text-[#7C3AED]">Student: {selectedStudent.student_name}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-extrabold border ${
                selectedStudent.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
              }`}>{selectedStudent.risk_level} RISK</span>
            </div>

            <div className="space-y-3 text-xs">
              <p className="text-slate-600 leading-relaxed">
                The XGBoost TreeExplainer analyzed {selectedStudent.student_name}'s academic feature set and identified the following top contributing factors:
              </p>

              <div className="space-y-2">
                {selectedStudent.shap_top_features?.map((feat, idx) => (
                  <div key={idx} className="p-3.5 rounded-2xl bg-[#FAF8FE] border border-purple-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{feat.description}</span>
                      <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                        feat.impact === 'NEGATIVE' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}>
                        Impact: {feat.impact}
                      </span>
                    </div>
                    <div className="flex justify-between text-[11px] text-slate-500 font-medium pt-1">
                      <span>Weight: {feat.importance}</span>
                      <span>Recorded Value: {feat.value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-purple-100 flex justify-end">
              <button onClick={() => setSelectedStudent(null)} className="px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MenteeRiskHeatmap;
