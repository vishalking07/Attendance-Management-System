import React, { useState, useEffect } from 'react';
import { Users, Plus, Trash2, Shield, Search } from 'lucide-react';
import api from '../../api/client';
import { getPersonPhoto } from '../../utils/avatarHelper';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '', email: '', phone: '', role: 'STUDENT', department_id: 'dept_cs', password: 'Student@123'
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [uRes, dRes] = await Promise.all([
        api.get('/users'),
        api.get('/departments')
      ]);
      setUsers(uRes.data);
      setDepartments(dRes.data);
    } catch (err) {
      console.error("Failed to load users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await api.post('/users', formData);
      setShowModal(false);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create user.");
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await api.delete(`/users/${userId}`);
      fetchData();
    } catch (err) {
      alert("Failed to delete user.");
    }
  };

  const filteredUsers = users.filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(searchTerm.toLowerCase()) || u.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter ? u.role === roleFilter : true;
    return matchesSearch && matchesRole;
  });

  return (
    <div className="space-y-5 pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 font-heading tracking-tight">User Management</h2>
          <p className="text-xs text-slate-500 font-medium mt-0.5">Manage all student, mentor, HOD, and administrative user profiles.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-bold shadow-md shadow-purple-600/20 flex items-center space-x-2 w-fit transition font-heading"
        >
          <Plus className="w-4 h-4" />
          <span>Add New User</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-white border border-purple-100 rounded-xl py-2 pl-10 pr-4 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400 shadow-sm"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="bg-white border border-purple-100 rounded-xl px-3.5 py-2 text-xs text-slate-700 font-bold focus:outline-none focus:ring-2 focus:ring-purple-400 shadow-sm font-heading"
        >
          <option value="">All Roles</option>
          <option value="ADMIN">ADMIN</option>
          <option value="HOD">HOD</option>
          <option value="MENTOR">MENTOR</option>
          <option value="STUDENT">STUDENT</option>
        </select>
      </div>

      {/* User Table */}
      <div className="app-card rounded-2xl overflow-hidden border border-purple-100/90 shadow-sm bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-[#FAF8FE] text-purple-900 font-bold border-b border-purple-100">
              <tr>
                <th className="p-4">User</th>
                <th className="p-4">Role</th>
                <th className="p-4">Department</th>
                <th className="p-4">Mentor ID</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
            {filteredUsers.map((u) => (
              <tr key={u.id} className="hover:bg-purple-50/40 transition">
                <td className="p-4 flex items-center space-x-3">
                  <img src={u.profile_photo?.includes('dicebear') ? getPersonPhoto(u.name) : (u.profile_photo || getPersonPhoto(u.name))} className="w-8 h-8 rounded-full border border-purple-200 object-cover" alt="" />
                  <div>
                    <span className="font-bold text-slate-900 block">{u.name}</span>
                    <span className="text-[11px] text-slate-500">{u.email}</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-extrabold border bg-purple-50 text-[#7C3AED] border-purple-200">
                    {u.role}
                  </span>
                </td>
                <td className="p-4 font-mono text-slate-600 font-medium">{u.department_id || 'N/A'}</td>
                <td className="p-4 font-mono text-[#7C3AED] font-medium">{u.mentor_id || 'Unassigned'}</td>
                <td className="p-4 text-right">
                  <button onClick={() => handleDeleteUser(u.id)} className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>

      {/* CREATE MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="app-card rounded-3xl p-6 border border-purple-100 max-w-md w-full space-y-4 bg-white shadow-2xl">
            <h3 className="font-black text-base text-slate-900">Create New User Account</h3>
            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-bold block mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>
              <div>
                <label className="text-slate-700 font-bold block mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-700 font-bold block mb-1">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  >
                    <option value="STUDENT">STUDENT</option>
                    <option value="MENTOR">MENTOR</option>
                    <option value="HOD">HOD</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-700 font-bold block mb-1">Department</label>
                  <select
                    value={formData.department_id}
                    onChange={(e) => setFormData({...formData, department_id: e.target.value})}
                    className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  >
                    {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-bold block mb-1">Initial Password</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-[#FAF8FE] border border-purple-100 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-purple-100">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 font-semibold hover:bg-slate-200">Cancel</button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-[#7C3AED] text-white font-bold hover:bg-[#6D28D9] shadow-sm">Create User</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
