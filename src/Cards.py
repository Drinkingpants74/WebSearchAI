import png  # pypng library
import base64
import json

from src import Settings

def extract_character_card_metadata(png_path):
    try:
        # Open the PNG file as binary
        with open(png_path, 'rb') as f:
            reader = png.Reader(file=f)
            # Iterate through all chunks
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
                # Optional: Handle zTXt (compressed tEXt) if your file uses it
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
    except Exception as e:
        print(f"Error processing the file: {e}")
        return None

def load_card(png_path):
    metadata = extract_character_card_metadata(png_path)
    if metadata:
        # print(f"Character card metadata:")
        print(json.dumps(metadata, indent=2))  # Pretty-print the metadata
        Settings.cardInfo = metadata
        Settings.system_prompt_default = metadata["description"] + "\n" + metadata["personality"]
        Settings.username_AI = metadata["name"]
        Settings.firstMessage = metadata["first_mes"]
        print(Settings.system_prompt_default)
        return True
    else:
        print("Debug: No character card metadata found in the PNG.")
        return False

#Example usage
# png_path = "cazmira_de_santis.png"
# metadata = extract_character_card_metadata(png_path)
# if metadata:
#     print(f"Character card metadata:")
#     print(json.dumps(metadata, indent=2))  # Pretty-print the metadata
#     Settings.cardInfo = metadata
#     Settings.system_prompt_default = metadata["description"] + "\n" + metadata["personality"]
# else:
#     # Debug: Print all text chunks to inspect
#     print("Debug: All text chunks:")
#     with open(png_path, 'rb') as f:
#         reader = png.Reader(file=f)
#         for chunk_type, chunk_data in reader.chunks():
#             if chunk_type in (b'tEXt', b'zTXt', b'iTXt'):
#                 parts = chunk_data.split(b'\x00', 1)
#                 if len(parts) == 2:
#                     key, value = parts
#                     print(f"  Key: {key.decode('ascii', errors='ignore')}, Value preview: {value[:50]}...")
