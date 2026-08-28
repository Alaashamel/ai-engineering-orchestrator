@echo off
cd /d "D:\portfolio-projects\creative - ideas\project - 5\apps\api"
set PYTHONPATH=D:\portfolio-projects\creative - ideas\project - 5
"D:\portfolio-projects\creative - ideas\project - 5\.venv\Scripts\uvicorn.exe" src.main:app --host 0.0.0.0 --port 8000
