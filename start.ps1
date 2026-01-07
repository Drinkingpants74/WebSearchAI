# start.ps1

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Running install.ps1..."
    & .\install.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Installation failed. Exiting."
        Read-Host "Press Enter to continue"
        exit 1
    }
}

Write-Host "Updating Application..."
git pull

Write-Host "Starting application..."
& ".venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment."
    Read-Host "Press Enter to continue"
    exit 1
}

python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: main.py execution failed."
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "Application exited successfully."
Read-Host "Press Enter to continue"
