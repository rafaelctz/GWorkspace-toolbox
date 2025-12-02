@echo off
echo ================================================
echo  GWorkspace Toolbox - Development Environment
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

echo . Python version:
python --version
echo . Node.js version:
node --version
echo.

REM Backend setup
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q -r requirements.txt

echo . Backend setup complete!
echo.

REM Frontend setup
echo Setting up Frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
) else (
    echo Node modules already installed.
)

echo . Frontend setup complete!
echo.

REM Start services
echo ================================================
echo   Starting GWorkspace Toolbox Services
echo ================================================
echo.

cd ..

echo Starting Backend on http://localhost:8000...
start "GWorkspace Toolbox Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend on http://localhost:3000...
start "GWorkspace Toolbox Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo   GWorkspace Toolbox is Running!
echo ================================================
echo.
echo  Frontend: http://localhost:3000
echo  Backend API: http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the services.
echo.

pause
