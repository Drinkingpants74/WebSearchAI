import json
import os.path

# User Settings
theme: str = "Dark"
userName: str = "Steve"
modelsPath: str = "Models/"
system_prompt_default: str = "You are a helpful AI assistant. You will answer all questions."

# Model Settings
gpuLayers: int = -1
ctxSize: int = 8192
batchSize: int = 512

# Chat Settings
temperature: float = 1.0
top_P: float = 0.95
top_K: float = 40
min_P: float = 0.05
penalty_repeat: float = 1.0
penalty_frequency: float = 1.0
seed: int = -1

# Misc
doSearch: bool = False
doMLX: bool = False
chatName: str = "Unnamed Chat"
loaded_model: str = "None"
reload_model: bool = False

# Colors
lightBase = "#cdcdcd"
darkBase = "#1c1c1c"

# Cards
cardPath = None
cardInfo = None
username_AI = "AI"
firstMessage = None

def load_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, \
        temperature, top_P, top_K, min_P, penalty_repeat, penalty_frequency, seed
    loadDict = None
    if (not os.path.isfile("settings.json")):
        save_settings()
    with open("settings.json", "r") as file:
        loadDict = json.load(file)

    if (loadDict is not None):
        theme = loadDict["THEME"]
        userName = loadDict["USERNAME"]
        modelsPath = loadDict["MODELS_PATH"]
        system_prompt_default = loadDict["SYSTEM_PROMPT"]

        # Model Settings
        gpuLayers = loadDict["GPU_LAYERS"]
        ctxSize = loadDict["CONTEXT"]
        batchSize = loadDict["BATCH_SIZE"]

        # Chat Settings
        temperature = loadDict["TEMPERATURE"]
        top_P = loadDict["TOP_P"]
        top_K = loadDict["TOP_K"]
        min_P = loadDict["MIN_P"]
        penalty_repeat = loadDict["PEN_REPEAT"]
        penalty_frequency = loadDict["PEN_FREQUENCY"]
        seed = loadDict["SEED"]
    pass


def save_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, temperature, top_P, top_K, min_P, penalty_repeat, penalty_frequency
    saveDict = {
        "THEME": theme,
        "USERNAME": userName,
        "MODELS_PATH": modelsPath,
        "SYSTEM_PROMPT": system_prompt_default,

        # Model Settings
        "GPU_LAYERS": gpuLayers,
        "CONTEXT": ctxSize,
        "BATCH_SIZE": batchSize,

        # Chat Settings
        "TEMPERATURE": temperature,
        "TOP_P": top_P,
        "TOP_K": top_K,
        "MIN_P": min_P,
        "PEN_REPEAT": penalty_repeat,
        "PEN_FREQUENCY": penalty_frequency,
        "SEED": seed,
    }

    with open("settings.json", "w") as settings_file:
        json.dump(saveDict, settings_file, indent=4)

    pass

def store_chat_history(chatName, messages) -> None:
    with open(f"Chats/{chatName}.json", "w") as chat_file:
        json.dump(messages, chat_file, indent=4)

def toggle_search() -> bool:
    global doSearch
    doSearch = not doSearch
    return doSearch
