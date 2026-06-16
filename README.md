# Expense Tracker

A modern and professional FastAPI expense tracker utilizing Supabase (PostgreSQL) storage, dynamic currency preferences, customizable budgets, interactive animations, and a React-based interactive landing page background.

## Key Features

- **Personalized Control Center**: Dynamic welcome greetings and settings-based currency switching (NGN/USD).
- **Budget Threshold Alerts**: Real-time spending threshold analysis and visual alerts.
- **Income Tracking**: Comprehensive management of income streams, recurring income automation, and net balance calculation.
- **AI Insights & Category Snapshots**: Category-based percentage tracking, top focus area analysis, and reports.
- **Reporting & Data Export**: Export reports in **CSV**, **Excel**, and **PDF** formats with dynamic filtering.
- **Automated Recurring Transactions**: Daily, weekly, monthly, and yearly recurring expense/income automation with optimized processing.
- **Advanced Security**: 
    - **Advanced Image Validation**: Uses Pillow to verify the integrity and format of uploaded receipt images.
    - **Global Rate Limiting**: Built-in protection against brute-force and spam via SlowAPI.
    - **Stateless Authentication**: HMAC-signed session cookies for secure, tamper-proof user sessions.
    - **CSRF Protection**: Comprehensive protection for all form-based state changes.
    - **Password Security**: Direct `bcrypt` hashing with enforced 72-byte truncation to prevent algorithmic vulnerabilities.
- **WebGL Landing Page**: Interactive particle galaxy background effect using customized fragment shaders.

## Stack & Libraries Used

### Backend (Python)
- **FastAPI**: Modern, fast (high-performance) web framework.
- **Uvicorn**: Lightning-fast ASGI server implementation.
- **Supabase (PostgreSQL)**: Scalable, cloud-hosted relational database.
- **Jinja2**: Templating engine for dynamic HTML rendering.
- **SlowAPI**: Rate limiting middleware for FastAPI.
- **Pillow**: Advanced image processing for receipt validation.
- **bcrypt**: Secure password hashing used directly for optimal performance and compatibility.
- **ReportLab**: PDF generation for financial reports.
- **Pandas & Openpyxl**: Data manipulation and Excel export functionality.
- **python-dateutil**: Advanced date calculations for recurring transactions.

### Frontend (JavaScript / CSS / React)
- **React**: Declarative component-based UI library.
- **OGL**: Minimal WebGL library used to render the interactive particle galaxy canvas.
- **Vite**: High-performance frontend toolchain/bundler.
- **Vanilla CSS**: Custom styling with CSS variables, transitions, and responsive grid layouts.

## Database Schematic

The application utilizes a PostgreSQL database managed via Supabase.

| Table | Description |
| :--- | :--- |
| `users` | Stores user credentials and profile information. |
| `categories` | Stores budget categories associated with a user. |
| `expenses` | Stores individual expense records. |
| `income` | Stores individual income records. |
| `recurring_expenses` | Stores configuration for recurring expenses and next occurrence. |
| `recurring_income` | Stores configuration for recurring income and next occurrence. |
| `settings` | User-specific application settings (e.g., currency, budget limits). |

## Recent Updates

### v2.3.0 — Full Codebase Audit & UI Polish
- **Full Codebase Security & Correctness Audit**: Fixed search bug (case-insensitive matching), added missing CSRF protection on login/register/settings endpoints, patched open redirect vulnerability on `next_url`, fixed auth race condition on concurrent requests, fixed logout button not clearing session properly, added guards for empty `chart_data`, fixed missing `next_url` passthrough on auth redirects, fixed export URL encoding for special characters, updated service worker to handle dynamic routes, fixed Chart.js resize observer conflict, fixed sidebar overlay z-index on mobile, fixed exitIntent mouseout event leak, removed unused EUR/GBP symbols from dropdown, fixed expense category datalist filtering, fixed light mode mock card visibility, added `created_at` to recurring tables.
- **Comprehensive UI Polish**: Refined dark/light theme colors, gradients, sidebar appearance, input fields, cards, buttons, and tables. Improved login/register two-column layout. Fixed hamburger menu dark mode toggle on mobile.
- **Hamburger Menu & Light Mode**: Replaced fixed sidebar collapse with hamburger toggle; implemented full light mode theme with CSS custom properties, localStorage persistence, and toggle button in sidebar. Added form persistence for expense/income inputs on navigation. Removed WebGL galaxy from app pages (kept on landing page only) for performance.
- **Mobile Navigation Evolution**:
  - `b9c3e22`: Introduced swipeable mobile nav with CSS scroll-snap and auto-center active item
  - `e343c66`: Increased nav height from 52px → 64px
  - `d29f511`: Redesigned from floating pill to professional edge-to-edge bottom tab bar
  - `7e795a2`: Restored horizontal swipe scroll, increased height to 72px for polished look

