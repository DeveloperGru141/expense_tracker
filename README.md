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

- **Environment Configuration**: Added `.env` file management, `python-dotenv` integration, and updated configuration to load secrets securely.
- **Mobile Navigation Redesign**: Implemented a floating pill-style bottom navigation bar, removed the sidebar toggle button, and optimized layout for mobile responsiveness.
- **Production Readiness**: Hardened `.gitignore` to exclude sensitive environment files, local database artifacts, and OS/IDE clutter.
- **Income Feature Integration**: Added `income` and `recurring_income` management, integrated into dashboard summary and financial reporting.
- **Security Patch**: Replaced `passlib` dependency with direct `bcrypt` implementation, incorporating strict 72-byte password truncation and frontend length limits to resolve hashing vulnerabilities.
- **Database Optimization**: Optimized recurring transaction logic in `app/crud/recurring.py` to run once per day per user, reducing database overhead.
- **Architecture**: Updated documentation to reflect Supabase/PostgreSQL as the primary database storage.

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
