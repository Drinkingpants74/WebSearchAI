#!/bin/bash

# If Linux System:
# Check for APT | DNF | Pacman
# Install gstreamer-dev & mpv-devel

python3 -m venv .venv
source python3 -m venv .venv

echo "######### Select GPU Type #########"
echo "| 1. Nvidia (CUDA)                |"
echo "| 2. AMD (Vulkan)                 |"
echo "| 3. Metal (Apple)                |"
echo "| 4. SYCL (Intel GPU W/ OneAPI)   |"
echo "| 5. CPU (No GPU)                 |"
echo "###################################"

echo -n "Select Number (1-6): "
read gpuChoice
echo ""


if [ $gpuChoice == "1" ]; then
  CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
elif [ $gpuChoice == "2" ]; then
  CMAKE_ARGS="-DGGML_VULKAN=on" pip install llama-cpp-python
elif [ $gpuChoice == "3" ]; then
  CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python
elif [ $gpuChoice == "4" ]; then
  source /opt/intel/oneapi/setvars.sh
  CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" pip install llama-cpp-python
elif [ $gpuChoice == "5" ]; then
  CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
fi

pip install flet httpx beautifulsoup4

echo "Install Complete! Please run start.sh to start the application."