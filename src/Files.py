# RAG, Code File & Vision Support

import os

def load_file(path: str):
    if (os.path.exists(path)):
        with open(path, "r") as file:
            document = "" + file.read()
            return document
    return None
