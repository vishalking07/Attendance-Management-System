import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Search, Bell, Menu } from 'lucide-react';
import api from '../api/client';
import { getPersonPhoto } from '../utils/avatarHelper';

const Navbar = ({ onToggleMobileMenu = () => {} }) => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifs();
    }
  }, [user]);

  const fetchNotifs = async () => {
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error("Failed to load notifications:", err);
    }
  };

  const getSubtext = () => {
    if (user?.role === 'STUDENT') return '3rd year';
    if (user?.role === 'MENTOR') return 'Faculty Advisor';
    if (user?.role === 'HOD') return 'HOD (CS)';
    return 'System Admin';
  };

  const todayStr = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  return (
    <header className="h-14 px-1 sm:px-2 flex items-center justify-between z-30 flex-shrink-0 border-b border-purple-50 pb-2 mb-2 gap-2">
      {/* Left Area: Mobile Hamburger Button + Pill Search Input */}
      <div className="flex items-center space-x-2 flex-1 sm:flex-initial">
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden w-9 h-9 rounded-full bg-[#FAF8FE] border border-purple-100 flex items-center justify-center text-purple-700 hover:bg-purple-100/60 transition shadow-sm flex-shrink-0"
          title="Open Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative w-full max-w-[200px] sm:max-w-none sm:w-72 md:w-80">
          <input
            type="text"
            placeholder="Search courses, logs..."
            className="w-full bg-[#FAF8FE] border border-purple-100 rounded-full py-1.5 sm:py-2 pl-8 sm:pl-9 pr-8 sm:pr-14 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:bg-white shadow-sm transition-all"
          />
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2 sm:top-2.5" />
          <div className="absolute right-2.5 top-2 px-1.5 py-0.5 rounded-md bg-purple-100/70 text-[9px] font-mono text-purple-700 font-bold border border-purple-200/60 hidden sm:block">
            Ctrl K
          </div>
        </div>
      </div>

      {/* Middle Status Pill (Hidden on mobile) */}
      <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-[#FAF8FE] border border-purple-100/90 text-[11px] text-slate-600 shadow-sm">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span className="font-semibold text-slate-700">Campus Geofence:</span>
        <span className="font-bold text-purple-700">Active (500m)</span>
        <span className="text-slate-300">|</span>
        <span className="text-slate-500 font-medium">{todayStr}</span>
      </div>

      {/* Right Actions: User Profile Pill & Notification Bell */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="w-9 h-9 rounded-full bg-[#FAF8FE] border border-purple-100 flex items-center justify-center text-slate-600 hover:text-purple-700 hover:border-purple-300 transition-all shadow-sm relative focus:outline-none"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            {notifications.filter(n => !n.read).length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full ring-2 ring-white animate-ping"></span>
            )}
            {notifications.filter(n => !n.read).length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full ring-2 ring-white"></span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-white rounded-3xl shadow-2xl p-4 z-50 border border-purple-100 max-h-96 overflow-y-auto custom-scrollbar">
              <div className="flex items-center justify-between border-b border-purple-50 pb-2 mb-3">
                <h3 className="font-bold text-xs text-slate-900 font-heading">Notifications</h3>
                <span className="text-[10px] text-purple-700 font-extrabold px-2 py-0.5 rounded-full bg-purple-50 border border-purple-100">
                  {notifications.length} Total
                </span>
              </div>
              {notifications.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-4">No notifications yet</p>
              ) : (
                <div className="space-y-2">
                  {notifications.map((n) => (
                    <div key={n.id} className="p-3 rounded-2xl bg-[#FAF8FE] border border-purple-100 text-xs space-y-1 hover:border-purple-200 transition">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-purple-900">{n.title}</span>
                        <span className="text-[10px] text-slate-400">{new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                      </div>
                      <p className="text-slate-600 text-[11px] leading-relaxed">{n.message}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* User Profile Pill matching reference design top-right */}
        <div className="flex items-center space-x-2.5 pl-1.5 pr-3 py-1 rounded-full bg-[#FAF8FE] border border-purple-100 shadow-sm">
          <div className="w-8 h-8 rounded-full ring-2 ring-purple-400 p-0.5 overflow-hidden flex-shrink-0 bg-purple-100 shadow-sm">
            <img
              src={user?.profile_photo?.includes('dicebear') ? getPersonPhoto(user?.name) : (user?.profile_photo || getPersonPhoto(user?.name))}
              alt="Profile"
              className="w-full h-full rounded-full object-cover"
            />
          </div>
          <div className="text-left hidden sm:block leading-tight">
            <h4 className="text-xs font-black text-slate-900 font-heading">{user?.name}</h4>
            <p className="text-[10px] text-purple-700 font-bold uppercase tracking-wider">{getSubtext()}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
