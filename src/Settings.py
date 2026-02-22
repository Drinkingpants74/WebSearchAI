import json
import random
import os.path
import Themes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# User Settings
theme: str = "Dark"
avatarColor = None
userName: str = "SETME#0074"
modelsPath: str = os.path.join(BASE_DIR, "Models")
system_prompt_default: str = "You are a helpful AI assistant. You will answer all questions."
userInfo = None
userTheme = Themes.default
userThemeName = "Default"

# Global Variables
windowWidth = 1024
windowHeight = 720
messages = []
messageID = -1
userBlacklist = []
# userWhitelist = []
firstPrompt = True

# Model Settings
gpuLayers: int = -1
ctxSize: int = 8192
batchSize: int = 512
temperature: float = 0.7
top_P: float = 0.90
top_K: int = 0
min_P: float = 0.0
penalty_repeat: float = 1.1
penalty_frequency: float = 0.0
seed: int = -1

# Misc
doSearch: bool = False
doToolCalls: bool = False
doMLX: bool = False
chatID = 0
editID = -1
chatName: str = "Unnamed Chat"
chatHistory = []
loaded_model: str = "None"
reload_model: bool = False

# Cards
cardsPath = "Cards/"
cardPath = None
cardInfo = None
username_AI = "AI"
firstMessage = None

# API
apiMode = False
apiPath = "http://127.0.0.1:3774"
apiKey = ""
apiModelID = "none"

embedderAPIPath = "http://127.0.0.1:3623"
embedderModelID = "nomic-embed-text-v1.5.Q4_K_M.gguf"

useTTS = False

# useSTT = False
# whisperAPIMode = False
# whisperAPIPath = "http://127.0.0.1:9477"
# whisperModelID = "base.en"

# Support for Keyboard Control
keyboard_shortcuts = {
    "Settings": "F1",
    "Send Message": "F2",
    "Toggle STT": "F5",
    "Toggle Search": "F4",
    # "Settings": "F1",
}

def set_avatar_color() -> str:
    return random.choice(["#FFA500", "#0000FF", "#964B00", "#00FFFF", "#008000", "#4B0082", "#00FF00", "#FFA500",
        "#FFC0CB", "#800080", "#FF0000", "#008080", "#FFFF00"])

def invert_hex_color(hex_color):
    # Remove the '#' character if it exists
    if (hex_color[0] == "#"):
        hex_color = hex_color[1:]

    # Split the hex code into its components
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Invert each component
    inverted_r = 255 - r
    inverted_g = 255 - g
    inverted_b = 255 - b

    # Convert the inverted components back to hex and combine them
    inverted_hex = f"{inverted_r:02x}{inverted_g:02x}{inverted_b:02x}"

    return f"#{inverted_hex}"

def load_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, temperature, \
            top_P, top_K, min_P, penalty_repeat, penalty_frequency, seed, avatarColor, userInfo, userTheme, userThemeName, \
            userBlacklist, apiPath, apiKey, windowWidth, windowHeight, embedderAPIPath, embedderModelID
    loadDict = None
    if not os.path.isfile("src/settings.json"):
        avatarColor = set_avatar_color()
        save_settings()
    with open("src/settings.json", "r") as file:
        loadDict = json.load(file)

    if loadDict is not None:
        if "THEME" in loadDict.keys():
            theme = loadDict["THEME"]
        if "AVATAR" in loadDict.keys():
            avatarColor = loadDict["AVATAR"] if loadDict["AVATAR"] != "NULL" else set_avatar_color()
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

        if "BLACKLIST" in loadDict.keys():
            userBlacklist = loadDict["BLACKLIST"]
        if "APIPATH" in loadDict.keys():
            apiPath = loadDict["APIPATH"]
        if "APIKEY" in loadDict.keys():
            apiKey = loadDict["APIKEY"]
        if "EMBEDAPIPATH" in loadDict.keys():
            embedderAPIPath = loadDict["EMBEDAPIPATH"]
        if "EMBEDMODEL" in loadDict.keys():
            embedderModelID = loadDict["EMBEDMODEL"]
        if "WINDOWWIDTH" in loadDict.keys():
            windowWidth = loadDict["WINDOWWIDTH"]
        if "WINDOWHEIGHT" in loadDict.keys():
            windowHeight = loadDict["WINDOWHEIGHT"]




def save_settings() -> None:
    global theme, userName, modelsPath, system_prompt_default, gpuLayers, ctxSize, batchSize, temperature, \
            top_P, top_K, min_P, penalty_repeat, penalty_frequency, seed, avatarColor, userInfo, userBlacklist, \
            apiPath, apiKey, windowWidth, windowHeight, embedderAPIPath
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
        "SEED": seed,
        "BLACKLIST": userBlacklist,
        "APIPATH": apiPath,
        "APIKEY": apiKey,
        "EMBEDAPIPATH": embedderAPIPath,
        "EMBEDMODEL": embedderModelID,
        "WINDOWWIDTH": windowWidth,
        "WINDOWHEIGHT": windowHeight
    }

    with open(os.path.join(BASE_DIR, "settings.json"), "w") as settings_file:
        json.dump(saveDict, settings_file, indent=4)

    pass


def store_chat_history(chatName, messages) -> None:
    with open(f"{os.path.join(BASE_DIR, "Chats", f"{chatName}.json")}", "w") as chat_file:
        json.dump(messages, chat_file, indent=4)

def toggle_search() -> bool:
    global doSearch
    doSearch = not doSearch
    return doSearch
