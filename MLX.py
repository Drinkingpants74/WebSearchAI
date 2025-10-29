#############################
# MLX Support is DISABLED.  #
# It does not support ANY   #
# current features built    #
# in this version of the    #
# WebSearchAI Application   #
#############################

import flet as ft
import mlx_lm as mlx
import mlx.core as mx
from mlx_lm.sample_utils import make_logits_processors, make_sampler

import LLM
import WebSearch
import Settings
import sys, re, gc
import datetime

model = None
tokenizer = None
sampler = None
messages = []
searchContext = None

def unload_model(e):
    global model, tokenizer, sampler
    if (model is not None) or (tokenizer is not None) or (sampler is not None):
        del model
        del tokenizer
        del sampler
    gc.collect()
    mx.metal.clear_cache()
    model = None
    tokenizer = None
    sampler = None

def load_model(fileName: str) -> bool:
    global model, tokenizer, sampler
    if (model is not None) or (tokenizer is not None) or (LLM.llm is not None):
        model = None
        tokenizer = None
        LLM.unload_model(None)
    model, tokenizer = mlx.load("Models/" + fileName)
    sampler = make_sampler(top_k=Settings.top_K, top_p=Settings.top_P, min_p=Settings.min_P, temp=Settings.temperature)
    if (model is None) or (tokenizer is None):
        return False
    return True

def create_message(role: str, text: str):
    return {"role": role, "content": text}

async def _run_search(query):  # New async wrapper
    return await WebSearch.search(query)


def generate_response(prompt: str, chatNode, page: ft.Page):
    global model, tokenizer, messages, searchContext
    if (model is None) or (tokenizer is None):
        return None


    if (Settings.chatName == "Unnamed Chat"):
        # chatNameText = mlx.generate(model=model, tokenizer=tokenizer, messages=[create_message("system",
        #                                         "Generate short and unique names for chat sessions based on their content or context. Do not answer the prompt." +
        #                                                                    "Generate only 1 sentence responses that are 5 words or less. Do not use titles."),
        #                                      create_message("user",
        #                                     "Summarize the following prompt:" + str(prompt))
        #                                      ])


        # Settings.chatName = chatNameText
        # if (Settings.chatName[-1] == ".") or (Settings.chatName[-1] == "?"):
        #     Settings.chatName = Settings.chatName[:-1]
        # if (sys.platform == "win32"):
        #     invalid_chars = r'[<>:"/\\|?*]+'
        #     Settings.chatName = re.sub(invalid_chars, '_', Settings.chatName)
        Settings.chatName = "MLX_Test_Chat_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    if (Settings.doSearch):
        print("SEARCHING")
        chatNode.controls[1].value = "Searching The Web..."
        page.update()
        tokenizer.apply_chat_template(conversation=[create_message("system", "Generate only 1 sentence responses."),
                                                create_message("user", "Create a web search question for the following prompt:"+str(prompt))
                                                ],
                                        add_generation_prompt=True)
        searchText = mlx.generate(model=model, tokenizer=tokenizer, sampler=sampler, prompt=prompt)

        print("Search Text:", searchText)

        async def run_search_wrapper():
            return await WebSearch.search(searchText)

        try:
            # future = page.run_task(WebSearch.search(searchText["choices"][0]["message"]["content"]))
            future = page.run_task(run_search_wrapper)
            searchContext = future.result()
        except Exception as e:
            print(e)

        if (searchContext != None):
            print("RESULTS FOUND")
            chatNode.controls[1].value = "Checking Results..."
            page.update()
            prompt += "\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):"
            for url in searchContext:
                prompt += "\nSource: " + url + "\n" + searchContext[url]

    messages.append(create_message(role="user", text=prompt))

    tokenizer.apply_chat_template(conversation=messages, add_generation_prompt=True)

    full_response = ""
    for chunk in mlx.stream_generate(model=model, tokenizer=tokenizer, sampler=sampler, prompt=prompt):
        delta = chunk.text
        full_response += str(delta)
        chatNode.controls[1].value = full_response
        page.update()

    messages.append(create_message(role="AI", text=full_response))
    Settings.store_chat_history(chatName=Settings.chatName, messages=messages)
    return True
