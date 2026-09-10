# Antigravity Workspace Guidelines & Design System Contract

## Core Directives for Attendance Management System

### 1. UI Theme, Typography & Hierarchy Lock (MANDATORY)
The user has established a strict design system that **must NEVER be changed** in any upcoming features, pages, components, or enhancements:

- **Fit-to-Screen Viewport Architecture**:
  - Always keep the application container fitted to 100% of the viewport height and width (`h-screen w-screen overflow-hidden bg-[#ECE6F8]`).
  - Never allow outer browser window scrollbars or double scrollbars.
  - Only the inner `<main className="flex-1 overflow-y-auto ... custom-scrollbar">` or modal dialogs may scroll.
- **Typography**:
  - Headings (`font-heading`): `Outfit`, `-0.025em` tracking, color `#0F172A`, weights `font-black` (800/900).
  - Body (`font-sans`): `Plus Jakarta Sans`, color `#334155`.
  - Numbers / Telemetry (`font-mono`): `JetBrains Mono`.
- **Card Tokens**:
  - Standard cards: `.app-card` / `.soft-card` (`#FFFFFF`, `rounded-2xl`, border `rgba(235, 229, 247, 0.9)`, subtle hover lift).
  - Highlight cards: `.app-card-active` / `.card-highlight` (`#FFFFFF`, border `2px solid #7C3AED`, purple glow ring).
- **Brand Palette**:
  - Primary violet `#7C3AED`, deep purple `#5B21B6`, gradient `from-[#8B5CF6] via-[#7C3AED] to-[#5B21B6]`.

### 2. Stack & Runtime Conventions
- **Frontend**: React + Vite on port 3000 (`cd frontend; npm run dev`)
- **Backend**: FastAPI + Uvicorn on port 8000 (`cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000`)
- **Database**: MongoDB on `mongodb://localhost:27017`
