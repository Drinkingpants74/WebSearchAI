#!/bin/bash

declare baseURL="https://github.com/ggml-org/llama.cpp/releases/download/"
declare versionID="b7658"

download_binaries() {
    local downloadURL="$1"
    local filename=$(basename "$downloadURL")
    curl -LO "$downloadURL"
    tar -xzf "$filename"
    local foldername=$(echo "$filename" | awk -F '-' '{print $1 "-" $2}')
    mv $foldername Llama.cpp
    echo "$versionID" > Llama.cpp/version
    rm $filename
}

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Download and Unpack Llama.cpp binaries
if [ -d "Llama.cpp" ]; then
    installedVersion=$(cat Llama.cpp/version)
    if [ $installedVersion != $versionID ]; then
        echo "Updating Llama.cpp Binaries"
        userBackend=$(cat Llama.cpp/backend)
        rm -r Llama.cpp/
        if [ "$userBackend" == "Metal" ]; then
            echo "Downloading Llama.cpp for Metal (Apple) Backend..."
            download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-macos-arm64.tar.gz"
            # Llama.cpp Binaries are NOT signed. In order to run them we need to
            # add the files as exclusions to Gatekeeper.
            xattr -dr com.apple.quarantine Llama.cpp/
            echo "Metal" > Llama.cpp/backend
        elif [ "$userBackend" == "CUDA" ]; then
            # echo "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
            echo "No Linux CUDA Binaries Available Yet. Falling Back to Vulkan..."
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "CUDA" > Llama.cpp/backend
            break
        elif [ "$userBackend" == "ROCm" ]; then
            # echo "Downloading Llama.cpp for ROCm (AMD) Backend..."
            echo "No Linux ROCm Binaries Available Yet. Falling Back to Vulkan..."
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "ROCm" > Llama.cpp/backend
            break
        elif [ "$userBackend" == "Vulkan" ]; then
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "Vulkan" > Llama.cpp/backend
            break
        else # CPU Backend
            echo "Downloading Llama.cpp for CPU Backend..."
            download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-x64.tar.gz"
            echo "CPU" > Llama.cpp/backend
            break
        fi
    fi
else
    if [ `uname -s` == "Darwin" ]; then
        echo "Downloading Llama.cpp for Metal (Apple) Backend..."
        download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-macos-arm64.tar.gz"
        # Llama.cpp Binaries are NOT signed. In order to run them we need to
        # add the files as exclusions to Gatekeeper.
        xattr -dr com.apple.quarantine Llama.cpp/
        echo "Metal" > Llama.cpp/backend
    else
        while :; do
            # echo "######### Select GPU Type #########"
            # echo "| 1. Nvidia (CUDA 13.1)           |"
            # echo "| 2. AMD (ROCm)                   |"
            # echo "| 3. GPU (Vulkan)                 |"
            # echo "| 4. CPU (No GPU)                 |"
            # echo "###################################"

            echo "######### Select GPU Type #########"
            echo "| 1. Nvidia (CUDA 13.1)           |"
            echo "| 2. GPU (Vulkan)                 |"
            echo "| 3. CPU (No GPU)                 |"
            echo "###################################"

            echo -n "Select Number (1-3): "
            read gpuChoice
            echo ""

            if [ $gpuChoice == "1" ]; then
                echo "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
                download_binaries "https://github.com/Drinkingpants74/WebSearchAI/releases/download/${versionID}//llama-${versionID}-bin-linux-cuda-x64.tar.gz"
                echo "CUDA" > Llama.cpp/backend
                break
            elif [ $gpuChoice == "2" ]; then
                echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
                download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
                echo "Vulkan" > Llama.cpp/backend
                break
            elif [ $gpuChoice == "3" ]; then
                echo "Downloading Llama.cpp for CPU Backend..."
                download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-x64.tar.gz"
                echo "CPU" > Llama.cpp/backend
                break
            else
                echo "Invalid Input! Only Enter the Number (1-3)..."
            fi

            # if [ $gpuChoice == "1" ]; then
            #     # echo "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
            #     echo "No Linux CUDA Binaries Available Yet. Falling Back to Vulkan..."
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "CUDA" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "2" ]; then
            #     # echo "Downloading Llama.cpp for ROCm (AMD) Backend..."
            #     echo "No Linux ROCm Binaries Available Yet. Falling Back to Vulkan..."
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "ROCm" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "3" ]; then
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "Vulkan" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "4" ]; then
            #     echo "Downloading Llama.cpp for CPU Backend..."
            #     download_binaries "${baseURL}/${versionID}/llama-${versionID}-bin-ubuntu-x64.tar.gz"
            #     echo "CPU" > Llama.cpp/backend
            #     break
            # else
            #     echo "Invalid Input! Only Enter the Number (1-4)..."
            # fi

        done
    fi
fi

# Install Base Requirements
python3 -m pip install PySide6 httpx beautifulsoup4 pypng readability-lxml numpy
if [ $? == 0 ]; then
    echo "Install Complete! Please run start.sh to start the application."
else
    echo "Base Installation Failed."
fi
