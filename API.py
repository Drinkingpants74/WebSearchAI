import httpx
import json

import Settings

def get_models(api: str = Settings.apiPath):
    models = httpx.get(f"{api}/v1/models")
    modelList = json.loads(models.text)
    modelDict = []

    for model in modelList["data"]:
        modelDict.append(model["id"])

    return modelDict

def create_message(role: str, text: str):
    return {"role": role, "content": text}

def send_embedding(texts):
    response = httpx.post(
        url="http://127.0.0.1:3623/v1/embeddings",
        timeout=120.0,
        json={
            "model": "nomic-embed-text-v1.5.Q4_K_M.gguf",
            "input": texts,
        })
    response.raise_for_status()
    return response

def send_message(prompt: str, sysMessage: str = Settings.system_prompt_default, doStream: bool = True):
    # New /v1/responses backend. Too New for Llama.cpp
    # with httpx.stream(
    #     method="POST",
    #     # url=f"{Settings.apiPath}/v1/responses",
    #     timeout=120.0,
    #     json={
    #         "instructions": sysMessage, #Settings.system_prompt_default,
    #         "model": Settings.apiModelID,
    #         "input": Settings.messages,
    #         "stream": doStream
    #     }) as response:
    #         response.raise_for_status()
    #         for chunk in response.iter_lines():
    #             if chunk:
    #                 yield chunk

    with httpx.stream(
        method="POST",
        url=f"{Settings.apiPath}/v1/chat/completions",
        timeout=120.0,
        json={
            # "instructions": sysMessage, #Settings.system_prompt_default,
            "model": Settings.apiModelID,
            "messages": Settings.messages,
            "stream": doStream,
            "temperature": Settings.temperature,
            "top_p": Settings.top_P,
            "min_p": Settings.min_P,
            "repeat_penalty": Settings.penalty_repeat,
            "frequency_penalty": Settings.penalty_frequency,
            "seed": Settings.seed
        }) as response:
            response.raise_for_status()
            for chunk in response.iter_lines():
                if chunk:
                    yield chunk


    # return message
