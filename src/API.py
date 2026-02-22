from typing import Iterable
import httpx
import json
from openai import Omit, OpenAI
from openai.types.chat import ChatCompletionToolChoiceOptionParam, ChatCompletionToolUnionParam
from datetime import datetime

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

def check_toolCalling():
    Settings.doToolCalls = False
    response = client.chat.completions.create(
        model=Settings.apiModelID,
        messages=[{"role": "user", "content": "Make a tool call to use the 'enable_toolCalls' function."}],
        stream=False,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "enable_toolCalls",
                    "description": "Enable Tool Calling if you support it",
                }
            },
        ],
        tool_choice="required",
    )

    if (response is not None):
        choice = response.choices[0].message

        for tool_call in choice.tool_calls:
            # print(tool_call)
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            result = eval(f"{function_name}(**{function_args})")
            return result
    return False

def enable_toolCalls():
    # print("TOOLS SUPPORTED!")
    Settings.doToolCalls = True
    return True

def create_chatName(messages):
    global client
    if (client is not None):
        response = client.chat.completions.create(
            model=Settings.apiModelID,
            messages=messages,
            stream=False,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "name_chat_toolCall",
                        "description": "Sets the name of the chat",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "chat_name": {
                                    "type": "string",
                                    "description": "A short name for the chat based on the initial prompt"
                                },
                            },
                            "required": ["chat_name"]
                        }
                    }
                },
            ],
            tool_choice="required",
        )

        if (response is not None):
            choice = response.choices[0].message

            # print("CHECKING TOOLS")
            for tool_call in choice.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                eval(f"{function_name}(**{function_args})")
                # print(function_response)


def name_chat_toolCall(chatName):
    Settings.chatName = datetime.now().strftime("%Y_%m_%d_%H%M_|") + str(chatName)


def set_embedder():
    global embedder
    embedder = OpenAI(
        base_url=f"{Settings.embedderAPIPath}/v1",
        api_key="sk-no-key-required",
        timeout=120.0,
    )


def get_models():
    global client
    modelDict = []
    if (client is not None):
        for model in client.models.list():
            modelDict.append(model.id)

    return modelDict

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

def get_availableTools() -> Omit | Iterable[ChatCompletionToolUnionParam]:
    availableTools: Iterable = []
    if (Settings.doSearch):
        getWeatherTool: ChatCompletionToolUnionParam = {
            "type": "function",
            "function": {
                "name": "Weather.get_weather",
                "description": "Retrieves realtime weather data from an API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The Temperature Unit for the location, in the format used by the location e.g. Texas = fahrenheit, Berlin = celsius"
                        }
                    },
                    "required": ["location", "unit"]
                }
            }
        }
        previousSearchesTool: ChatCompletionToolUnionParam = {
            "type": "function",
            "function": {
                "name": "check_previous_articles",
                "description": "Uses an Embedder Model to determine if there is useful information in previous searches.",
            }
        }
        newSearchTool: ChatCompletionToolUnionParam = {
            "type": "function",
            "function": {
                "name": "send_searches",
                "description": "Searches the Internet to provide updated information on topics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "A list of search queries e.g. baseball opening day 2026"
                        },
                    },
                    "required": ["search_query"]
                }
            }
        }

        availableTools.extend([getWeatherTool, newSearchTool])

        if (not Settings.firstPrompt):
            availableTools.extend(previousSearchesTool)


    if (len(availableTools) > 0):
        return availableTools
    else:
        return Omit()


def send_message(prompt: str, sysMessage: str = Settings.system_prompt_default, doStream: bool = True, toolMode: ChatCompletionToolChoiceOptionParam = "auto"):
    """
    Arguments:
        prompt: User Prompt\n
        sysMessage: System Message - Default: Settings.system_prompt_default\n
        doStream: Enable Streaming Responses - Default: True\n
        toolMode:
            "none" - Tool Calling Disabled\n
            "required" - Tool Calling Always Occurs\n
            "auto" - Tool Calling Used as Necessary\n
    """
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

    availableTools = get_availableTools()

    # Open AI Conversion
    global client
    if (client is not None):
        # print("SENDING MESSAGE")
        response = client.chat.completions.create(
            model=Settings.apiModelID,
            messages=Settings.messages,
            stream=doStream,
            temperature=Settings.temperature,
            top_p=Settings.top_P,
            frequency_penalty=Settings.penalty_frequency,
            seed=int(Settings.seed),
            tools=availableTools,
            tool_choice=toolMode,
            extra_body={
                "min_p": Settings.min_P,
                "top_k": Settings.top_K,
                "repeat_penalty": Settings.penalty_repeat,
                "batch_size": Settings.batchSize
            }
        )
        return response
