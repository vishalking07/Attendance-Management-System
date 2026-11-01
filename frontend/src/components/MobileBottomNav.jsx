import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, CheckSquare, BrainCircuit, Users, Menu,
  ShieldCheck, Calendar, FileText
} from 'lucide-react';

const MobileBottomNav = ({ onOpenMenu }) => {
  const { user } = useAuth();
  const role = user?.role;

  const getBottomItems = () => {
    switch (role) {
      case 'ADMIN':
        return [
          { name: 'Overview', path: '/admin', icon: LayoutDashboard },
          { name: 'Users', path: '/admin/users', icon: Users },
          { name: 'Audit', path: '/admin/audit-logs', icon: ShieldCheck },
        ];
      case 'HOD':
        return [
          { name: 'Home', path: '/hod', icon: LayoutDashboard },
          { name: 'Students', path: '/hod/students', icon: Users },
          { name: 'Approvals', path: '/hod/approvals', icon: CheckSquare },
        ];
      case 'MENTOR':
        return [
          { name: 'Home', path: '/mentor', icon: LayoutDashboard },
          { name: 'Mentees', path: '/mentor/mentees', icon: Users },
          { name: 'Heatmap', path: '/mentor/risk-heatmap', icon: BrainCircuit },
          { name: 'Approvals', path: '/mentor/approvals', icon: CheckSquare },
        ];
      case 'STUDENT':
      default:
        return [
          { name: 'Home', path: '/student', icon: LayoutDashboard },
          { name: 'Check-in', path: '/student/checkin', icon: CheckSquare, highlight: true },
          { name: 'XAI Risk', path: '/student/performance', icon: BrainCircuit },
          { name: 'Schedule', path: '/student/calendar', icon: Calendar },
        ];
    }
  };

  const items = getBottomItems();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-lg border-t border-purple-100 shadow-[0_-8px_20px_rgba(91,33,182,0.08)] px-2 py-1.5 flex items-center justify-around">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/admin' || item.path === '/hod' || item.path === '/mentor' || item.path === '/student'}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center py-1 px-2.5 rounded-2xl transition-all duration-150 ${
                item.highlight
                  ? isActive
                    ? 'bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] text-white shadow-md shadow-purple-900/30 -translate-y-1'
                    : 'bg-purple-50 text-[#7C3AED] border border-purple-200'
                  : isActive
                  ? 'text-[#7C3AED] font-black'
                  : 'text-slate-400 hover:text-slate-700'
              }`
            }
          >
            <Icon className={`w-5 h-5 ${item.highlight ? 'text-inherit' : ''}`} />
            <span className="text-[10px] font-heading font-bold mt-0.5 tracking-tight">
              {item.name}
            </span>
          </NavLink>
        );
      })}

      {/* Menu Drawer Toggle Button */}
      <button
        onClick={onOpenMenu}
        className="flex flex-col items-center justify-center py-1 px-2.5 rounded-2xl text-slate-400 hover:text-purple-700 transition"
      >
        <Menu className="w-5 h-5" />
        <span className="text-[10px] font-heading font-bold mt-0.5 tracking-tight">
          Menu
        </span>
      </button>
    </nav>
  );
};

export default MobileBottomNav;
