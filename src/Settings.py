import json
import os.path
from src import Themes

# User Settings
theme: str = "Dark"
avatarColor = None
userName: str = "SETME#0074"
modelsPath: str = "Models/"
system_prompt_default: str = "You are a helpful AI assistant. You will answer all questions."
userInfo = None
userTheme = Themes.default
userThemeName = "Default"

# Model Settings
gpuLayers: int = -1
ctxSize: int = 8192
batchSize: int = 512

# Chat Settings
temperature: float = 1.0
top_P: float = 0.95
top_K: int = 40
min_P: float = 0.05
penalty_repeat: float = 1.0
penalty_frequency: float = 1.0
seed: int = -1

# Misc
doSearch: bool = False
doMLX: bool = False
chatID = 0
editID = -1
chatName: str = "Unnamed Chat"
chatHistory = []
loaded_model: str = "None"
reload_model: bool = False

# Cards
cardPath = None
cardInfo = None
username_AI = "AI"
firstMessage = None

def load_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, temperature, \
            top_P, top_K, min_P, penalty_repeat, penalty_frequency, seed, avatarColor, userInfo, userTheme, userThemeName
    loadDict = None
    if not os.path.isfile("settings.json"):
        save_settings()
    with open("settings.json", "r") as file:
        loadDict = json.load(file)

    if loadDict is not None:
        if "THEME" in loadDict.keys():
            theme = loadDict["THEME"]
        if "AVATAR" in loadDict.keys():
            avatarColor = loadDict["AVATAR"] if loadDict["AVATAR"] != "NULL" else None
        if "USERNAME" in loadDict.keys():
            userName = loadDict["USERNAME"]
        if "MODELS_PATH" in loadDict.keys():
            modelsPath = loadDict["MODELS_PATH"]
        if "SYSTEM_PROMPT" in loadDict.keys():
            system_prompt_default = loadDict["SYSTEM_PROMPT"]
        if "USERINFO" in loadDict.keys():
            userInfo = loadDict["USERINFO"] if loadDict["USERINFO"] != "NULL" else None
        if "USERTHEME" in loadDict.keys():
            userThemeName = loadDict["USERTHEME"]
            userTheme = Themes.list[userThemeName]

        # Model Settings
        if "GPU_LAYERS" in loadDict.keys():
            gpuLayers = loadDict["GPU_LAYERS"]
        if "CONTEXT" in loadDict.keys():
            ctxSize = loadDict["CONTEXT"]
        if "BATCH_SIZE" in loadDict.keys():
            batchSize = loadDict["BATCH_SIZE"]

        # Chat Settings
        if "TEMPERATURE" in loadDict.keys():
            temperature = loadDict["TEMPERATURE"]
        if "TOP_P" in loadDict.keys():
            top_P = loadDict["TOP_P"]
        if "TOP_K" in loadDict.keys():
            top_K = loadDict["TOP_K"]
        if "MIN_P" in loadDict.keys():
            min_P = loadDict["MIN_P"]
        if "PEN_REPEAT" in loadDict.keys():
            penalty_repeat = loadDict["PEN_REPEAT"]
        if "PEN_FREQUENCY" in loadDict.keys():
            penalty_frequency = loadDict["PEN_FREQUENCY"]
        if "SEED" in loadDict.keys():
            seed = loadDict["SEED"]
    pass


def save_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, temperature, \
            top_P, top_K, min_P, penalty_repeat, penalty_frequency, seed, avatarColor, userInfo
    saveDict = {
        "THEME": theme,
        "USERNAME": userName,
        "AVATAR": avatarColor if avatarColor is not None else "NULL",
        "MODELS_PATH": modelsPath,
        "SYSTEM_PROMPT": system_prompt_default,
        "USERINFO": userInfo if userInfo is not None else "NULL",
        "USERTHEME": userThemeName,
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
        "SEED": seed
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
