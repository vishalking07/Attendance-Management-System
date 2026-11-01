import React, { useState, useEffect } from 'react';
import { UserCheck } from 'lucide-react';
import api from '../../api/client';
import { getPersonPhoto } from '../../utils/avatarHelper';

const DepartmentMentors = () => {
  const [mentors, setMentors] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [selectedMentor, setSelectedMentor] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [mRes, sRes] = await Promise.all([
        api.get('/users?role=MENTOR'),
        api.get('/users?role=STUDENT')
      ]);
      setMentors(mRes.data);
      setStudents(sRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReassign = async (e) => {
    e.preventDefault();
    if (!selectedStudent || !selectedMentor) return;
    try {
      await api.put(`/users/${selectedStudent}/reassign-mentor?mentor_id=${selectedMentor}`);
      alert("Mentor re-assigned successfully!");
      fetchData();
    } catch (err) {
      alert("Failed to reassign mentor.");
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Faculty Mentors & Load Balance</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">View faculty mentee allocations and reassign advisors as needed.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {mentors.length} Faculty Mentors
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Mentor Cards */}
        <div className="space-y-3">
          <h3 className="font-black text-sm text-slate-900 font-heading uppercase tracking-wider">Department Mentors</h3>
          {mentors.map((m) => {
            const menteeCount = students.filter(s => s.mentor_id === m.id).length;
            return (
              <div key={m.id} className="app-card p-4 rounded-2xl border border-purple-100/90 flex items-center justify-between bg-white shadow-sm hover:border-purple-200 transition">
                <div className="flex items-center space-x-3">
                  <img src={m.profile_photo?.includes('dicebear') ? getPersonPhoto(m.name) : (m.profile_photo || getPersonPhoto(m.name))} className="w-10 h-10 rounded-full border border-purple-200 object-cover" alt="" />
                  <div>
                    <span className="font-bold text-slate-900 text-xs block font-heading">{m.name}</span>
                    <span className="text-[10px] text-slate-500">{m.email}</span>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-black bg-purple-50 text-[#7C3AED] border border-purple-200">
                  {menteeCount} Mentees
                </span>
              </div>
            );
          })}
        </div>

        {/* Re-assign Form */}
        <div className="app-card p-6 rounded-3xl border border-purple-100 space-y-4 text-xs bg-white shadow-sm">
          <h3 className="font-extrabold text-sm text-slate-900">Reassign Mentor to Student</h3>
          <form onSubmit={handleReassign} className="space-y-3.5">
            <div>
              <label className="text-slate-700 font-bold block mb-1">Select Student</label>
              <select
                value={selectedStudent}
                onChange={(e) => setSelectedStudent(e.target.value)}
                className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                <option value="">-- Choose Student --</option>
                {students.map(s => <option key={s.id} value={s.id}>{s.name} (Current Mentor: {s.mentor_id || 'None'})</option>)}
              </select>
            </div>
            <div>
              <label className="text-slate-700 font-bold block mb-1">New Target Mentor</label>
              <select
                value={selectedMentor}
                onChange={(e) => setSelectedMentor(e.target.value)}
                className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                <option value="">-- Choose Mentor --</option>
                {mentors.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-bold shadow-md shadow-purple-600/20 transition"
            >
              Reassign Mentor
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DepartmentMentors;
