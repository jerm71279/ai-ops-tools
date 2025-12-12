@echo off
REM RAG Query Tool - Windows Access
REM Usage: rag_query.bat "your question here"

if "%~1"=="" (
    echo Starting RAG Interactive Mode...
    echo.
    wsl -d Ubuntu -e bash -c "cd /home/mavrick/Projects/Secondbrain && source venv/bin/activate && python3 query_brain.py"
) else (
    wsl -d Ubuntu -e bash -c "cd /home/mavrick/Projects/Secondbrain && source venv/bin/activate && python3 query_brain.py '%*'"
)
