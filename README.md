# WebSearchAI (Beta)
A Local LLM Chat Tool with built in Web Searching

### The Skinny
Tired of using online AI Models to solve your problems, just so they can sell your data to the highest bidder?
Well so was I. So I built a brand new tool to chat with Local AI LLMs, and extend them with the power of **THE INTERNET**.

> ### BETA STATUS
> This application is in *BETA*. Core functionality is 100% built, but there are a few features I want to add and others I want to refine.
> 
>Do not expect this project to be as good as Claude/Grok/Chat-GPT in its current state. But one day, I'll get it there.
> 
>Also, this is a one man operation. I have no team, no backers. This project is made with passion alone.

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
The goal of the `WebSearchAI` project is just as the name states; Give Local LLMs the ability to search the web.

Local LLMs are a really useful tool. The problem is they minute they'remade, the information inside them is out of date. So how do we fix that?
We let the AI search the web for modern information.

### Current Features
* Local Chat with LLM
* AI can "Search" to help answer your prompt
* Character Cards

### Requirements
* Python3.13 (Recommended) -> Python3.9(Minimum)
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
That, or I'm just stupid. So for now, AMD cards will use Vulkan.

### Planned Features
* Enhanced Web Searching
* RAG
* File Uploads W/ Image Support

#### ⚠️WARNING⚠️
**This project uses Artificial Intelligence. Information given by AI models may not always be factual.**

#### 🛑NOTICE🛑
**_PLEASE_ use this project responsibiy. I am not responsible for the actions of the user. By downloading and using this project, you (the user) assume all responsiblty.**
