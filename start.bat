@echo off

if not exist ".venv\Scripts\activate.bat" (
    echo "Virtual environment not found. Running install.bat..."
    call install.bat
    if errorlevel 1 (
        echo "ERROR: Installation failed. Exiting."
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo "ERROR: Failed to activate virtual environment."
    pause
    exit /b 1
)

python Main.py
if errorlevel 1 (
    echo "ERROR: Main.py execution failed."
    pause
    exit /b 1
)

echo "Application exited successfully."
pause