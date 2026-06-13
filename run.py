try:
    import uvicorn
except ModuleNotFoundError as exc:
    raise SystemExit(
        "uvicorn is not installed for this Python interpreter.\n"
        "Use the project's virtual environment interpreter:\n"
        r"  .\.venv\Scripts\python.exe run.py\n"
        "Or install dependencies with:\n"
        r"  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    ) from exc


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
