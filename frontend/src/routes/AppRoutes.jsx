import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';

// Pages
import LoginPage from '../pages/auth/LoginPage';

// Admin
import AdminDashboard from '../pages/admin/AdminDashboard';
import UserManagement from '../pages/admin/UserManagement';
import DepartmentManagement from '../pages/admin/DepartmentManagement';
import GeofenceConfig from '../pages/admin/GeofenceConfig';
import MLModelConfig from '../pages/admin/MLModelConfig';
import AuditLogs from '../pages/admin/AuditLogs';

// HOD
import HODDashboard from '../pages/hod/HODDashboard';
import DepartmentStudents from '../pages/hod/DepartmentStudents';
import DepartmentMentors from '../pages/hod/DepartmentMentors';
import HODApprovals from '../pages/hod/HODApprovals';

// Mentor
import MentorDashboard from '../pages/mentor/MentorDashboard';
import MenteeList from '../pages/mentor/MenteeList';
import MenteeRiskHeatmap from '../pages/mentor/MenteeRiskHeatmap';
import MentorApprovals from '../pages/mentor/MentorApprovals';
import MeetingLog from '../pages/mentor/MeetingLog';

// Student
import StudentDashboard from '../pages/student/StudentDashboard';
import AttendanceCheckin from '../components/AttendanceCheckin';
import AttendanceCalendar from '../pages/student/AttendanceCalendar';
import LeaveRequests from '../pages/student/LeaveRequests';
import CorrectionRequests from '../pages/student/CorrectionRequests';
import PerformanceRiskView from '../pages/student/PerformanceRiskView';

// Layout Wrapper with Fit-To-Screen Container matching reference design
const DashboardLayout = () => {
  return (
    <div className="h-screen w-screen overflow-hidden bg-[#ECE6F8] p-2 sm:p-3 lg:p-4 flex items-center justify-center">
      {/* Central App Card Container with rounded corners, subtle ring & elevation */}
      <div className="w-full h-full max-w-[1680px] bg-white rounded-[2rem] lg:rounded-[2.5rem] shadow-2xl shadow-purple-950/15 p-2.5 sm:p-3.5 lg:p-4 flex flex-col md:flex-row gap-3 sm:gap-4 lg:gap-5 overflow-hidden border border-purple-100/90 ring-1 ring-purple-900/5">
        {/* Left Floating Purple Gradient Sidebar */}
        <Sidebar />

        {/* Main Dashboard Area */}
        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto px-1 sm:px-2 pt-1 pb-4 custom-scrollbar">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

// Protected Route Wrapper enforcing Role Access Control
const ProtectedRoute = ({ allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#ECE6F8] flex items-center justify-center text-purple-800 font-black text-sm font-heading tracking-wide">
        <div className="flex items-center space-x-3 p-4 rounded-2xl bg-white shadow-xl border border-purple-100">
          <span className="w-3 h-3 rounded-full bg-[#7C3AED] animate-ping"></span>
          <span>Authenticating Bio-XAI Portal...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    switch (user.role) {
      case 'ADMIN': return <Navigate to="/admin" replace />;
      case 'HOD': return <Navigate to="/hod" replace />;
      case 'MENTOR': return <Navigate to="/mentor" replace />;
      case 'STUDENT': default: return <Navigate to="/student" replace />;
    }
  }

  return <DashboardLayout />;
};

const AppRoutes = () => {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/" replace />} />

      {/* ADMIN ROUTES */}
      <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<UserManagement />} />
        <Route path="/admin/departments" element={<DepartmentManagement />} />
        <Route path="/admin/geofence" element={<GeofenceConfig />} />
        <Route path="/admin/ml-config" element={<MLModelConfig />} />
        <Route path="/admin/audit-logs" element={<AuditLogs />} />
      </Route>

      {/* HOD ROUTES */}
      <Route element={<ProtectedRoute allowedRoles={['HOD']} />}>
        <Route path="/hod" element={<HODDashboard />} />
        <Route path="/hod/students" element={<DepartmentStudents />} />
        <Route path="/hod/mentors" element={<DepartmentMentors />} />
        <Route path="/hod/approvals" element={<HODApprovals />} />
      </Route>

      {/* MENTOR ROUTES */}
      <Route element={<ProtectedRoute allowedRoles={['MENTOR']} />}>
        <Route path="/mentor" element={<MentorDashboard />} />
        <Route path="/mentor/mentees" element={<MenteeList />} />
        <Route path="/mentor/risk-heatmap" element={<MenteeRiskHeatmap />} />
        <Route path="/mentor/approvals" element={<MentorApprovals />} />
        <Route path="/mentor/meetings" element={<MeetingLog />} />
      </Route>

      {/* STUDENT ROUTES */}
      <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/student/checkin" element={<AttendanceCheckin />} />
        <Route path="/student/calendar" element={<AttendanceCalendar />} />
        <Route path="/student/leaves" element={<LeaveRequests />} />
        <Route path="/student/corrections" element={<CorrectionRequests />} />
        <Route path="/student/performance" element={<PerformanceRiskView />} />
      </Route>

      {/* ROOT FALLBACK ROUTE */}
      <Route
        path="*"
        element={
          user ? (
            user.role === 'ADMIN' ? <Navigate to="/admin" replace /> :
            user.role === 'HOD' ? <Navigate to="/hod" replace /> :
            user.role === 'MENTOR' ? <Navigate to="/mentor" replace /> :
            <Navigate to="/student" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
};

export default AppRoutes;
