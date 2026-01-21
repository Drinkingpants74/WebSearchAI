#!/bin/bash

declare llamaBaseURL="https://github.com/ggml-org/llama.cpp/releases/download/"
declare llamaVersionID="b7772"

declare whisperBaseURL="https://github.com/Drinkingpants74/WebSearchAI-Binaries/releases/download/whisper-"
declare whisperVersionID="v1.8.3"

download_binaries() {
    local downloadURL="$1"
    local filename=$(basename "$downloadURL")
    curl -LO "$downloadURL"
    tar -xzf "$filename"
    local foldername=$(echo "$filename" | awk -F '-' '{print $1 "-" $2}')
    mv $foldername src/Llama.cpp/
    echo "$llamaVersionID" > src/Llama.cpp/version
    rm $filename
}

download_whisper() {
    local downloadURL="$1"
    local filename=$(basename "$downloadURL")
    curl -LO "$downloadURL"
    mkdir src/Whisper.cpp
    cd src/Whisper.cpp
    tar -xzf "../../$filename"
    cd ../..
    echo "$whisperVersionID" > src/Whisper.cpp/version
    rm $filename
}

echo "Updating Application..."
git pull

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Download and Unpack Llama.cpp binaries
if [ -d "src/Llama.cpp" ]; then
    installedVersion=$(cat src/Llama.cpp/version)
    if [ $installedVersion != $llamaVersionID ]; then
        echo "Updating Llama.cpp Binaries"
        userBackend=$(cat src/Llama.cpp/backend)
        rm -r src/Llama.cpp/
        if [ "$userBackend" == "Metal" ]; then
            echo "Downloading Llama.cpp for Metal (Apple) Backend..."
            download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-macos-arm64.tar.gz"
            # Llama.cpp Binaries are NOT signed. In order to run them we need to
            # add the files as exclusions to Gatekeeper.
            xattr -dr com.apple.quarantine src/Llama.cpp/
            echo "Metal" > src/Llama.cpp/backend
        elif [ "$userBackend" == "CUDA" ]; then
            # echo "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
            echo "No Linux CUDA Binaries Available Yet. Falling Back to Vulkan..."
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "CUDA" > src/Llama.cpp/backend
            break
        elif [ "$userBackend" == "ROCm" ]; then
            # echo "Downloading Llama.cpp for ROCm (AMD) Backend..."
            echo "No Linux ROCm Binaries Available Yet. Falling Back to Vulkan..."
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "ROCm" > src/Llama.cpp/backend
            break
        elif [ "$userBackend" == "Vulkan" ]; then
            echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            echo "Vulkan" > src/Llama.cpp/backend
            break
        else # CPU Backend
            echo "Downloading Llama.cpp for CPU Backend..."
            download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-x64.tar.gz"
            echo "CPU" > src/Llama.cpp/backend
            break
        fi
    fi
else
    if [ `uname -s` == "Darwin" ]; then
        echo "Downloading Llama.cpp for Metal (Apple) Backend..."
        download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-macos-arm64.tar.gz"
        # Llama.cpp Binaries are NOT signed. In order to run them we need to
        # add the files as exclusions to Gatekeeper.
        xattr -dr com.apple.quarantine src/Llama.cpp/
        echo "Metal" > src/Llama.cpp/backend
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
                download_binaries "https://github.com/Drinkingpants74/WebSearchAI-Binaries/releases/download/${llamaVersionID}/llama-${llamaVersionID}-bin-linux-cuda-x64.tar.gz"
                echo "CUDA" > src/Llama.cpp/backend
                break
            elif [ $gpuChoice == "2" ]; then
                echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
                download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
                echo "Vulkan" > src/Llama.cpp/backend
                break
            elif [ $gpuChoice == "3" ]; then
                echo "Downloading Llama.cpp for CPU Backend..."
                download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-x64.tar.gz"
                echo "CPU" > src/Llama.cpp/backend
                break
            else
                echo "Invalid Input! Only Enter the Number (1-3)..."
            fi

            # if [ $gpuChoice == "1" ]; then
            #     # echo "Downloading Llama.cpp for CUDA (Nvidia) Backend..."
            #     echo "No Linux CUDA Binaries Available Yet. Falling Back to Vulkan..."
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "CUDA" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "2" ]; then
            #     # echo "Downloading Llama.cpp for ROCm (AMD) Backend..."
            #     echo "No Linux ROCm Binaries Available Yet. Falling Back to Vulkan..."
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "ROCm" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "3" ]; then
            #     echo "Downloading Llama.cpp for GPU (Vulkan) Backend..."
            #     download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-vulkan-x64.tar.gz"
            #     echo "Vulkan" > Llama.cpp/backend
            #     break
            # elif [ $gpuChoice == "4" ]; then
            #     echo "Downloading Llama.cpp for CPU Backend..."
            #     download_binaries "${llamaBaseURL}/${llamaVersionID}/llama-${llamaVersionID}-bin-ubuntu-x64.tar.gz"
            #     echo "CPU" > Llama.cpp/backend
            #     break
            # else
            #     echo "Invalid Input! Only Enter the Number (1-4)..."
            # fi

        done
    fi
fi

# Install Whisper.cpp
if [ -d "src/Whisper.cpp" ]; then
    installedVersion=$(cat src/Whisper.cpp/version)
    if [ $installedVersion != $whisperVersionID ]; then
        echo "Updating Whisper.cpp Installation..."
        rm -r src/Whisper.cpp/
        if [ `uname -s` == "Darwin" ]; then
            download_whisper "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-MacOS.tar.gz"
            xattr -dr com.apple.quarantine src/Llama.cpp/
        else
            download_whisper "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-Linux.tar.gz"
        fi
    fi
else
    echo "Installing Whisper.cpp..."
    if [ `uname -s` == "Darwin" ]; then
        download_whisper "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-MacOS.tar.gz"
        xattr -dr com.apple.quarantine src/Llama.cpp/
    else
        download_whisper "${whisperBaseURL}${whisperVersionID}/whisper-${whisperVersionID}-Linux.tar.gz"
    fi
fi


if [ ! -f src/nomic-embed-text-v.1.5.Q4_K_M.gguf ]; then
    echo "Downloading Text Embedder..."
    cd src/
    curl -LO https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf
    cd ..
fi


# Install Base Requirements
python3 -m pip install flet[all] httpx beautifulsoup4 pypng readability-lxml numpy openai
if [ $? == 0 ]; then
    echo "Install Complete! Please run start.sh to start the application."
else
    echo "Base Installation Failed."
fi
