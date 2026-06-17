@echo off
cd /d "H:\Docker开发项目\另外账号开发\BoscoTsang\BoscoTsang-0.1"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
