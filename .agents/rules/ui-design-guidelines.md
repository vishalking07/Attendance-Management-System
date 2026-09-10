# UI Design System & Hierarchy Preservation Rule

This rule strictly enforces the visual identity, typography, layout hierarchy, and theme across all current and future features, pages, components, and enhancements in this project.

## 1. Absolute Rule: Fit-to-Screen Viewport Architecture
- **Zero Window Scrollbar**: The application container MUST ALWAYS fit 100% of the browser viewport:
  - Root: `h-screen w-screen overflow-hidden bg-[#ECE6F8]`
  - Shell Container: `w-full h-full max-w-[1680px] bg-white rounded-[2rem] lg:rounded-[2.5rem] shadow-2xl shadow-purple-950/15 p-2.5 sm:p-3.5 lg:p-4 flex flex-col md:flex-row gap-3 sm:gap-4 lg:gap-5 overflow-hidden border border-purple-100/90 ring-1 ring-purple-900/5`
  - Sidebar: `h-full flex-shrink-0 overflow-hidden`
  - Main Area: `flex-1 flex flex-col min-w-0 h-full overflow-hidden`
  - Content Scroll: `<main className="flex-1 overflow-y-auto px-1 sm:px-2 pt-1 pb-4 custom-scrollbar">`
- **Never allow window-level double scrollbars**. Only the inner `<main>` container or modal content may scroll.

---

## 2. Typography Rules
- **Headings (`font-heading`)**:
  - Font: `Outfit`, `'Plus Jakarta Sans'`, sans-serif
  - Color: `#0F172A` (deep dark slate for maximum contrast)
  - Letter-spacing: `-0.025em` (tight, crisp, modern)
  - Weights: `font-black` (800 / 900) for titles and KPI numbers, `font-bold` for card headers
- **Body Text (`font-sans`)**:
  - Font: `'Plus Jakarta Sans'`, system-ui, sans-serif
  - Color: `#334155` (slate-700) for readable copy, `#64748B` (slate-500) for subtitles
- **Metrics, Codes & Timestamps (`font-mono`)**:
  - Font: `'JetBrains Mono'`, monospace
  - Usage: Percentages, model scores, coordinates, dates, IDs, phone numbers

---

## 3. Colors & Card Design Tokens
- **Canvas Background**: `#ECE6F8` (soft warm ambient lavender)
- **Standard Card**:
  - Class: `.app-card` (or alias `.soft-card`)
  - Background: Pure crisp `#FFFFFF`
  - Border radius: `1.25rem` (`rounded-2xl`)
  - Border: `1px solid rgba(235, 229, 247, 0.9)`
  - Shadow: Soft violet ambient shadow with smooth hover elevation
- **Active Focal Card**:
  - Class: `.app-card-active` (or alias `.card-highlight`)
  - Border: `2px solid #7C3AED` with `0 0 0 3px rgba(124, 58, 237, 0.08)`
  - Shadow: Glowing violet shadow `0 10px 25px -4px rgba(124, 58, 237, 0.18)`
- **Brand Palette**:
  - Primary: `#7C3AED` (vibrant violet)
  - Gradients: `from-[#8B5CF6] via-[#7C3AED] to-[#5B21B6]`
  - Accents: Emerald (`#10B981`) for verified/safe, Rose (`#F43F5E`) for high risk/critical, Amber (`#F59E0B`) for warnings

---

## 4. Visual Hierarchy Rules
1. **Primary Anchor**: Top header / Hero banner with clean summary badge, greeting, and primary action button.
2. **Secondary Anchor**: 3–4 KPI Metric Cards across the top. The central or most critical metric MUST use `.app-card-active` with elevated text and badge.
3. **Tertiary Anchor**: Main data tables or charts wrapped in `.app-card`, using `#FAF8FE` table headers, monospace stats, and pill badges (`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase`).
4. **Quaternary**: Side informational panels (notices, directory, audit feeds) with compact line-heights and subtle purple links.

DO NOT alter these typography rules, color tokens, or viewport fit layout in any upcoming features or refactors.
