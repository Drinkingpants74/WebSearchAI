#!/bin/bash

# If Linux System:
# Check for APT | DNF | Pacman
# Install gstreamer-dev & mpv-devel
if [ `uname -s` != "Darwin" ]; then
  echo "WebSearchAI uses Flet which requires GStreamer and MPV."
  echo -n "Do you consent to installing the packages (y/N): "
  read doInstall

  if [ $doInstall == "y" ]; then
    if [ `command -v apt >/dev/null` ]; then
      sudo apt update
      sudo apt install -y libgtk-3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libmpv-dev mpv
    elif [ `command -v dnf >/dev/null` ]; then
      sudo dnf install -y gtk3-devel gstreamer1-devel gstreamer1-plugins-base-devel mpv-devel mpv
    else
      echo "Please install GTK3 development files, GStreamer developer files and MPV development files"
    fi
  else
    echo "WebSearchAI will install, but may not work without Flet requirements."
  fi
fi

python3 -m venv .venv
source python3 -m venv .venv

declare done=false
while [ done == false ]; do

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
    echo "Building Llama.cpp for CUDA (Nvidia) Backend..."
    CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
    done=true
  elif [ $gpuChoice == "2" ]; then
    echo "Building Llama.cpp for Vulkan (AMD) Backend..."
    CMAKE_ARGS="-DGGML_VULKAN=on" pip install llama-cpp-python
    done=true
  elif [ $gpuChoice == "3" ]; then
    echo "Building Llama.cpp for Metal (Apple) Backend..."
    CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python
    done=true
  elif [ $gpuChoice == "4" ]; then
    echo "Building Llama.cpp for SYCL (Intel) Backend..."
    source /opt/intel/oneapi/setvars.sh
    CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" pip install llama-cpp-python
    done=true
  elif [ $gpuChoice == "5" ]; then
    echo "Building Llama.cpp for CPU Backend..."
    CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
    done=true
  else
    echo "Invalid Input! Only Enter the Number (1-5)..."
  fi

done
pip install flet httpx beautifulsoup4

echo "Install Complete! Please run start.sh to start the application."