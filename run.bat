@echo off
echo Starting the Thai Traffic Law RAG program...
.venv\Scripts\uvicorn.exe app:app --reload --host 0.0.0.0 --port 8000
pause