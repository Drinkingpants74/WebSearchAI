import re
import sys
import os
from datetime import datetime
import gc
import traceback
import numpy as np
import subprocess
from platform import system as get_system
from time import sleep as timeSleep
import flet as ft
import threading
import json

# from llama_cpp import Llama

import WebSearch
import Settings
import API
import Audio
import Weather

process = None
llm = None

searchContext = None
embeddings = None
embedder = None

usrPrompt = ""

model_thinking = False
think_thread_running = False
thinking_thread = None

tokenizedBody = []
previousInfo = []

def unload_embedder():
    global embedder
    if (embedder is not None):
        embedder.terminate()
        embedder.wait()
        embedder = None
        gc.collect()

def load_embedder():
    if (Settings.embedderAPIPath == "http://127.0.0.1:3623"):
        launch_embedder()
    API.set_embedder()

def launch_embedder():
    global embedder
    # Mobile Embedder
    # embedder = Llama(
    #     model_path=f"src/{Settings.embedderModelID}",
    #     embeddings=True,
    #     n_gpu_layers=0,
    #     n_ctx=2048,
    #     n_batch=2048,
    #     chat_format="chatml",
    #     verbose=False,
    # )
    global embedder
    llamapath = os.path.join(Settings.BASE_DIR, "Llama.cpp", "llama-server")
    if (get_system() == "Windows"):
        llamapath += ".exe"
    embedder = subprocess.Popen([
        llamapath,
        '-m', os.path.join(Settings.BASE_DIR, "nomic-embed-text-v1.5.Q4_K_M.gguf"),
        '--port', '3623', '--embedding',
        '-ngl', '0', '-c', '4096',
        '-b', '2048',
        #'--top-k', '40',
        #'-ctk', 'q8_0', '-ctv', 'q8_0', '-fa', 'on'
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )
    timeSleep(2)
    if (embedder.poll()):
        stderr_output = embedder.stderr.read().decode() if embedder.stderr else ""
        print(f"Llama.cpp Embedder failed to launch: {stderr_output}")

def update_embedding(pages):
    global embeddings, embedder

    MAX_CHARS = 1000
    toEmbed = [item["CHUNK"][:MAX_CHARS] for item in pages]

    response = API.send_embedding(toEmbed)

    if (response is None):
        return None

    data = response.data
    embedEncoded = [item.embedding for item in data]

    new_emb = np.array(embedEncoded, dtype=np.float32)
    new_emb = new_emb / np.linalg.norm(new_emb, axis=-1, keepdims=True)
    embeddings = new_emb if embeddings is None else np.vstack([embeddings, new_emb])


def get_context_from_embed(prompt, top_k, threshold):
    global embeddings, embedder
    if (embeddings is not None):
        response = API.send_embedding(prompt)

        if (response is None):
            return None

        data = response.data
        embedEncoded = [item.embedding for item in data]

        q_emb = np.array(embedEncoded[0], dtype=np.float32)
        q_emb = q_emb / np.linalg.norm(q_emb)  # This should work fine
        scores = np.dot(embeddings, q_emb)

        # Filter by threshold
        valid_indices = np.where(scores >= threshold)[0]
        if len(valid_indices) == 0:
            print(f"No chunks above threshold {threshold}")
            return None

        # Get top K from valid indices
        valid_scores = scores[valid_indices]
        best_index = np.argsort(valid_scores)[-top_k:][::-1]
        best_indecies = valid_indices[best_index]
        embContext = "\n\n".join(WebSearch.previousInfo[id] for id in best_indecies)
        return embContext
    return None

# llama-cpp-python code (Possible Mobile Usage)
# def update_embedding(pages):
#     global embeddings, embedder

#     # MAX_CHARS = 1000
#     toEmbed = [item["CHUNK"] for item in pages]
#     embedEncoded = []
#     toEmbed = []
#     for item in pages:
#         if (item["CHUNK"].strip() != ""):
#             # print(item["CHUNK"])
#             embedEncoded.extend(embedder.embed([item["CHUNK"]]))
#             # toEmbed.append(str(item["CHUNK"]))

#     new_emb = np.array(embedEncoded, dtype=np.float32)
#     new_emb = new_emb / np.linalg.norm(new_emb, axis=-1, keepdims=True)
#     embeddings = new_emb if embeddings is None else np.vstack([embeddings, new_emb])


# def get_context_from_embed(prompt, top_k, threshold):
#     global embeddings, embedder
#     if (embeddings is not None):

#         embedEncoded = embedder.embed([prompt])

#         q_emb = np.array(embedEncoded[0], dtype=np.float32)
#         q_emb = q_emb / np.linalg.norm(q_emb)  # This should work fine
#         scores = np.dot(embeddings, q_emb)

#         # Filter by threshold
#         valid_indices = np.where(scores >= threshold)[0]
#         if len(valid_indices) == 0:
#             print(f"No chunks above threshold {threshold}")
#             return None

#         # Get top K from valid indices
#         valid_scores = scores[valid_indices]
#         best_index = np.argsort(valid_scores)[-top_k:][::-1]
#         best_indecies = valid_indices[best_index]
#         embContext = "\n\n".join(WebSearch.previousInfo[id] for id in best_indecies)
#         # print("Chosen Context:", embContext)
#         return embContext
#     return None

def create_message(role: str, text: str):
    return {"role": role, "content": text}

def load_model(modelName, userInput: ft.TextField, page: ft.Page, update_function):
    Settings.apiModelID = modelName
    if (not Settings.apiMode):
        launch_llama()
    API.check_toolCalling()
    # Settings.doToolCalls = True
    # toolsEnabled = API.check_toolCalling()
    # if (toolsEnabled):
    #     userInput.value = "Tools Enabled"
    #     page.run_task(update_function)
    #     timeSleep(2)
    if (userInput.disabled):
        userInput.value = ""
        userInput.disabled = False
    page.run_task(update_function)

def unload_model():
    global process
    if (process is not None):
        process.terminate()
        process.wait()
        process = None
        gc.collect()

def launch_llama():
    unload_model()
    global process
    llamapath = os.path.join(Settings.BASE_DIR, "Llama.cpp", "llama-server")
    if (get_system() == "Windows"):
        llamapath += ".exe"
    process = subprocess.Popen([
        llamapath,
        '-m', os.path.join(Settings.modelsPath, Settings.apiModelID),
        '--port', '3774',
        '-ngl', str(Settings.gpuLayers),
        '-c', str(Settings.ctxSize),
        '-b', str(Settings.batchSize),
        '--top-k', str(Settings.top_K),
        '-ctk', 'q8_0', '-ctv', 'q8_0', '-fa', 'on',
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )
    timeSleep(2)
    if (process.poll()):
        stderr_output = process.stderr.read().decode() if process.stderr else ""
        print(f"Llama.cpp backend failed to launch: {stderr_output}")

def set_system_message():
    systemMessage = Settings.system_prompt_default

    if (Settings.userInfo is not None):
        systemMessage += "\n\nUser Information:\n" + Settings.userInfo

    if (Settings.cardPath is None):
        systemMessage += f"\n\nCurrent Date: {datetime.now().strftime("%A %B %-d %Y")}"

    Settings.messages.append(create_message("system", systemMessage))
    Settings.messageID += 1

def update_system_message(new_message):
    # print(f"NEW MESSAGE: {new_message}")
    for message in Settings.messages:
        if (message["role"] == "system"):
            # print(f"SYS MESSAGE: {message["content"]}")
            message["content"] = new_message

def extract_keywords(text, top_k=Settings.top_K, ngram_range=(1, 5)):
    """
    Extract keywords from text using embeddings

    Args:
        text: Input text to extract keywords from
        top_k: Number of top keywords to return
        ngram_range: (min, max) word length for candidates
    """
    # Generate candidate keywords (n-grams)
    words = re.findall(r'\b\w+\b', text.lower())

    # Filter out very short words and common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those'}
    words = [w for w in words if w not in stop_words and len(w) > 2]

    # Generate n-grams
    candidates = []
    for n in range(ngram_range[0], ngram_range[1] + 1):
        for i in range(len(words) - n + 1):
            candidates.append(' '.join(words[i:i+n]))

    # Remove duplicates while preserving order
    candidates = list(dict.fromkeys(candidates))

    if not candidates:
        return []

    # Embed the full text
    text_response = API.send_embedding(text)

    if (text_response is None):
        print("RESPONSE WAS NONE")
        return False

    text_embed = np.array(text_response.data[0].embedding, dtype=np.float32)
    # text_embed = np.array(text_response.json()['data'][0]['embedding'], dtype=np.float32)
    text_embed = text_embed / np.linalg.norm(text_embed)

    # Embed all candidates
    candidates_response = API.send_embedding(candidates)
    if (candidates_response is None):
        return
    candidates_embeds = [item.embedding for item in candidates_response.data]
    candidates_embeds = np.array(candidates_embeds, dtype=np.float32)
    candidates_embeds = candidates_embeds / np.linalg.norm(candidates_embeds, axis=-1, keepdims=True)

    # Calculate similarity scores
    scores = np.dot(candidates_embeds, text_embed)

    # Get top K
    top_indices = np.argsort(scores)[-top_k:][::-1]
    keywords = [(candidates[i], scores[i]) for i in top_indices]

    return keywords


def generate_response(prompt: str, label: ft.Markdown, page: ft.Page, update_function):
    global searchContext, embeddings, embedder, cancel_run, model_thinking, usrPrompt
    if Settings.apiModelID is None:
        label.value = "No Model Loaded."
        page.run_task(update_function)
        return None

    usrPrompt = prompt
    Settings.messages.append(create_message(role="user", text=prompt))

    # if Settings.chatName == "Unnamed Chat":
    #     API.create_chatName()

    if Settings.chatName == "Unnamed Chat":
        keywords = extract_keywords(prompt)

        if keywords:
            chatNameText = ' '.join(keywords[0][0].split())  # Clean title case if needed
        else:
            chatNameText = "Untitled Chat"

        Settings.chatName = datetime.now().strftime("%Y_%m_%d_%H%M_|") + str(chatNameText)
        if (Settings.chatName[-1] == ".") or (Settings.chatName[-1] == "?"):
            Settings.chatName = Settings.chatName[:-1]
        if sys.platform == "win32":
            invalid_chars = r'[<>:"/\\|?*]+'
            Settings.chatName = re.sub(invalid_chars, "_", Settings.chatName)

    if (Settings.doSearch):
        # if (cancel_run):
        #     return None
        # label.value = f"**{Settings.username_AI}:** Searching The Web..."
        # page.run_task(update_function)

        providedURLs = []
        for chunk in prompt.split('\n'):
            for word in chunk.split(' '):
                word = word.strip()
                if ("http://" in word) or ("https://" in word):
                    for char in ['[','<','>',':','"','/','\\','|','?','*',']','+','\'', ',', ';', '.', '{', '}', '-', '_', '=']:
                        if (word[-1] == char):
                            word = word[:-1]
                    providedURLs.append(word)


        if (len(providedURLs) > 0):
            label.value = f"**{Settings.username_AI}:** Scraping Provided URL..."
            page.run_task(update_function)
            # print(f"URL PULL: {providedURLs}")
            urlPull = WebSearch.cleanup(providedURLs)
            if (urlPull is not None):
                update_embedding(urlPull)

    thinking = True
    toolMode = "auto" if (Settings.doSearch) else "none"

    while thinking:
        full_response = ""
        reasoning_response = ""
        addText = True
        addReasonText = False
        thread_running = False
        thinking_thread = None
        runTool = False
        function_name = ""
        function_args = ""
        tool_call_id = -1
        try:
            response = API.send_message(prompt=prompt, doStream=True, toolMode=toolMode)
            if (response is not None):
                page.run_task(update_function)
                for chunk in response:
                    choice = chunk.choices[0]
                    if (choice.delta is not None):
                        if (choice.delta.tool_calls is not None):
                            runTool = True

                            for tool_call in choice.delta.tool_calls:
                                if (tool_call.function.name is not None):
                                    function_name = tool_call.function.name
                                if (tool_call.function.arguments is not None):
                                    function_args += tool_call.function.arguments
                                if (tool_call.id is not None):
                                    tool_call_id = tool_call.id


                        if (choice.delta.content is not None):
                            if (choice.delta.content == "<think>"):
                                addText = False
                                addReasonText = True
                                model_thinking = True
                                if (not thread_running):
                                    thread_running = True
                                    thinking_thread = threading.Thread(
                                        target=animate_thinking,
                                        args=("Thinking", label, page, update_function),
                                        daemon=True
                                    )
                                    thinking_thread.start()
                            elif (choice.delta.content == "</think>"):
                                reasoning_response += choice.delta.content
                                addText = True
                                addReasonText = False
                                model_thinking = False
                                if (thinking_thread is not None) and (thread_running):
                                    thinking_thread.join(timeout=1)
                                continue

                            if (addText):
                                full_response += choice.delta.content
                                if (not Settings.useTTS):
                                    label.value = f"**{Settings.username_AI}:** {full_response.strip()}"
                                    page.run_task(update_function)
                            if (addReasonText):
                                reasoning_response += choice.delta.content


                if (full_response.strip() != "") and (not runTool):
                    if (Settings.useTTS):
                        page.run_thread(Audio.speak, full_response)
                    label.value = f"**{Settings.username_AI}:** {full_response.strip()}"
                    page.run_task(update_function)
                    Settings.messages.append(create_message(role="assistant", text=full_response.strip()))
                    Settings.store_chat_history(chatName=Settings.chatName, messages=Settings.messages)
                    thinking = False
                    usrPrompt = ""
        except Exception as _e:
            traceback.print_exc()
            label.value = "GENERATION ERROR!"
            page.run_task(update_function)
            thinking = False


        if (runTool):
            assistantThinking = str(reasoning_response.strip()) + str(full_response.strip())

            assistantMessage = {
                "role": "assistant",
                "content": str(assistantThinking),  # or "" if you prefer to hide thinking
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": str(function_name),
                            "arguments": str(function_args)  # the raw string that was parsed
                        }
                    }
                ]
            }

            Settings.messages.append(assistantMessage)

            function_args = json.loads(function_args)
            # print(f"{function_name}(**{function_args})")

            function_response = run_toolCall(function_name, function_args, label, page, update_function)

            # function_response = eval(f"{function_name}(**{function_args})")
            # print(function_response)

            Settings.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": function_name,
                "content": str(function_response),
            })

            # print(Settings.messages)

    return True

