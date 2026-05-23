# Expense Tracker

A modern and professional FastAPI expense tracker utilizing SQLite storage, dynamic currency preferences, customizable budgets, interactive animations, and a React-based interactive landing page background.

## Key Features

- **Personalized Control Center**: Dynamic welcome greetings and settings-based currency switching (NGN/USD).
- **Budget Threshold Alerts**: Real-time spending threshold analysis and visual alerts.
- **AI Insights & Category Snapshots**: Category-based percentage tracking, top focus area analysis, and reports.
- **Reporting & Data Export**: Dynamic CSV report downloads based on current filters.
- **WebGL Landing Page**: Interactive particle galaxy background effect using customized fragment shaders.

## Stack & Libraries Used

### Backend (Python)
- **FastAPI**: Modern, fast ASGI web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI server implementation.
- **Jinja2**: Modern and designer-friendly templating language for Python.
- **SQLite3** (Standard Library): Serverless, local SQL database engine.
- **Pillow**: Python Imaging Library for visual image manipulations.
- **python-multipart**: Streaming multipart parser for handling form submissions.

### Frontend (JavaScript / CSS / React)
- **React**: Declarative component-based UI library.
- **OGL**: Minimal WebGL library used to render the interactive particle galaxy canvas.
- **Vite**: High-performance frontend toolchain/bundler.
- **Vanilla CSS**: Curated color tokens, transition effects, and responsive layouts.

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
