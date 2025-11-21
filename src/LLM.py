import gc
import re
import sys
import flet as ft
import llama_cpp
from src import Settings
from src import WebSearch
import numpy as np


llm = None
messages = []
searchContext = None
embeddings = None
embedder = llama_cpp.Llama(
    model_path="all-minilm-l6-v2_q8_0.gguf",
    n_gpu_layers=0,
    n_ctx=516,
    seed=0,
    verbose=False,
    embedding=True
)


def unload_model(e):
    global llm
    if isinstance(llm, llama_cpp.Llama):
        llm.close()
    gc.collect()
    llm = None

def unload_embedder(e):
    global embedder
    embedder.close()
    gc.collect()
    embedder = None

def load_model(fileName: str) -> bool:
    global llm
    if llm is not None:
        unload_model(None)
    llm = llama_cpp.Llama(
        model_path=Settings.modelsPath + fileName,
        n_gpu_layers=Settings.gpuLayers,
        n_ctx=Settings.ctxSize,
        seed=Settings.seed,
        verbose=False,
        # Added to account for extra context from Search
        flash_attn=True,
        kv_overrides={ "cache_type_k": "q8_0", "cache_type_v": "q8_0" }
    )
    messages.clear()
    systemMessage = create_message("system", Settings.system_prompt_default)
    if (Settings.userInfo is not None):
        systemMessage["content"] += f"\nInformation about {Settings.userName}:\n"
        systemMessage["content"] += Settings.userInfo
    messages.append(systemMessage)
    if Settings.username_AI != "AI" and Settings.firstMessage is not None:
        messages.append(create_message("user", ""))
        Settings.chatHistory.append({"USER": Settings.userName, "ID": Settings.chatID, "Content": create_message("user", "")})
        messages.append(create_message("AI", Settings.firstMessage))
        Settings.chatHistory.append({"USER": Settings.username_AI, "ID": Settings.chatID, "Content": create_message("AI", Settings.firstMessage)})

    if llm is not None:
        Settings.loaded_model = fileName
        return True
    return False


def create_message(role: str, text: str):
    return {"role": role, "content": text}


async def _run_search(query):  # New async wrapper
    return await WebSearch.search(query)


def update_embedding(pages):
    print("Main Embedding...")
    global embeddings, embedder
    new_emb = np.array([embedder.create_embedding(dict["CHUNK"])["data"][0]["embedding"] for dict in pages], dtype=np.float32)
    new_emb = new_emb / np.linalg.norm(new_emb, axis=-1, keepdims=True)
    embeddings = new_emb if embeddings is None else np.vstack([embeddings, new_emb])
    print("Done.")

def get_context_from_embed(prompt):
    print("Question Embedding...")
    global embeddings, embedder
    if (embeddings is not None):
        print("Not None")
        q_emb = np.array(embedder.create_embedding(prompt)["data"][0]["embedding"], dtype=np.float32)
        q_emb = q_emb / np.linalg.norm(q_emb)
        scores = np.dot(embeddings, q_emb)
        best_index = np.argsort(scores)[-4:][::-1]
        embContext = "\n\n".join(WebSearch.previousInfo[id] for id in best_index)
        print("Chosen Context:", embContext)
        return embContext
    print("NONE")
    return ""


