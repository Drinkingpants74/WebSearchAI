import re
import sys
from datetime import datetime
import gc
import numpy as np
import subprocess
from platform import system as get_system
from time import sleep as timeSleep

import WebSearch
import Settings
import API

process = None

searchContext = None
embeddings = None
embedder = None
kw_model = None

def unload_embedder():
    global embedder, kw_model
    # embedder = None
    # kw_model = None
    if (embedder is not None):
        embedder.terminate()
        embedder.wait()
        gc.collect()

def load_embedder():
    global embedder, kw_model
    llamapath = "./Llama.cpp/llama-server"
    if (get_system() == "Windows"):
        llamapath += ".exe"
    embedder = subprocess.Popen([
        llamapath,
        '-m', 'nomic-embed-text-v1.5.Q4_K_M.gguf',
        '--port', '3623', '--embedding',
        '-ngl', '0', '-c', '4096',
        '-b', '256',
        #'--top-k', '40',
        #'-ctk', 'q8_0', '-ctv', 'q8_0', '-fa', 'on'
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )
    timeSleep(2)
    if (embedder.poll()):
        stderr_output = embedder.stderr.read().decode() if embedder.stderr else ""
        print(f"Llama.cpp backend failed to launch: {stderr_output}")
    # embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    # kw_model = KeyBERT(model=embedder)


def update_embedding(pages):
    # print(f"PAGES:\n{pages}")
    global embeddings, embedder

    print(f"Embedding {len(pages)} chunks")
    for i, page in enumerate(pages[:3]):  # Print first 3
        chunk = page if isinstance(page, str) else page.get("CHUNK", "")
        print(f"Chunk {i} length: {len(chunk)} chars, preview: {chunk[:100]}")

    MAX_CHARS = 1000
    toEmbed = [item["CHUNK"][:MAX_CHARS] for item in pages]
    # [item["CHUNK"] for item in pages]

    print("CHUNK")

    response = API.send_embedding(toEmbed)
    data = response.json()['data']
    emebedEncoded = [item["embedding"] for item in data]

    new_emb = np.array(emebedEncoded, dtype=np.float32)

    # new_emb = np.array([embedder.encode(dict["CHUNK"]) for dict in pages], dtype=np.float32)
    # new_emb = np.array([embedder.encode(dict["CHUNK"])["data"][0]["embedding"] for dict in pages], dtype=np.float32)
    new_emb = new_emb / np.linalg.norm(new_emb, axis=-1, keepdims=True)
    embeddings = new_emb if embeddings is None else np.vstack([embeddings, new_emb])


def get_context_from_embed(prompt, top_k, threshold):
    global embeddings, embedder
    if (embeddings is not None):
        response = API.send_embedding(prompt)
        data = response.json()['data']
        emebedEncoded = data[0]['embedding']

        q_emb = np.array(emebedEncoded, dtype=np.float32)

        # q_emb = np.array(embedder.encode(prompt), dtype=np.float32)
        # q_emb = np.array(embedder.encode(prompt)["data"][0]["embedding"], dtype=np.float32)
        q_emb = q_emb / np.linalg.norm(q_emb)
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
        # print("Chosen Context:", embContext)
        return embContext
    return None

def create_message(role: str, text: str):
    return {"role": role, "content": text}

def load_model(modelName):
    Settings.apiModelID = modelName
    if (not Settings.apiMode):
        launch_llama()

def unload_model():
    global process
    if (process is not None):
        process.terminate()
        process.wait()

def launch_llama():
    unload_model()
    global process
    llamapath = "./Llama.cpp/llama-server"
    if (get_system() == "Windows"):
        llamapath += ".exe"
    process = subprocess.Popen([
        llamapath,
        '-m', f"{Settings.modelsPath}{Settings.apiModelID}",
        '--port', '3774',
        '-ngl', str(Settings.gpuLayers),
        '-c', str(Settings.ctxSize),
        '-b', str(Settings.batchSize),
        '--top-k', str(Settings.top_K),
        '-ctk', 'q8_0', '-ctv', 'q8_0', '-fa', 'on'
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )
    timeSleep(2)
    if (process.poll()):
        stderr_output = process.stderr.read().decode() if process.stderr else ""
        print(f"Llama.cpp backend failed to launch: {stderr_output}")


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
    text_embed = np.array(text_response.json()['data'][0]['embedding'], dtype=np.float32)
    text_embed = text_embed / np.linalg.norm(text_embed)

    # Embed all candidates
    candidates_response = API.send_embedding(candidates)
    candidates_embeds = [item["embedding"] for item in candidates_response.json()['data']]
    candidates_embeds = np.array(candidates_embeds, dtype=np.float32)
    candidates_embeds = candidates_embeds / np.linalg.norm(candidates_embeds, axis=-1, keepdims=True)

    # Calculate similarity scores
    scores = np.dot(candidates_embeds, text_embed)

    # Get top K
    top_indices = np.argsort(scores)[-top_k:][::-1]
    keywords = [(candidates[i], scores[i]) for i in top_indices]

    return keywords


def generate_response(prompt: str, textSignal):
    global searchContext, embeddings, embedder, cancel_run, kw_model
    if Settings.apiModelID is None:
        textSignal.emit("No Model Loaded.")
        return None

    textSignal.emit(f"**{Settings.username_AI}:** Thinking...")

    if Settings.chatName == "Unnamed Chat":
        # keywords = kw_model.extract_keywords(
        #     prompt,
        #     keyphrase_ngram_range=(1, 5),
        #     stop_words='english',
        #     top_n=Settings.top_K,
        #     use_mmr=True,
        #     diversity=0.5
        # )

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

        # print("CHAT: ", chatNameText)

    if Settings.doSearch:
        # if (cancel_run):
        #     return None
        textSignal.emit(f"**{Settings.username_AI}:** Searching The Web...")

        continueSearch = True
        # Check if previous searches contain necessary information
        if (embeddings is not None):
            emb_top_k = 4 if (Settings.ctxSize <= 8192) else 8
            embContext = get_context_from_embed(prompt, top_k=emb_top_k, threshold=0.6)
            if (embContext is not None):
                continueSearch = False
                prompt += "\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):" + embContext

        if (continueSearch):
            searchSuccess = False
            searchCount = 0
            while not searchSuccess:
                # if (cancel_run):
                #     return None
                if searchCount >= 5:
                    searchSuccess = True
                    break

                searchKeywords = extract_keywords(prompt)
                # = kw_model.extract_keywords(
                #     prompt,
                #     keyphrase_ngram_range=(1, 5),
                #     stop_words='english',
                #     top_n=Settings.top_K,
                #     use_mmr=True,
                #     diversity=0.5
                # )

                if searchKeywords:
                    searchText = ' '.join(searchKeywords[0][0].split())  # Clean title case if needed
                else:
                    textSignal.emit(f"**{Settings.username_AI}:** Unable to Search. Please provide more context.")
                    searchSuccess = True
                    return None

                searchContext = WebSearch.search(searchText)

                if searchContext is not None:
                    doesAnswer = False
                    textSignal.emit(f"**{Settings.username_AI}:** Checking Results...")
                    update_embedding(searchContext)
                    emb_top_k = 4 if (Settings.ctxSize <= 8192) else 8
                    embContext = get_context_from_embed(prompt, top_k=emb_top_k, threshold=0.4)
                    if (embContext is not None):
                        doesAnswer = True

                    if (doesAnswer):
                        searchSuccess = True
                        prompt += str("\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):") + str(embContext)
                    else:
                        textSignal.emit(f"**{Settings.username_AI}:** Results Unsatisfactory. Searching Again...")
                        searchCount += 1
                else:
                    textSignal.emit(f"**{Settings.username_AI}:** Unable to Search. Check your Connection, or try again later.")
                    searchSuccess = True
                    return None
        else:
            textSignal.emit(f"**{Settings.username_AI}:** Checking Results...")


    Settings.messages.append(create_message(role="user", text=prompt))

    return API.send_message(prompt=prompt, doStream=True)
