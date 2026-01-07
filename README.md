# WebSearch AI
A Local LLM Chat Tool with built in Web Searching

### The Skinny
Tired of using online AI Models to solve your problems, just so they can sell your data to the highest bidder?
Well so was I. So I built a brand new tool to chat with Local AI LLMs, and extend them with the power of **_THE INTERNET_**.

> ### PROJECT STATUS
> This application is now **OUT OF BETA!** It's stable and I'm happy with where it's at.
> 
> This application is around 60-70% of the quality of Grok/Claude/Chat-GPT, and that's running a 4B model.
> 
> Also, this is a one man operation. I have no team, no backers. This project is made with passion alone.

## Quick Start
#### All Systems
1. Open a terminal where you want to install the project
2. `git clone https://github.com/Drinkingpants74/WebSearchAI`
3. `cd WebSearchAI/`

#### Linux & MacOS
Run `start.sh` or `install.sh` and follow the instructions.
#### Windows
Run `start.bat` or `install.bat` and follow the instructions.

## Description
The goal of the `WebSearch AI` project is just as the name states; Give Local LLMs the ability to search the web.

Local LLMs are a really useful tool. The problem is they minute they're made, the information inside them is out of date. So how do we fix that?
We let the AI search the web for modern information.

### Current Features
* Chat with an LLM Locally
* AI can "Search" to help answer your prompt
* Keep a History of your Chats (On Device only)

### Requirements
* Python3 (Recommended: **3.14**)
* A Supported Inference Device (List Below)
* GGUF Models

### Supported Device
* **_Nvidia w/ CUDA_**
* **_AMD w/ Vulkan_**
* **_Apple w/ Metal_**
* **_Intel w/ SYCL & OneAPI_**
* **_CPU_** _(Recommend Ryzen 5000 Series / Intel 10th Gen or Newer)_

#### ROCm Support
As an AMD user myself, ROCm support is something I'd love to add. However, the `llama-cpp-python` library seems to struggle with ROCm.
That, or I'm just stupid. Support is currently **_EXPERIMENTAL_**, but I recommend using Vulkan if you don't want to tinker.

### Planned Features
* Character Cards (Rebuild)
* OpenAI API v2 Support (Use Any Backend)
* Enhanced Web Searching
* RAG
* File Uploads W/ Image Support

#### ⚠️WARNING⚠️
**This project uses Artificial Intelligence. Information given by AI models may not always be factual.**

#### 🛑NOTICE🛑
**_PLEASE_ use this project responsibiy. I am not responsible for the actions of the user. By downloading and using this project, you (the user) assume all responsiblty.**
