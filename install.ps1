# install.ps1

$llamaBaseURL = "https://github.com/ggml-org/llama.cpp/releases/download/"
$llamaVersionID = "b7898"

$whisperBaseURL="https://github.com/Drinkingpants74/WebSearchAI-Binaries/releases/download/whisper-"
$whisperVersionID="v1.8.3"


function Download-Binaries {
    param ([string]$downloadURL)

    $filename = Split-Path $downloadURL -Leaf
    # Invoke-WebRequest -Uri $downloadURL -OutFile $filename
    curl.exe -L -o $filename $downloadURL
    Expand-Archive -Path $filename -DestinationPath "src/Llama.cpp" -Force
    Set-Content -Path "src/Llama.cpp/version" -Value $llamaVersionID
    Remove-Item $filename
}

function Download-DLLs {
    param ([string]$downloadURL)

    $filename = Split-Path $downloadURL -Leaf
    curl.exe -L -o $filename $downloadURL
    Expand-Archive -Path $filename -DestinationPath "src/Llama.cpp" -Force
    Remove-Item $filename
}

function Download-Whisper {
    param ([string]$downloadURL)

    $filename = Split-Path $downloadURL -Leaf
    # Invoke-WebRequest -Uri $downloadURL -OutFile $filename
    curl.exe -L -o $filename $downloadURL
    Expand-Archive -Path $filename -DestinationPath "src/Whisper.cpp" -Force
    Set-Content -Path "src/Whisper.cpp/version" -Value $whisperVersionID
    Remove-Item $filename
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".venv\Scripts\Activate.ps1"

# Download and unpack Llama.cpp binaries
if (Test-Path "src/Llama.cpp") {
    $installedVersion = Get-Content "src/Llama.cpp/version"

    if ($installedVersion -ne $llamaVersionID) {
        Write-Host "Updating Llama.cpp Binaries"
        $userBackend = Get-Content "src/Llama.cpp/backend"
        Remove-Item "src/Llama.cpp" -Recurse -Force

        switch ($userBackend) {
            "CUDA" {
                Write-Host "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-cuda-13.1-x64.zip"
                Download-DLLs "${llamaBaseURL}${llamaVersionID}/cudart-llama-bin-win-cuda-13.1-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "CUDA"
            }
            "ROCm" {
                Write-Host "Downloading Llama.cpp for HIP (AMD) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-hip-radeon-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "ROCm"
            }
            "Vulkan" {
                Write-Host "Downloading Llama.cpp for GPU (Vulkan) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-vulkan-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "Vulkan"
            }
            default { # CPU Backend
                Write-Host "Downloading Llama.cpp for CPU Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "CPU"
            }
        }
    }
} else {
    # First time installation - prompt user for backend
    while ($true) {
        Write-Host ""
        Write-Host "######### Select GPU Type #########"
        Write-Host "| 1. Nvidia (CUDA 13.1)           |"
        Write-Host "| 2. AMD (HIP)                   |"
        Write-Host "| 3. GPU (Vulkan)                 |"
        Write-Host "| 4. CPU (No GPU)                 |"
        Write-Host "###################################"

        $gpuChoice = Read-Host "Select Number (1-4)"
        Write-Host ""

        switch ($gpuChoice) {
            "1" {
                Write-Host "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-cuda-13.1-x64.zip"
                Download-DLLs "${llamaBaseURL}${llamaVersionID}/cudart-llama-bin-win-cuda-13.1-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "CUDA"
                break
            }
            "2" {
                Write-Host "Downloading Llama.cpp for HIP (AMD) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-hip-radeon-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "ROCm"
                break
            }
            "3" {
                Write-Host "Downloading Llama.cpp for GPU (Vulkan) Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-vulkan-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "Vulkan"
                break
            }
            "4" {
                Write-Host "Downloading Llama.cpp for CPU Backend..."
                Download-Binaries "${llamaBaseURL}${llamaVersionID}/llama-${llamaVersionID}-bin-win-x64.zip"
                Set-Content -Path "src/Llama.cpp/backend" -Value "CPU"
            }
            default {
                Write-Host "Invalid Input! Only Enter the Number (1-4)..."
            }
        }
    }
}

# Download and unpack Whisper.cpp binaries
if (Test-Path "src/Whisper.cpp") {
    $installedVersion = Get-Content "src/Whisper.cpp/version"

    if ($installedVersion -ne $llamaVersionID) {
        Write-Host "Updating Llama.cpp Binaries..."
        Remove-Item "src/Llama.cpp" -Recurse -Force
        Download-Binaries "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-Windows.zip"
    }
} else {
    Download-Binaries "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-Windows.zip"
}

# Install base requirements
python -m pip install flet[all] httpx beautifulsoup4 pypng readability-lxml numpy openai

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Install Complete! Please run start.ps1 to start the application."
} else {
    Write-Host "Base Installation Failed."
}