def generate_response(prompt: str, chatNode, page: ft.Page, chatContainer: ft.ListView):
    global llm, messages, searchContext, embeddings, embedder
    if llm is None:
        return None

    async def run_search_wrapper():
        return await WebSearch.search(
            searchText["choices"][0]["message"]["content"]
        )

    if Settings.chatName == "Unnamed Chat":
        chatNameText = llm.create_chat_completion(
            messages=[
                create_message("system",
                    "Generate short and unique names for chat sessions based on their content or context. Do not answer the prompt."
                    + "Generate only 1 sentence responses that are 5 words or less. Do not use titles."),
                create_message("user", "Summarize the following prompt:" + str(prompt)),
            ]
        )

        Settings.chatName = chatNameText["choices"][0]["message"]["content"]
        if (Settings.chatName[-1] == ".") or (Settings.chatName[-1] == "?"):
            Settings.chatName = Settings.chatName[:-1]
        if sys.platform == "win32":
            invalid_chars = r'[<>:"/\\|?*]+'
            Settings.chatName = re.sub(invalid_chars, "_", Settings.chatName)

    if Settings.doSearch:
        chatNode.controls[1].value = "Searching The Web..."
        page.update()

        continueSearch = True
        if (embeddings is not None):
            embContext = get_context_from_embed(prompt)
            # Check if previous searches contain necessary information
            doesAnswer = llm.create_chat_completion(seed=0, temperature=0.0, max_tokens=1, stop=["\n", " ", "."],
                messages=[
                    create_message("system", "Reply with only 'yes' or 'no' to the prompt."),
                    create_message("user", f"Does the following search results answer the prompt?\nPrompt: {prompt}\nSearch Results: {embContext}"),
                ]
            )
            continueSearch = not ("yes" in doesAnswer["choices"][0]["message"]["content"])


        if (continueSearch):
            searchSuccess = False
            searchCount = 0
            searchResults = ""
            while not searchSuccess:
                if searchCount >= 5:
                    searchSuccess = True
                    break
                searchText = llm.create_chat_completion(seed=-1,
                    messages=[
                        create_message("system", "Generate only 1 sentence responses."),
                        create_message("user", "Create a web search question for the following prompt:" + str(prompt)),
                    ]
                )

                try:
                    future = page.run_task(run_search_wrapper)
                    searchContext = future.result()
                except Exception as e:
                    pass

                if searchContext is not None:
                    chatNode.controls[1].value = "Checking Results..."
                    page.update()
                    update_embedding(searchContext)
                    # for url in searchContext:
                    #     searchResults += "\nSource: " + url + "\n" + searchContext[url]
                    embContext = get_context_from_embed(prompt)
                    # Check if previous searches contain necessary information
                    doesAnswer = llm.create_chat_completion(seed=0, temperature=0.0, max_tokens=1, stop=["\n", " ", "."],
                        messages=[
                            create_message("system", "Reply with only 'yes' or 'no' to the prompt."),
                            create_message("user", f"Does the following search results answer the prompt?\nPrompt: {prompt}\nSearch Results: {embContext}"),
                        ]
                    )

                    if (doesAnswer["choices"][0]["message"]["content"] == "yes"):
                        searchSuccess = True
                        prompt += "\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):" + searchResults
                    else:
                        chatNode.controls[1].value = "Results Unsatisfactory. Searching Again..."
                        page.update()
                        searchCount += 1
                else:
                    chatNode.controls[1].value = "Unable to Search. Check your Connection, or try again later."
                    page.update()
                    searchSuccess = True
                    return False
        else:
            chatNode.controls[1].value = "Checking Results..."
            page.update()


    messages.append(create_message(role="user", text=prompt))

    text = llm.create_chat_completion(
        messages=messages,
        temperature=Settings.temperature,
        top_p=Settings.top_P,
        min_p=Settings.min_P,
        top_k=Settings.top_K,
        seed=Settings.seed,
        repeat_penalty=Settings.penalty_repeat,
        frequency_penalty=Settings.penalty_frequency,
        stream=True,
    )
    full_response = ""
    count = 0
    for chunk in text:
        count += 1
        delta = chunk["choices"][0]["delta"].get("content", "")
        full_response += str(delta)
        if count >= 5:
            count = 0
            chatNode.controls[1].value = full_response
            page.update()
            chatContainer.scroll_to(-1)

    chatNode.controls[1].value = full_response.strip()
    page.update()
    Settings.chatHistory.append({"USER": Settings.username_AI , "ID": Settings.chatID, "Content": full_response.strip()})
    Settings.chatID += 1
    chatContainer.scroll_to(-1)
    messages.append(create_message(role="AI", text=full_response))
    Settings.store_chat_history(chatName=Settings.chatName, messages=messages)
    return True
