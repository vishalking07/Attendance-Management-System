import React, { useState, useEffect } from 'react';
import { Users, Sparkles, Sliders, Brain, Mail, Phone, GraduationCap } from 'lucide-react';
import api from '../../api/client';
import AICounselingDossierModal from '../../components/AICounselingDossierModal';
import WhatIfSimulatorModal from '../../components/WhatIfSimulatorModal';

const MenteeList = () => {
  const [mentees, setMentees] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [isWhatIfOpen, setIsWhatIfOpen] = useState(false);

  useEffect(() => {
    fetchMentees();
  }, []);

  const fetchMentees = async () => {
    try {
      const res = await api.get('/users?role=STUDENT');
      setMentees(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenDossier = (student) => {
    setSelectedStudent(student);
    setIsDossierOpen(true);
  };

  const handleOpenWhatIf = (student) => {
    setSelectedStudent(student);
    setIsWhatIfOpen(true);
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Assigned Student Mentees
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Directory of students under your advisement with AI Intervention Dossiers & What-If tools.
          </p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {mentees.length} Students Assigned
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mentees.map((m) => (
          <div
            key={m.id}
            className="app-card p-4 sm:p-5 rounded-2xl border border-purple-100/90 flex flex-col justify-between bg-white shadow-sm space-y-3"
          >
            <div className="flex items-start space-x-3.5">
              <img
                src={m.profile_photo || `https://api.dicebear.com/7.x/avataaars/svg?seed=${m.name}`}
                className="w-13 h-13 sm:w-14 sm:h-14 rounded-2xl border-2 border-purple-200 p-0.5 bg-purple-50 object-cover flex-shrink-0"
                alt=""
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-black text-sm text-slate-900 font-heading truncate">
                    {m.name}
                  </h3>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100 uppercase font-mono">
                    Active
                  </span>
                </div>
                <p className="text-xs text-slate-500 truncate mt-0.5 flex items-center">
                  <Mail className="w-3 h-3 mr-1 text-slate-400" />
                  {m.email}
                </p>
                <div className="flex items-center space-x-3 mt-1 text-[10px]">
                  <span className="font-mono font-bold text-[#7C3AED]">
                    ID: {m.id}
                  </span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-500 font-medium">B.Tech CS</span>
                </div>
              </div>
            </div>

            {/* Interconnected Action Buttons */}
            <div className="pt-2 border-t border-purple-50 flex items-center justify-end space-x-2">
              <button
                onClick={() => handleOpenWhatIf(m)}
                className="px-3 py-1.5 rounded-xl bg-purple-50 hover:bg-purple-100 text-[#7C3AED] font-bold text-xs flex items-center space-x-1.5 transition-colors font-heading"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>What-If Goal</span>
              </button>

              <button
                onClick={() => handleOpenDossier(m)}
                className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-purple-700 to-[#7C3AED] hover:from-purple-800 hover:to-purple-700 text-white font-bold text-xs flex items-center space-x-1.5 transition-all shadow-sm font-heading"
              >
                <Brain className="w-3.5 h-3.5" />
                <span>✨ AI Dossier</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Module 5: AI Counseling Dossier Modal */}
      <AICounselingDossierModal
        isOpen={isDossierOpen}
        onClose={() => setIsDossierOpen(false)}
        studentId={selectedStudent?.id}
        studentName={selectedStudent?.name}
        userRole="MENTOR"
      />

      {/* Module 1: What-If Goal Simulator Modal */}
      <WhatIfSimulatorModal
        isOpen={isWhatIfOpen}
        onClose={() => setIsWhatIfOpen(false)}
        studentId={selectedStudent?.id}
        studentName={selectedStudent?.name}
      />
    </div>
  );
};

export default MenteeList;