def stop_animate_messageText():
    global think_thread_running, thinking_thread
    if (not think_thread_running) and (thinking_thread is not None):
        thinking_thread.join(timeout=1)

def animate_messageText(textString: str, label: ft.Markdown, page: ft.Page, update_function):
    global think_thread_running, thinking_thread
    stop_animate_messageText()
    if (not think_thread_running):
        think_thread_running = True
        thinking_thread = threading.Thread(
            target=animate_thinking,
            args=(textString, label, page, update_function),
            daemon=True
        )
        thinking_thread.start()

def animate_thinking(textString: str, label: ft.Markdown, page: ft.Page, update_function):
    global model_thinking
    dots = 0
    while model_thinking:
        label.value = f"**{Settings.username_AI}:** {textString}" + ("." * dots)
        page.run_task(update_function)
        dots = (dots + 1) % 4
        timeSleep(0.5)


def run_toolCall(functionName, args, label, page, update_function):
    thread_running = False
    thinking_thread = None
    result = None
    if (functionName == "send_searches"):
        label.value = f"**{Settings.username_AI}:** Searching The Web..."
        page.run_task(update_function)
        result = send_searches(args)
        label.value = f"**{Settings.username_AI}:** Checking Results..."
        page.run_task(update_function)
    elif (functionName == "check_previous_articles"):
        label.value = f"**{Settings.username_AI}:** Checking Previous Searches..."
        page.run_task(update_function)
        result = check_previous_articles()
        if (thinking_thread is not None) and (thread_running):
            thinking_thread.join(timeout=1)
    elif (functionName == "Weather.get_weather"):
        label.value = f"**{Settings.username_AI}:** Checking The Weather..."
        page.run_task(update_function)
        result = Weather.get_weather(args)
        if (thinking_thread is not None) and (thread_running):
            thinking_thread.join(timeout=1)

    return result

def send_searches(search_query):
    global usrPrompt
    for query in search_query:
        results = WebSearch.search(query)
        if (results is not None):
            update_embedding(results)
        else:
            return "SEARCH FAILED! INFORM USER THAT SEARCH IS UNAVAILABLE."

    emb_top_k = 4 if (Settings.ctxSize <= 8192) else 8
    embContext = get_context_from_embed(usrPrompt, top_k=emb_top_k, threshold=0.5)
    if (embContext is None):
        return "NO USABLE INFORMATION FOUND USING WEB SEARCH."
    else:
        return str("\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):\n") + str(embContext)


def check_previous_articles():
    global usrPrompt
    # Check if previous searches contain necessary information
    if (embeddings is not None):
        emb_top_k = 4 if (Settings.ctxSize <= 8192) else 8
        embContext = get_context_from_embed(usrPrompt, top_k=emb_top_k, threshold=0.7)
        if (embContext is not None):
            return "\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):" + str(embContext)
    else:
        return "NO INFORMATION USABLE. PERFORM WEB SEARCH FUNCTION CALL."
