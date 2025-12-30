@echo off
cd /d "D:\ChatBot\main"

call conda activate AIChat

:: Kill old server
netstat -ano | findstr :5000 | findstr LISTENING >nul && (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do taskkill /PID %%a /F >nul 2>&1
)

:: Start Ollama
tasklist | findstr ollama >nul || start "" ollama serve
timeout /t 8 >nul

:: Start Flask
start "Flask" cmd /c "python app.py"

timeout /t 6 >nul
start http://127.0.0.1:5000

echo.
echo Chatbot LIVE at http://127.0.0.1:5000
echo.
pause