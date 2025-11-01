@echo off

python -m venv .venv
if errorlevel 1 (
    echo "ERROR: Failed to create virtual environment."
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo "ERROR: Failed to activate virtual environment."
    pause
    exit /b 1
)

:ask_gpu
echo "######### Select GPU Type #########"
echo "| 1. Nvidia (CUDA)                |"
echo "| 2. AMD (Vulkan)                 |"
echo "| 3. Metal (Apple)                |"
echo "| 4. SYCL (Intel GPU w/ OneAPI)   |"
echo "| 5. CPU (No GPU)                 |"
echo "###################################"

set "gpuChoice="
set /p gpuChoice=Select Number (1-5):
echo.

if "%gpuChoice%"=="1" goto cuda
if "%gpuChoice%"=="2" goto vulkan
if "%gpuChoice%"=="3" goto metal
if "%gpuChoice%"=="4" goto sycl
if "%gpuChoice%"=="5" goto cpu

echo *** Invalid choice. Please enter 1-5. ***
goto ask_gpu


:cuda
echo "Building Llama.cpp for CUDA (Nvidia) Backend..."
set "CMAKE_ARGS=-DGGML_CUDA=on"
goto install_llama

:vulkan
echo "Building Llama.cpp for Vulkan (AMD) Backend..."
set "CMAKE_ARGS=-DGGML_VULKAN=on"
goto install_llama

:metal
echo "Metal is Unsupported on Windows Devices..."
goto ask_gpu

:sycl
echo "Building Llama.cpp for SYCL (Intel) Backend..."
REM ---- Intel oneAPI environment (if installed) ----
if exist "%INTEL_ONEAPI_ROOT%\setvars.bat" (
    call "%INTEL_ONEAPI_ROOT%\setvars.bat"
) else if exist "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" (
    call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
) else (
    echo "WARNING: Intel oneAPI not found – SYCL build will fail."
)
set "CMAKE_ARGS=-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx"
goto install_llama

:cpu
echo "Building Llama.cpp for CPU Backend..."
set "CMAKE_ARGS=-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"
goto install_llama


:install_llama
echo "Installing llama-cpp-python (CMAKE_ARGS=%CMAKE_ARGS%) ..."
pip install --upgrade pip
pip install llama-cpp-python %CMAKE_ARGS%
if errorlevel 1 (
    echo "ERROR: llama-cpp-python installation failed."
    pause
    exit /b 1
)

pip install flet httpx beautifulsoup4
if errorlevel 1 (
    echo "ERROR: Additional packages failed to install."
    pause
    exit /b 1
)

echo.
echo "Install Complete! Please run start.bat to start the application."
pause