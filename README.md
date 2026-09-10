# Bio-XAI: Smart Attendance & Student Performance Prediction System

A full-stack enterprise web application featuring Biometric Face Verification, Strict Polygon Campus Geofencing, Adaptive 2FA OTP, XGBoost & SHAP Explainable AI for Student Risk Prediction, and strict Role-Based Access Control (RBAC).

---

## ⚡ Current Status
Both servers are **already running** in the background:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

## 🚀 How to Run the Project (Step-by-Step)

If you need to start the servers manually in the future, open two separate terminal windows (PowerShell or Command Prompt):

### Terminal 1: Backend (FastAPI + Python)

```powershell
# 1. Navigate to the backend directory
cd "Attendance Management System\backend"

# 2. Activate the virtual environment
.\venv\Scripts\activate

# 3. Start the FastAPI development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend will start on `http://localhost:8000`. On startup, it automatically seeds sample users, polygon geofence zones, trains the XGBoost risk model, and schedules the daily 09:30 AM auto-absence cron job.*

---

### Terminal 2: Frontend (Vite + React)

```powershell
# 1. Navigate to the frontend directory
cd "Attendance Management System\frontend"

# 2. (Optional, if not already installed) Install dependencies
npm install

# 3. Start the Vite React development server
npm run dev
```
*Frontend will start on `http://localhost:3000` with instant hot-reloading.*

---

## 🔑 Default Login Credentials

You can use the **1-Click Quick-Fill buttons** directly on the Login screen (`http://localhost:3000/login`) or use the credentials below:

| Role | Email | Password | What You Can Test |
| :--- | :--- | :--- | :--- |
| **👑 ADMIN** | `admin@bioxai.edu` | `Admin@123` | System analytics charts, User CRUD, Building polygon geofences, ML threshold tuning & retraining trigger, immutable audit trail. |
| **🎓 HOD (CS)** | `hod.cs@bioxai.edu` | `Hod@123` | Scoped to Computer Science department, mentor load rebalancing, student directory, escalated approvals. |
| **👨‍🏫 MENTOR** | `mentor1.cs@bioxai.edu` | `Mentor@123` | Assigned mentees list, SHAP risk heatmap ("Why this student is at risk"), counseling meeting logs, approve/reject correction requests. |
| **👨‍🎓 STUDENT** | `sarah.jenkins@student.bioxai.edu` | `Student@123` | Multi-step Biometric Check-in (GPS + Webcam + Adaptive 2FA OTP), attendance shortage warning (<75%), leave applications, correction requests. |
| **👨‍🎓 STUDENT 2** | `alex.smith@student.bioxai.edu` | `Student@123` | High-attendance student (92%) with Low Risk classification. |

---

## 🌟 Key Architecture & Workflows

### 1. Smart 3-Factor Attendance Flow
1. **Factor 1: Polygon Geofence Location Check**: Device coordinates (Geolocation API) are verified against the building's multi-point polygon boundary before anything else. Outside coordinates are rejected with an audit log.
2. **Factor 2: Face Biometric & Liveness**: Live webcam frame captures the student's face, checks for liveness, extracts a 128-dimensional embedding vector, and matches against stored templates using Cosine Similarity.
3. **Factor 3: Adaptive 2FA OTP**:
   - **High Confidence (>85%)**: Auto-completes and marks `PRESENT` directly.
   - **Borderline Confidence (60–85%)**: Issues a single-use 6-digit OTP (120s validity) displayed in the in-app notification & console preview for demo testing.

### 2. Machine Learning Student Risk Prediction (XGBoost + SHAP)
- Evaluates 5 key academic features: Overall Attendance %, Exam Average, Assignment Completion %, Leave Frequency, and Correction Frequency.
- Classifies students into **LOW**, **MEDIUM**, or **HIGH** risk.
- Computes **SHAP (Shapley Additive exPlanations)** values to surface the exact reasons why a student is at risk to their mentor and HOD.

### 3. Automated Daily Absence Cutoff
- APScheduler runs every morning at the configured cutoff time (09:30 AM).
- Enrolled students with no attendance record for the day are automatically marked `ABSENT` and immediately notified with a direct link to submit a correction request if disputed.
