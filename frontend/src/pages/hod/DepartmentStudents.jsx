import React, { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import api from '../../api/client';
import { getPersonPhoto } from '../../utils/avatarHelper';

const DepartmentStudents = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const res = await api.get('/users?role=STUDENT');
      setStudents(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 pb-2">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">Department Students Directory</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Students enrolled under the Computer Science & AI Department.</p>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
          {students.length} Enrolled
        </span>
      </div>

      <div className="app-card rounded-2xl overflow-hidden border border-purple-100/90 shadow-sm bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-4">Student</th>
                <th className="p-4">Phone</th>
                <th className="p-4">Assigned Mentor ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
              {students.map((s) => (
                <tr key={s.id} className="hover:bg-purple-50/40 transition">
                  <td className="p-4 flex items-center space-x-3">
                    <img src={s.profile_photo?.includes('dicebear') ? getPersonPhoto(s.name) : (s.profile_photo || getPersonPhoto(s.name))} className="w-8 h-8 rounded-full border border-purple-200 object-cover" alt="" />
                    <div>
                      <span className="font-bold text-slate-900 block font-heading">{s.name}</span>
                      <span className="text-[11px] text-slate-500">{s.email}</span>
                    </div>
                  </td>
                  <td className="p-4 text-slate-600 font-mono">{s.phone || 'N/A'}</td>
                  <td className="p-4 font-mono font-bold text-[#7C3AED]">{s.mentor_id || 'Unassigned'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DepartmentStudents;