### Account Registration Bug Fixes
- **Security Definer Fix** (`0ae7326`): Changed `handle_new_user()` DB trigger from `SECURITY INVOKER` to `SECURITY DEFINER` to fix permission denied errors on user creation.
- **Duplicate Username Handling** (`f80b635`): Fixed edge case where email prefixes collided on the `username` UNIQUE constraint — trigger now appends MD5 hash suffix on collision. Also cleaned up orphaned `public.users` rows. Updated auth error messages to show actual Supabase error instead of generic text.
- **Removed Redundant Insert** (`e3f2b58`): Backend `auth.py` no longer manually inserts into `public.users` — handled entirely by the DB trigger.

### Authentication & Session
- **Auth Token Expiration Fix** (`53d4427`): Expired Supabase JWT tokens were caught by generic `except Exception` blocks and converted to 500 errors. Fixed by raising `AuthError` instead, with a global handler that redirects to `/login` (303).
- **CSRF Protection**: Added CSRF token validation (double-submit cookie pattern) to all POST endpoints. `secure` flag is environment-aware (enabled in production).
- **Two-Step Logout** (`e309d52`): First sidebar click navigates to dashboard, second click confirms logout — prevents accidental logouts.
- **Cookie & Session Security**: HMAC-signed session cookies for tamper-proof auth. Rate limiter is proxy-aware via `X-Forwarded-For`/`X-Real-IP` headers.

### Database Schema Tightening (`0a158d5`)
- **Numeric Precision**: Changed all financial columns from `double precision` to `numeric(12,2)` to prevent floating-point rounding errors.
- **Indexes**: Added indexes on all `user_id` foreign key columns for query performance.
- **RLS Optimization**: Rewritten with `(select auth.uid())` to avoid per-row function re-evaluation.
- **Trigger Hardening**: Revoked public `EXECUTE` on `handle_new_user()` trigger function.
- **Timestamps**: Added `updated_at` columns with triggers to all tables.
- **Cleanup**: Removed orphaned `food` column from schema.

### Backend Security Hardening
- **Input Validation**: Added length limits and validation to all POST endpoints. Frontend maxlength enforced (72 chars on password fields).
- **Open Redirect Prevention**: `validate_redirect_url()` validates `next_url` against a whitelist of allowed paths.
- **Receipt Upload**: Added 10MB file size limit; image validation via Pillow.verify().
- **Account Deletion**: `delete_account` now also removes the auth user from Supabase Auth, not just local data.
- **Error Handling**: Added `try/except` with `(AuthError, HTTPException): raise` to all endpoint handlers. `get_settings()` and `render_page()` have fallback error handling.
- **Global Rate Limiting**: SlowAPI rate limiter (5–10 req/min per endpoint) with proxy-aware IP detection.

### UI Improvements
- **Back Button Removal** (`763afb7`): Removed back buttons from all 7 templates and associated CSS — no longer needed after auth redirect fix.
- **Light Mode Theme**: Full light theme with CSS custom properties, toggle persists in localStorage, smooth transitions.
- **Form Persistence**: Expense and income input values persist across page navigations.
- **Landing Page Fixes**: Fixed favicon reference (`svg` → `png`), updated `theme-color` meta tag, cache-busting query param `v2.3.0`.

### Architecture
- **Environment Configuration**: Added `.env` file management, `python-dotenv` integration, and updated configuration to load secrets securely.
- **Production Readiness**: Hardened `.gitignore` to exclude sensitive environment files, local database artifacts, and OS/IDE clutter.
- **Income Feature Integration**: Added `income` and `recurring_income` management, integrated into dashboard summary and financial reporting.
- **Database Optimization**: Optimized recurring transaction logic in `app/crud/recurring.py` to run once per day per user, reducing database overhead.

## Run Locally

### 1. Backend Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the application:
   ```bash
   python run.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:8000`

### 2. Frontend Assets Compilation (Vite)
If you make changes to the interactive WebGL landing page assets under `frontend/`:
1. Install node dependencies:
   ```bash
   npm install
   ```
2. Compile/rebuild production bundles:
   ```bash
   npm run build:landing
   ```
