import httpx
import json
from openai import OpenAI

import Settings

client = None
embedder = None

def cleanup():
    global client, embedder
    if (client is not None):
        client.close()
    if (embedder is not None):
        embedder.close()

def get_authorized():
    global client
    apiKey = "sk-no-key-required"
    if (Settings.apiKey.strip() != "") and (Settings.apiMode):
        apiKey = Settings.apiKey
    client = OpenAI(
        base_url=f"{Settings.apiPath}/v1",
        api_key=apiKey,
        timeout=120.0
    )

def set_embedder():
    global embedder
    embedder = OpenAI(
        base_url=f"{Settings.embedderAPIPath}/v1",
        api_key="sk-no-key-required",
        timeout=120.0,
    )


def get_models(api: str = "Default"):
    if (api == "Default"):
        api = Settings.apiPath
    models = httpx.get(f"{api}/v1/models")
    modelList = json.loads(models.text)
    modelDict = []

    for model in modelList["data"]:
        modelDict.append(model["id"])

    return modelDict

def get_models_openAI():
    global client
    if (client is not None):
        print(client.models.list())
    pass

def create_message(role: str, text: str):
    return {"role": role, "content": text}

def send_whisper():

    pass

def send_embedding(texts):
    global embedder
    if (embedder is not None):
        # print(embedder.base_url)
        response = embedder.embeddings.create(
            model=f"{Settings.embedderModelID}",
            input=texts,
            extra_body={
                "top_k": Settings.top_K,
                "batch_size": Settings.batchSize
            }
        )
        return response
    return None

def send_message(prompt: str, sysMessage: str = Settings.system_prompt_default, doStream: bool = True):
    pass
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

    # headerArgs = None

    # if (Settings.apiKey.strip() != "") and (Settings.apiMode):
    #     headerArgs = {
    #         "Authorization": f"Bearer {Settings.apiKey}"
    #     }

    # with httpx.stream(
    #     method="POST",
    #     url=f"{Settings.apiPath}/v1/chat/completions",
    #     timeout=120.0,
    #     headers=headerArgs,
    #     json={
    #         # "instructions": sysMessage, #Settings.system_prompt_default,
    #         "model": Settings.apiModelID,
    #         "messages": Settings.messages,
    #         "stream": doStream,
    #         "temperature": Settings.temperature,
    #         "top_p": Settings.top_P,
    #         "min_p": Settings.min_P,
    #         "repeat_penalty": Settings.penalty_repeat,
    #         "frequency_penalty": Settings.penalty_frequency,
    #         "seed": Settings.seed
    #     }) as response:
    #         response.raise_for_status()
    #         for chunk in response.iter_lines():
    #             if chunk:
    #                 yield chunk


    # return message

    # Open AI Conversion
    global client
    if (client is not None):
        # print("SENDING MESSAGE")
        response = client.chat.completions.create(
            model=Settings.apiModelID,
            messages=Settings.messages,
            stream=True,
            temperature=Settings.temperature,
            top_p=Settings.top_P,
            frequency_penalty=Settings.penalty_frequency,
            seed=int(Settings.seed),
            extra_body={
                "min_p": Settings.min_P,
                "top_k": Settings.top_K,
                "repeat_penalty": Settings.penalty_repeat,
                "batch_size": Settings.batchSize
            }
        )
        return response
