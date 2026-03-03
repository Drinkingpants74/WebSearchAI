import png  # pypng library
import base64
import json
import zlib
import os

import Settings

# Character Card V3 Specs
class CardData():
    json = {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": "",
            "description": "",
            "tags": [],
            "creator": "",
            "character_version": "1.0.0",
            "mes_example": "",
            "extensions": {}, # Ignoring.
            "system_prompt": "", # Ignoring. Using Default System Prompt instead
            "post_history_instructions": "", # Ignoring. For Jailbreaking (unsupported)
            "first_mes": "",
            "alternate_greetings": [], # Array of Strings
            "personality": "",
            "scenario": "",
            "creator_notes": "", # User Information; Display on Hover?
            "character_book": None, # Ignoring.
            "assets": None, # Ignoring.
            "nickname": None, # Replaces default "name" if set
            "creator_notes_multilingual": None, # Ignoring. Only using default Creator Notes
            "source": None, # Ignoring.
            "group_only_greetings": [], # Array of Strings
            "creation_date": None, # Set to current UNIX Time in Seconds OR Do not change
            "modification_date": None, # Set to current UNIX Time in Seconds
        },
    }


character_system_prompt = None
saveAs = "PNG" # PNG or JSON
storeAs = "TEXT" # TEXT or ZTXT (Compressed)

# Use New V3 Spec to handle files (PNG & JSON)

def get_cardData(file_path: str):
    try:
        if (file_path.endswith(".json")):
            pass
        elif (file_path.endswith(".png")):
            with open(file_path, 'rb') as f:
                reader = png.Reader(file=f)
                for chunk_type, chunk_data in reader.chunks():
                    if chunk_type == b'tEXt':
                    # Split tEXt chunk: key\0value
                        parts = chunk_data.split(b'\x00', 1)
                        if len(parts) == 2:
                            key, value = parts
                            if key == b'chara':
                                # Decode base64 to UTF-8 string, then parse JSON
                                decoded_data = base64.b64decode(value).decode('utf-8')
                                metadata_json = json.loads(decoded_data)
                                return metadata_json
                    elif chunk_type == b'zTXt':
                        # Decompress with zlib
                        parts = chunk_data.split(b'\x00', 2)
                        if len(parts) == 3 and parts[1] == b'zlib':
                            compressed_value = parts[2]
                            decompressed = zlib.decompress(compressed_value)
                            key, value = decompressed.split(b'\x00', 1)
                            if key == b'chara':
                                decoded_data = base64.b64decode(value).decode('utf-8')
                                metadata_json = json.loads(decoded_data)
                                return metadata_json
            print("No 'chara' chunk found in the PNG.")
            return None
        else:
            print("Not a PNG or JSON file.")
            return None
    except Exception as e:
        print(f"Error processing the file: {e}")
        return None

def load_card(file_path: str):
    global character_system_prompt

    loaded_data = get_cardData(file_path)
    if (loaded_data is None):
        return None

    character_system_prompt = ""

    Settings.username_AI = loaded_data["data"]["name"]
    if ("description" in loaded_data["data"]) and (loaded_data["data"]["description"].strip() != ""):
        character_system_prompt += "\n\nDESCRIPTION:\n" + loaded_data["data"]["description"]
    if ("personality" in loaded_data["data"]) and (loaded_data["data"]["personality"].strip() != ""):
        character_system_prompt += "\n\nPERSONALITY:\n" + loaded_data["data"]["personality"]
    if ("scenario" in loaded_data["data"]) and (loaded_data["data"]["scenario"].strip() != ""):
        character_system_prompt += "\n\nSCENARIO:\n" + loaded_data["data"]["scenario"]


    for chunk in loaded_data["data"]:
        print(f"{chunk}")


def get_char_sysPrompt():
    if (Settings.card is None):
        return None

    cardDAT = Settings.card.json["data"]

    return f'{cardDAT["description"]}\n\n{cardDAT["personality"]}\n\n{cardDAT["scenario"]}\n\n{cardDAT["mes_example"]}'


def get_char_firstMessage():
    if (Settings.card is None):
        return None

    return Settings.card.json["data"]["first_mes"]

def get_char_name():
    if (Settings.card is None):
        return None

    cardDAT = Settings.card.json["data"]

    if (cardDAT["nickname"].strip() != ""):
        return cardDAT["nickname"]
    else:
        return cardDAT["name"]


def get_char_description():
    if (Settings.card is None):
        return None

    return Settings.card.json["data"]["first_mes"]

# Used to build Character Card Buttons
def get_characterInfo(file_path):
    """
    Returns - Name, Description
    """
    loaded_data = get_cardData(file_path)
    if (loaded_data is None):
        return "", ""

    # if (Settings.card is None):
    #     return "", ""

    # loaded_data = loaded

    character_blurb: str = ""
    # if ("character_version" in loaded_data["data"]) and (loaded_data["data"]["character_version"].strip() != ""):
    #     character_blurb += "V: " + loaded_data["data"]["character_version"] + " | "
    if ("creator_notes" in loaded_data["data"]) and (loaded_data["data"]["creator_notes"].strip() != ""):
        character_blurb += loaded_data["data"]["creator_notes"].split('\n')[0][:300]

    return str(loaded_data["data"]["name"]), character_blurb



def build_character_card(file_path, cardData: CardData, exportPath: str):
    global saveAs, storeAs
    if (saveAs == "JSON"):
        charJSON = json.dumps(cardData.json, ensure_ascii=False, separators=(',', ':'))

        with open(exportPath, 'w') as f:
            f.write(charJSON)

        if (os.path.exists(exportPath)):
            return True
        return False
    else:
        stored_info = False
        chunks = []
        charJSON = json.dumps(cardData.json, ensure_ascii=False, separators=(',', ':'))
        if (storeAs == "ZTXT"):
            charBYTES = charJSON.encode('utf-8')
            charCOMP = zlib.compress(charBYTES, level=9)
            charZTXT = b"chara\x00\x00" + charCOMP
            charCHUNK = (b'zTXt', charZTXT)
        else:
            char64 = base64.b64encode(charJSON.encode('utf-8')).decode('ascii')
            charTEXT = b"chara\x00" + char64.encode('ascii')
            charCHUNK = (b'tEXt', charTEXT)

        with open(file_path, 'rb') as f:
            reader = png.Reader(file=f)
            for chunk_type, chunk_data in reader.chunks():
                if (chunk_type == b'tEXt') or (chunk_type == b'zTXt'):
                    try:
                        parts = chunk_data.split(b'\x00', 1)
                        if len(parts) == 2:
                            key, value = parts
                            if key == b'chara':
                                chunks.append(charCHUNK)
                                stored_info = True
                    except Exception as _e:
                        pass
                elif chunk_type == b'IEND':
                    if (not stored_info):
                        chunks.append(charCHUNK)
                    chunks.append((chunk_type, chunk_data))
                else:
                    chunks.append((chunk_type, chunk_data))

        cardNameBITS = cardData.json["data"]["name"].strip().split(' ')
        cardName = ""
        if (len(cardNameBITS) > 1):
            for i in cardNameBITS:
                cardName += i + "_"
            cardName = cardName[:-1] + ".png"
        else:
            cardName = cardData.json["data"]["name"].strip()

        with open(exportPath, 'wb') as f:
            png.write_chunks(f, chunks)

        if (os.path.exists(exportPath)):
            return True
        return False



# cardData = CardData()
# cardData.json["data"]["name"] = "TEST CARD"

# build_character_card("src/Cards/cazmira_de_santis.png", cardData)

# print(get_cardData("src/Cards/TEST_CARD.png"))
