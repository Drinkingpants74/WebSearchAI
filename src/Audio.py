from platform import system as get_system
import subprocess
from time import sleep as timeSleep
import gc
import flet as ft
import re


button_pressed = False
whisper = None

def load_whisper(userInput: ft.TextField, page: ft.Page, update_function):
    global button_pressed
    # button_pressed = not button_pressed
    if (button_pressed) and (whisper is None):
        userInput.value = "Starting STT Listener..."
        page.run_task(update_function)
        launch_whisper(userInput, page, update_function)

def launch_whisper(userInput: ft.TextField, page: ft.Page, update_function):
    global whisper, button_pressed
    llamapath = "./src/Whisper.cpp/whisper-stream"
    if (get_system() == "Windows"):
        llamapath += ".exe"
    whisper = subprocess.Popen([
        llamapath, '-m', 'src/Whisper.cpp/ggml-base.en.bin'
        #'--port', '9477',
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    timeSleep(2)
    if (whisper.poll()):
        stderr_output = whisper.stderr.read() if whisper.stderr else ""
        print(f"Whisper.cpp backend failed to launch: {stderr_output}")

    try:
        userInput.value = ""
        page.run_task(update_function)
        for line in whisper.stdout:
            if (button_pressed):
                cleaned = re.sub(r'\x1b\[[\d;]*[A-Za-z]', '', line)
                cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned)
                cleaned = cleaned.strip()
                if (not cleaned) or (re.match(r'^\[.*\]$', cleaned)):
                    continue
                else:
                    print(f"Transcribed: {line}")
                    userInput.value += cleaned + " "
                    page.run_task(update_function)

    except KeyboardInterrupt:
        stop_whisper()

def stop_whisper():
    global whisper
    if (whisper is not None):
        whisper.terminate()
        whisper.wait()
        gc.collect()
    pass


def speak(text: str):
    cleaned = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'https?://\S+', 'Provided Website', cleaned)
    cleaned = re.sub(r'^#+\s+', '', cleaned, flags=re.MULTILINE)
    print(cleaned)



    system = get_system()

    print(system)
    if (system == "Darwin"):
        subprocess.run([ 'say', cleaned ])



# testText = """Testing Text
# # Header 1
# ## Header 2
# https://testsite.com
# http://badsite.com
# ```python
# print("Hey there!")
# Should be gone too
# ```
# Print this.
# """
# speak(testText)
