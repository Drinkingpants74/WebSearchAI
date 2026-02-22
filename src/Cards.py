import png  # pypng library
import base64
import json

import Settings

# Character Card V3 Specs
cardData = {
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
                        # Decompress with zlib (requires import zlib)
                        import zlib
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


# Used to build Character Card Buttons
def get_characterInfo(file_path: str):
    """
    Returns - Name, Description
    """
    loaded_data = get_cardData(file_path)
    if (loaded_data is None):
        return ""

    character_blurb: str = ""
    if ("character_version" in loaded_data["data"]) and (loaded_data["data"]["character_version"].strip() != ""):
        character_blurb += "V: " + loaded_data["data"]["character_version"]
    if ("creator_notes" in loaded_data["data"]) and (loaded_data["data"]["creator_notes"].strip() != ""):
        character_blurb += " | " + loaded_data["data"]["creator_notes"].split('\n')[0][:50]

    return str(loaded_data["data"]["name"]), character_blurb
