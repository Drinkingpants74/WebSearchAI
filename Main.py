import asyncio
import json
import LLM
import Settings
import flet as ft
import os
import sys
# import time
import Test

modelLoader = "none"

# MLX SUPPORT IS EXPERIMENTAL
if (sys.platform == "darwin"):
    import MLX
    Settings.doMLX = True

def main(page: ft.Page):
    Settings.load_settings()
    # page.window.icon = "icon.png" # In Progress
    page.title = "WebSearch AI"
    page.scroll = ft.ScrollMode.ADAPTIVE

    class Message:
        def __init__(self, user_name: str, text: str, message_type: str):
            self.user_name = user_name
            self.text = text
            self.message_type = message_type

    class ChatMessage(ft.Row):
        def __init__(self, message: Message):
            super().__init__()
            self.vertical_alignment = ft.CrossAxisAlignment.START
            self.controls = [
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.Colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                # self.get_avatar_image(user_name=message.user_name),
                #message.text
                ft.Markdown(value=self.clean_text(message.text), selectable=True, fit_content=True, width=page.width-100)
                # ft.Text(value=self.clean_text(message.text), selectable=True, overflow=ft.TextOverflow.VISIBLE,
                #         width=page.width-100, bgcolor=ft.Colors.TRANSPARENT)
            ]

        def clean_text(self, text: str):
            text = text.replace("{{char}}", Settings.username_AI)
            text = text.replace("{{user}}", Settings.userName)
            return text


        def get_initials(self, user_name: str):
            if user_name:
                if (len(user_name) <= 2):
                    return user_name
                else:
                    return user_name[:1].capitalize()
            else:
                return "Unknown"  # or any default value you prefer

        def get_avatar_color(self, user_name: str):
            colors_lookup = [
                ft.Colors.AMBER,
                ft.Colors.BLUE,
                ft.Colors.BROWN,
                ft.Colors.CYAN,
                ft.Colors.GREEN,
                ft.Colors.INDIGO,
                ft.Colors.LIME,
                ft.Colors.ORANGE,
                ft.Colors.PINK,
                ft.Colors.PURPLE,
                ft.Colors.RED,
                ft.Colors.TEAL,
                ft.Colors.YELLOW,
            ]
            return colors_lookup[hash(user_name) % len(colors_lookup)]

        def get_avatar_image(self, user_name: str):
            if (user_name != "AI"):
                return ft.CircleAvatar(
                    content=ft.Image(src=Settings.cardPath),
                    color=ft.Colors.TRANSPARENT,
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
            else:
                return ft.CircleAvatar(
                    content=ft.Text(self.get_initials(user_name)),
                    color=ft.Colors.WHITE,
                    bgcolor=self.get_avatar_color(user_name),
                )

    def _on_model_load_alert_close_pressed(e):
        modelLoadDLG.open = False
        modelPickerDLG.open = True
        page.update()

    def _on_load_model_pressed(e):
        global modelLoader
        # modelPickerDLG.open = False
        data = e.control.data
        modelLoader = data["Loader"]
        if (data["Loader"] == "GGUF"):
            if (not LLM.load_model(data["FileName"])):
                modelLoadDLG.title = ft.Text("Model Failed to Load!")
                modelLoadDLG.open = True
            else:
                modelPickerDLG.close_view(data["FileName"])
                open_searchBar("None")
                toggle_chatBox(True)
        elif (data["Loader"] == "MLX"):
            if (not MLX.load_model(data["FileName"])):
                modelLoadDLG.title = ft.Text("Model Failed to Load!")
                modelLoadDLG.open = True
            else:
                modelPickerDLG.close_view(data["FileName"])
                open_searchBar("None")
                toggle_chatBox(True)
        page.update()

    def _on_load_chat_pressed(e):
        chat.controls = []
        data = e.control.data
        filename = data["FileName"]

        if (filename == "Start New Chat"):
            Settings.chatName = "Unnamed Chat"
            LLM.messages.clear()
        else:
            with open(f"Chats/{filename}", "rt") as f:
                history = json.loads(f.read())
                LLM.messages = history
                for message in history:
                    if (message["role"] == "AI"):
                        responseChatMessage = ChatMessage(message=Message(Settings.username_AI, message["content"], message_type="chat_message"))
                        chat.controls.append(responseChatMessage)
                    elif (message["role"] == "user"):
                        userMessage = message["content"].split("\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):\n")
                        responseChatMessage = ChatMessage(message=Message(Settings.userName, userMessage[0], message_type="chat_message"))
                        chat.controls.append(responseChatMessage)

            chatPickerDLG.close_view(data["FileName"])
            open_searchBar("None")
            page.update()



    def toggle_chatBox(toggle: bool, message: str = ""):
        if (toggle):
            new_message.value = ""
            new_message.disabled = False
            submitButton.disabled = False
            new_message.focus()
        else:
            new_message.value = message
            new_message.disabled = True
            submitButton.disabled = True
        page.update()

    def send_message_click(e):
        if new_message.value != "":
            chat.controls.append(ChatMessage(Message(Settings.userName,new_message.value,message_type="chat_message")))

            prompt = new_message.value
            new_message.value = "Thinking..."
            new_message.disabled = True
            submitButton.disabled = True
            page.update()

            # new_message.value = ""
            # new_message.disabled = False
            # submitButton.disabled = False
            # new_message.focus()
            # page.update()


            try:
                # if modelLoader == "MLX":
                #     response = MLX.generate_response(prompt)
                # else:
                #     response = LLM.generate_response(prompt)

                # if (LLM.llm == None):
                #     print("No Model Loaded!")
                #     new_message.value = ""
                #     new_message.disabled = False
                #     submitButton.disabled = False
                #     new_message.focus()
                #     page.update()
                #     return

                responseChatMessage = ChatMessage(message=Message(Settings.username_AI, "", message_type="chat_message"))
                chat.controls.append(responseChatMessage)

                if modelLoader == "MLX":
                    response = MLX.generate_response(prompt, responseChatMessage, page)
                else:
                    response = LLM.generate_response(prompt, responseChatMessage, page)

                # response = LLM.generate_response(prompt, responseChatMessage, page)
                chatPickerDLG.bar_hint_text = Settings.chatName

                if response:
                    new_message.value = ""
                    new_message.disabled = False
                    submitButton.disabled = False
                    new_message.focus()
                    page.update()
            except Exception as ex:
                print("EXCPETION:", ex)


    def _on_search_button_pressed(e):
        if (Settings.toggle_search()):
            searchButton.icon = ft.Icons.SEARCH_ROUNDED
            searchButton.icon_color = ft.Colors.GREEN
        else:
            searchButton.icon = ft.Icons.SEARCH_OFF_ROUNDED
            searchButton.icon_color = ft.Colors.RED
        page.update()

    def _on_theme_button_pressed(e):
        if (Settings.theme == "Dark"):
            Settings.theme = "Light"
        else:
            Settings.theme = "Dark"
        update_theme()



    def update_theme():
        page.theme_mode = ft.ThemeMode.LIGHT if Settings.theme == "Light" else ft.ThemeMode.DARK
        page.window.bgcolor = Settings.lightBase if Settings.theme == "Light" else Settings.darkBase

        submitButton.icon_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
        settingsButton.icon_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
        closeSettingsButton.icon_color = "#cdcdcd" if Settings.theme == "Dark" else "#AA0000"
        quickUnloadModelButton.icon_color = "#BB0000" if Settings.theme == "Dark" else "#ff3333"

        themeSettingsButton.bgcolor = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
        themeSettingsButton.icon_color = Settings.lightBase if Settings.theme == "Light" else Settings.darkBase
        themeSettingsButton.color = Settings.lightBase if Settings.theme == "Light" else Settings.darkBase

        if (Settings.gpuLayers == -1):
            automaticGPULayerButton.bgcolor = "#009900" if Settings.theme == "Dark" else "#4dff4d"
            automaticGPULayerButton.icon_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            automaticGPULayerButton.color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            gpuLayerSlider.disabled = True
            gpuLayerSlider.active_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            gpuLayerSlider.thumb_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            gpuLayerSlider.overlay_color = "#cdcdcd44" if Settings.theme == "Dark" else "#1c1c1c44"
        else:
            automaticGPULayerButton.bgcolor = "#990000" if Settings.theme == "Dark" else "#ff4d4d"
            automaticGPULayerButton.icon_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            automaticGPULayerButton.color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            gpuLayerSlider.disabled = False
            gpuLayerSlider.value = Settings.gpuLayers
            gpuLayerSlider.active_color = "#9900cc" if Settings.theme == "Light" else "#00ffff"
            gpuLayerSlider.thumb_color = Settings.lightBase if Settings.theme == "Dark" else Settings.darkBase
            gpuLayerSlider.overlay_color = "#44cdcdcd" if Settings.theme == "Dark" else "#441c1c1c"

        page.update()


    def create_model_buttons(ifilename: str, ifile: str, loader: str):
        return ft.ListTile(title=ft.Text(ifilename), on_click=lambda e: _on_load_model_pressed(e), data={"FileName": ifile, "Loader": loader})

    def create_chat_buttons(ifilename: str, ifile: str, loader: str):
        return ft.ListTile(title=ft.Text(ifilename), on_click=lambda e: _on_load_chat_pressed(e), data={"FileName": ifile, "Loader": loader})

    def set_model_buttons():
        if (not os.path.isdir("Models/")):
            os.mkdir("Models/")
        modelButtons = []
        for file in os.listdir("Models/"):
            if (file.endswith(".gguf")):
                filename = file.replace(".gguf", "" ).replace("-", " ").replace("_", " ")
                modelButtons.append(create_model_buttons(filename, file, "GGUF"))
            elif (os.path.isdir("Models/" + file)) and (Settings.doMLX):
                for check in os.listdir("Models/" + file):
                    if (check.endswith(".safetensors")):
                        filename = file.replace("-", " ").replace("_", " ")
                        modelButtons.append(create_model_buttons(filename, file, "MLX"))
                        break
        return modelButtons

    def set_chat_buttons():
        if (not os.path.isdir("Chats/")):
            os.mkdir("Chats/")
        modelButtons = [create_chat_buttons("Start New Chat...", "None", "None")]
        for file in os.listdir("Chats/"):
            if (file.endswith(".json")):
                filename = file.replace(".json", "" ).replace("-", " ").replace("_", " ")
                modelButtons.append(create_chat_buttons(filename, file, "GGUF"))
        return modelButtons

    def on_window_resize(e):
        if (chat.controls != None) and (chat.controls != []):
            for i in chat.controls:
                print(i)
                if isinstance(i, ChatMessage):
                    print("CHAT MESSAGE")
                    for j in i.controls:
                        if isinstance(j, ft.Text):
                            j.width = page.width - 100
            page.update()

    def open_searchBar(searchBar: str):
        if (searchBar == "modelPickerDLG"):
            modelPickerDLG.visible = True
            chatPickerDLG.visible = False
            modelPickerDLG.open_view()
        elif (searchBar == "chatPickerDLG"):
            modelPickerDLG.visible = False
            chatPickerDLG.visible = True
            chatPickerDLG.open_view()
        else:
            modelPickerDLG.visible = True
            chatPickerDLG.visible = True

        page.update()

    def eject_model(e):
        print("EJECTING MODEL")
        LLM.unload_model(None)
        modelPickerDLG.close_view("Search Installed Models...")

    def _on_load_card_pressed(e):
        LLM.messages.clear()
        chat.controls.clear()
        if (Test.load_card(characterCardField.value)):
            LLM.messages.clear()
            LLM.messages.append(LLM.create_message("system", Settings.system_prompt_default))
            LLM.messages.append(LLM.create_message("user", ""))
            LLM.messages.append(LLM.create_message("AI", Settings.firstMessage))
            chat.controls.append(ChatMessage(message=Message(Settings.username_AI, Settings.firstMessage, message_type="chat_message")))

    def _on_automatic_gpu_pressed(e):
        print("SETTING GPU LAYERS")
        gpuLayerSlider.value = 0
        if (Settings.gpuLayers == -1):
            print("NON-AUTO")
            Settings.gpuLayers = 0
            gpuLayerSlider.disabled = False
        else:
            print("AUTO")
            Settings.gpuLayers = -1
            gpuLayerSlider.disabled = True
        # gpuLayerText.value = str(Settings.gpuLayers)
        update_theme()

    def _on_gpuSlider_changed(e):
        Settings.gpuLayers = int(gpuLayerSlider.value)
        # gpuLayerText.value = str(Settings.gpuLayers)
        if (LLM.llm != None):
            Settings.reload_model = True
        # page.update()

    def _on_model_settings_changed(e):
        if (temperatureField.value != Settings.temperature):
            Settings.temperature = temperatureField.value
            Settings.reload_model = True

        if (topKField.value):
            Settings.topK = topKField.value
            Settings.reload_model = True

        if (topPField.value):
            Settings.topP = topPField.value
            Settings.reload_model = True

        if (minPField.value):
            Settings.minP = minPField.value
            Settings.reload_model = True

        if (penRepeatField.value):
            Settings.penRepeat = penRepeatField.value
            Settings.reload_model = True

        if (penFrequencyField.value):
            Settings.penFrequency = penFrequencyField.value
            Settings.reload_model = True

        if (seedField.value):
            Settings.seed = seedField.value
            Settings.reload_model = True

    modelPickerDLG = ft.SearchBar(
        bar_hint_text="Search Installed Models...",
        on_tap=lambda e: open_searchBar("modelPickerDLG"),
        controls=set_model_buttons(),
        expand=True,
        visible=True,
    )

    chatPickerDLG = ft.SearchBar(
        bar_hint_text="Previous Chats",
        # on_tap=lambda e: chatPickerDLG.open_view(),
        on_tap=lambda e: open_searchBar("chatPickerDLG"),
        expand=True,
        visible=True,
        controls=set_chat_buttons()
    )

    modelLoadDLG = ft.AlertDialog(
        open=False, modal=True, bgcolor=ft.Colors.TRANSPARENT,
        content=ft.ElevatedButton(text="Close", on_click=_on_model_load_alert_close_pressed))

    chat = ft.ListView(
        expand=True,
        spacing=15,
        auto_scroll=True,
    )

    chat_container = ft.Container(
        content=chat,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT
        # width=page.width - 100,
    )

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        adaptive=True,
        on_submit=send_message_click,
    )

    submitButton = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        tooltip="Send message",
        on_click=send_message_click,
    )

    searchButton = ft.IconButton(
        icon=ft.Icons.SEARCH_OFF_ROUNDED,
        tooltip="Toggle Search",
        on_click=_on_search_button_pressed,
        icon_color=ft.Colors.RED
    )

    settingsButton = ft.IconButton(
        icon=ft.Icons.SETTINGS_OUTLINED,
        tooltip="Open Settings",
        on_click=lambda e: page.go("/Settings"),
    )

    closeSettingsButton = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_color="#AA0000",
        tooltip="Close",
        on_click=lambda e: page.go("/Chat"),
    )

    themeSettingsButton = ft.ElevatedButton(
        icon=ft.Icons.INVERT_COLORS,
        tooltip="Close",
        on_click=_on_theme_button_pressed,
        icon_color="#cdcdcd",
        text="Change Theme",
        bgcolor=Settings.darkBase,
    )

    unloadModelButton = ft.ElevatedButton(
        icon=ft.Icons.EJECT,
        tooltip="Remove Model from Memory",
        on_click=eject_model,
        icon_color="#cdcdcd",
        text="Unload Model",
        bgcolor=Settings.darkBase,
    )

    quickUnloadModelButton = ft.IconButton(
        icon=ft.Icons.EJECT_ROUNDED,
        tooltip="Remove Model from Memory",
        on_click=eject_model,
        icon_color="#cdcdcd",
        # text="Unload Model",
        # bgcolor=Settings.darkBase,
    )

    automaticGPULayerButton = ft.ElevatedButton(
        icon=ft.Icons.AUTOFPS_SELECT,
        tooltip="Disable Automatic GPU Layers",
        on_click=_on_automatic_gpu_pressed,
        icon_color="#cdcdcd",
        text="Automatic GPU Layers",
        bgcolor=Settings.darkBase,
    )

    gpuLayerSlider = ft.Slider(
        min=0,
        max=100,
        divisions=100,
        label="{value}",
        round=0,
        width=500,
        value=0,
        disabled=True,
        on_change_end=_on_gpuSlider_changed
    )

    # gpuLayerText = ft.Text(value=str(Settings.gpuLayers))


    temperatureField = ft.TextField(
        # label=str(Settings.temperature),
        value=str(Settings.temperature),
        hint_text="Temperature",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    topKField = ft.TextField(
        value=str(Settings.top_K),
        hint_text="Top K",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    topPField = ft.TextField(
        value=str(Settings.top_P),
        hint_text="Top P",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )
    minPField = ft.TextField(
        value=str(Settings.min_P),
        hint_text="Min P",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    penRepeatField = ft.TextField(
        value=str(Settings.penalty_repeat),
        hint_text="Repeat Penalty",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    penFrequencyField = ft.TextField(
        value=str(Settings.penalty_frequency),
        hint_text="Frequency Penalty",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    seedField = ft.TextField(
        value=str(Settings.seed),
        hint_text="Seed",
        tooltip="Random Seed: -1",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed
    )

    loadCharacterButton = ft.ElevatedButton(
        icon=ft.Icons.PERSON,
        tooltip="Load Character Card",
        # on_click=lambda e: page.go("/CharacterLoader"),
        on_click=_on_load_card_pressed,
        icon_color="#cdcdcd",
        text="Load Character",
        bgcolor=Settings.darkBase,
    )

    characterCardField = ft.TextField(
        value="",
        hint_text="Path to Character Card",
        tooltip="Use Full Path",
        adaptive=True,
    )

    appPages = {
        "/Chat": ft.View(
            "/Chat",
            [
                ft.Row(controls=[modelPickerDLG, quickUnloadModelButton, chatPickerDLG]),
                chat_container,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[settingsButton, new_message, searchButton, submitButton]
                ),
            ],
            bgcolor=ft.Colors.TRANSPARENT
        ),

        "/Loader": ft.View(
            "/Loader",
            [
                modelPickerDLG,
            ]
        ),

        "/Settings": ft.View(
        "/Settings",
        [
            closeSettingsButton, themeSettingsButton,
            ft.Row(controls=[loadCharacterButton, characterCardField]),
            ft.Row(controls=[automaticGPULayerButton, gpuLayerSlider]),
            ft.Row(controls=[ft.Text(value="Temperature: ", expand=True), temperatureField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Seed: ", expand=True), seedField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Top K: ", expand=True), topKField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Top P: ", expand=True), topPField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Min P: ", expand=True), minPField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Repeat Penalty: ", expand=True), penRepeatField], alignment=ft.MainAxisAlignment.START),
            ft.Row(controls=[ft.Text(value="Frequency Penalty: ", expand=True), penFrequencyField], alignment=ft.MainAxisAlignment.START),
                ],
            bgcolor=ft.Colors.TRANSPARENT
        ),

        "/CharacterLoader": ft.View(
        "/CharacterLoader",
        [
            # closeCharButton,
            ft.Text(value="NOT IMPLEMENTED YET", expand=True, text_align=ft.TextAlign.CENTER),
                ],
            bgcolor=ft.Colors.TRANSPARENT
        ),

    }


    def route_change(route):
        page.views.clear()
        page.views.append(appPages[route.route])
        if (Settings.reload_model):
            toggle_chatBox(False, "Loading Model...")
            LLM.load_model(Settings.loaded_model)
            toggle_chatBox(True, "")
        page.update()

    async def close_window(e):
        if (e.data == "close"):
            page.open(ft.AlertDialog(
                    open=True, modal=True, icon=ft.Icon(name=ft.Icons.WARNING, color="#FF0000"),
                    title="Closing Application...", content=ft.Text("Please Wait.\nUnloading Model..."),
                ))
            page.update()
            LLM.unload_model(None)
            Settings.save_settings()
            await asyncio.sleep(2)
            # time.sleep(2)
            page.window.destroy()


    page.on_resized = on_window_resize
    page.window.on_event = close_window
    page.window.prevent_close = True
    page.on_route_change = route_change
    page.go("/Chat")
    toggle_chatBox(False, "Select a Model to Load...")
    update_theme()

ft.app(target=main, view=ft.AppView.FLET_APP)