import React, { useState } from 'react';
import { MessageSquare, Plus, Calendar, Sparkles, Brain } from 'lucide-react';
import AICounselingDossierModal from '../../components/AICounselingDossierModal';

const MeetingLog = () => {
  const [meetings, setMeetings] = useState([
    { id: 'm1', student: 'Sarah Jenkins', date: '2026-09-07', notes: 'Discussed low attendance in morning sessions. Advised on study timetable.', outcome: 'Agreed on weekly progress check' }
  ]);

  const [form, setForm] = useState({ student: 'Sarah Jenkins', notes: '', outcome: '' });
  const [isDossierOpen, setIsDossierOpen] = useState(false);

  const handleAddMeeting = (e) => {
    e.preventDefault();
    setMeetings([{
      id: `m_${meetings.length + 1}`,
      student: form.student,
      date: new Date().toISOString().split('T')[0],
      notes: form.notes,
      outcome: form.outcome
    }, ...meetings]);
    setForm({ student: 'Sarah Jenkins', notes: '', outcome: '' });
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">
            Mentor-Mentee Counseling Log & Action Plans
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Record advising sessions, track recovery milestones, and generate AI counseling dossiers.
          </p>
        </div>

        {/* Module 5: AI Dossier Generator Launcher */}
        <button
          onClick={() => setIsDossierOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-purple-700 to-[#7C3AED] hover:from-purple-800 hover:to-purple-700 text-white font-black text-xs shadow-md shadow-purple-900/20 transition-all font-heading self-start sm:self-auto"
        >
          <Brain className="w-4 h-4" />
          <span>✨ Generate AI Dossier</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Form */}
        <div className="app-card p-5 sm:p-6 rounded-2xl border border-purple-100/90 space-y-3.5 text-xs bg-white shadow-sm">
          <h3 className="font-black text-sm text-slate-900 font-heading uppercase tracking-wider">
            Log Advising Session
          </h3>
          <form onSubmit={handleAddMeeting} className="space-y-3.5">
            <div>
              <label className="text-slate-700 font-bold block mb-1">Select Mentee</label>
              <select
                value={form.student}
                onChange={(e) => setForm({...form, student: e.target.value})}
                className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                <option value="Sarah Jenkins">Sarah Jenkins (At-Risk)</option>
                <option value="Marcus Vance">Marcus Vance (Debarment Warning)</option>
                <option value="Alex Smith">Alex Smith (Honor Roll)</option>
                <option value="David Kumar">David Kumar (Standard)</option>
              </select>
            </div>
            <div>
              <label className="text-slate-700 font-bold block mb-1">Session Notes & Observations</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({...form, notes: e.target.value})}
                required
                className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400 h-20"
                placeholder="Discussed low attendance root causes, sleep schedule, transportation constraints..."
              />
            </div>
            <div>
              <label className="text-slate-700 font-bold block mb-1">Agreed Action Item / Target</label>
              <input
                type="text"
                value={form.outcome}
                onChange={(e) => setForm({...form, outcome: e.target.value})}
                required
                className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                placeholder="Biometric target: 80% over next 14 days, clear 5 lectures"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-bold shadow-md shadow-purple-600/20 transition font-heading"
            >
              Save Advising Record
            </button>
          </form>
        </div>

        {/* List */}
        <div className="space-y-3">
          <h3 className="font-black text-sm text-slate-900 font-heading uppercase tracking-wider">
            Recorded Advising History
          </h3>
          {meetings.map((m) => (
            <div key={m.id} className="app-card p-4 sm:p-5 rounded-2xl border border-purple-100/90 text-xs space-y-1.5 bg-white shadow-sm hover:border-purple-200 transition">
              <div className="flex justify-between font-black text-slate-900 font-heading">
                <span>{m.student}</span>
                <span className="text-[#7C3AED] font-mono">{m.date}</span>
              </div>
              <p className="text-slate-600 leading-relaxed font-medium">{m.notes}</p>
              <span className="text-[11px] font-extrabold text-emerald-700 block pt-1">Outcome: {m.outcome}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Module 5: AI Counseling Dossier Modal */}
      <AICounselingDossierModal
        isOpen={isDossierOpen}
        onClose={() => setIsDossierOpen(false)}
        studentId="usr_student_2"
        studentName={form.student}
        userRole="MENTOR"
      />
    </div>
  );
};

export default MeetingLog;
