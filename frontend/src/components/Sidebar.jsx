import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, Users, Building, MapPin, Cpu, ShieldAlert,
  CheckSquare, Calendar, FileText, BrainCircuit, UserCheck, MessageSquare,
  GraduationCap, LogOut, X
} from 'lucide-react';

const Sidebar = ({ isMobileOpen = false, onClose = () => {} }) => {
  const { user, logout } = useAuth();
  const role = user?.role;

  const getNavItems = () => {
    switch (role) {
      case 'ADMIN':
        return [
          { name: 'Dashboard', path: '/admin', icon: LayoutDashboard },
          { name: 'Users', path: '/admin/users', icon: Users },
          { name: 'Departments', path: '/admin/departments', icon: Building },
          { name: 'Geofences', path: '/admin/geofence', icon: MapPin },
          { name: 'ML Engine', path: '/admin/ml-config', icon: Cpu },
          { name: 'Audit Trail', path: '/admin/audit-logs', icon: ShieldAlert },
        ];

      case 'HOD':
        return [
          { name: 'Dashboard', path: '/hod', icon: LayoutDashboard },
          { name: 'Students', path: '/hod/students', icon: Users },
          { name: 'Mentors', path: '/hod/mentors', icon: UserCheck },
          { name: 'Approvals', path: '/hod/approvals', icon: CheckSquare },
        ];

      case 'MENTOR':
        return [
          { name: 'Dashboard', path: '/mentor', icon: LayoutDashboard },
          { name: 'Mentees', path: '/mentor/mentees', icon: Users },
          { name: 'Risk Heatmap', path: '/mentor/risk-heatmap', icon: BrainCircuit },
          { name: 'Approvals', path: '/mentor/approvals', icon: CheckSquare },
          { name: 'Counseling', path: '/mentor/meetings', icon: MessageSquare },
        ];

      case 'STUDENT':
      default:
        return [
          { name: 'Dashboard', path: '/student', icon: LayoutDashboard },
          { name: 'Attendance', path: '/student/checkin', icon: CheckSquare },
          { name: 'Schedule', path: '/student/calendar', icon: Calendar },
          { name: 'Leaves', path: '/student/leaves', icon: FileText },
          { name: 'Correction', path: '/student/corrections', icon: CheckSquare },
          { name: 'Risk Analytics', path: '/student/performance', icon: BrainCircuit },
        ];
    }
  };

  const navItems = getNavItems();

  const renderSidebarContent = (isMobile = false) => (
    <div className="flex flex-col h-full min-h-0">
      {/* App Emblem Tile */}
      <div className="flex flex-col items-center pt-1 pb-4 border-b border-white/10 flex-shrink-0 relative">
        {isMobile && (
          <button
            onClick={onClose}
            className="absolute top-1 right-1 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white"
            title="Close menu"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center shadow-lg border border-white/25 text-white relative">
          <GraduationCap className="w-7 h-7 sm:w-8 sm:h-8 text-white drop-shadow-sm" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 border-2 border-purple-800 rounded-full animate-pulse" title="System Live"></span>
        </div>
        <span className="mt-2 text-xs sm:text-[13px] font-extrabold tracking-wider text-white uppercase text-center font-heading">
          Bio-XAI Portal
        </span>
        <span className="text-[10px] text-purple-200/90 font-medium tracking-wide">
          Smart Attendance AI
        </span>
      </div>

      {/* Navigation Items */}
      <nav className="space-y-1.5 py-4 flex-1 overflow-y-auto no-scrollbar">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => { if (isMobile) onClose(); }}
              end={item.path === '/admin' || item.path === '/hod' || item.path === '/mentor' || item.path === '/student'}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-tight transition-all duration-200 ${
                  isActive
                    ? 'bg-white text-[#6D28D9] font-black shadow-md shadow-purple-950/25 translate-x-1'
                    : 'text-purple-100/80 hover:text-white hover:bg-white/10'
                }`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Section: Active Role & Logout */}
      <div className="pt-3 border-t border-white/15 flex-shrink-0 space-y-2">
        <div className="px-3 py-1.5 rounded-xl bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-between">
          <span className="text-[10px] text-purple-200 uppercase font-bold tracking-wider">Role</span>
          <span className="text-[10px] font-black px-2 py-0.5 rounded-md bg-white/20 text-white border border-white/20 uppercase">
            {role || 'STUDENT'}
          </span>
        </div>

        <button
          onClick={() => {
            if (isMobile) onClose();
            logout();
          }}
          className="w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-purple-200 hover:text-white hover:bg-white/15 transition-all"
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* 1. Desktop Fixed Sidebar */}
      <aside className="hidden md:flex w-56 lg:w-60 h-full rounded-[1.75rem] lg:rounded-[2rem] bg-gradient-to-b from-[#8B5CF6] via-[#7C3AED] to-[#5B21B6] text-white p-4 lg:p-5 flex-col justify-between shadow-xl shadow-purple-900/25 flex-shrink-0 overflow-hidden">
        {renderSidebarContent(false)}
      </aside>

      {/* 2. Mobile Drawer & Backdrop */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Backdrop Blur */}
          <div
            onClick={onClose}
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity animate-fade-in"
          />

          {/* Drawer Body */}
          <div className="relative w-72 max-w-[85vw] h-full bg-gradient-to-b from-[#8B5CF6] via-[#7C3AED] to-[#5B21B6] text-white p-5 flex flex-col justify-between shadow-2xl z-10 animate-slide-right">
            {renderSidebarContent(true)}
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
