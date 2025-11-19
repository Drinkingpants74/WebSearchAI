# import asyncio
import json
import os
# import sys
from pathlib import Path
import flet as ft
from markdown import markdown

import LLM
import Settings
# import time
import Cards
import Themes

modelLoader = "none"

# Disabling MLX support for now
# Once LLM is more robust, I'll look at re-adding MLX

# MLX SUPPORT IS EXPERIMENTAL
# if sys.platform == "darwin":
#     import MLX
#     Settings.doMLX = True


def main(page: ft.Page):
    Settings.load_settings()
    # page.window.icon = "icon.png" # In Progress
    page.title = "WebSearch AI"
    page.scroll = ft.ScrollMode.ADAPTIVE
    # page.bgcolor = ft.Colors.TRANSPARENT

    class Message:
        def __init__(self, user_name: str, text: str, message_type: str):
            self.user_name = user_name
            self.text = text
            self.message_type = message_type

    class ChatMessage(ft.Row):
        def __init__(self, message: Message):
            super().__init__()
            self.vertical_alignment = ft.CrossAxisAlignment.START
            if (message.user_name == Settings.userName):
                self.controls.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    tooltip="Edit Message",
                    on_click=lambda e: edit_text(e),
                    data=Settings.chatID,
                    icon_color=Settings.userTheme[Settings.theme]["Icon"]
                ))
            self.controls.append(ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ))

            self.controls.append(ft.Markdown(
                value=self.clean_text(message.text),
                selectable=True,
                fit_content=True,
                width=page.width - 150,
                soft_line_break=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                md_style_sheet=Themes.build_md_sheet(),
            ))

        def clean_text(self, text: str):
            text = text.replace("{{char}}", Settings.username_AI)
            text = text.replace("{{user}}", Settings.userName)
            return text

        def get_initials(self, user_name: str):
            if user_name:
                if len(user_name) <= 2:
                    return user_name
                else:
                    return user_name[:1].capitalize()
            else:
                return "User"  # or any default value you prefer

        def get_avatar_color(self, user_name: str):
            if Settings.avatarColor is None:
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
                Settings.avatarColor = colors_lookup[hash(user_name) % len(colors_lookup)]
                # return colors_lookup[hash(user_name) % len(colors_lookup)]
            return Settings.avatarColor

        def get_avatar_image(self, user_name: str):
            if user_name != "AI":
                return (
                    ft.CircleAvatar(
                        content=ft.Image(src=Settings.cardPath),
                        color=ft.Colors.TRANSPARENT,
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                )
            else:
                return ft.CircleAvatar(
                    content=ft.Text(self.get_initials(user_name)),
                    color=ft.Colors.WHITE,
                    bgcolor=self.get_avatar_color(user_name),
                )

    def join_chat_click(e):
        if not firstRunUsername.value:
            firstRunUsername.error_text = "Name cannot be blank!"
            firstRunUsername.update()
        else:
            Settings.userName = firstRunUsername.value
            Settings.save_settings()
            firstRunDLG.open = False
            new_message.prefix = ft.Text(f"{Settings.userName}: ")
            page.update()

    def _on_load_model_pressed(e):
        global modelLoader
        data = e.control.data
        modelLoader = data["Loader"]
        if data["Loader"] == "GGUF":
            modelPickerDLG.close_view(data["FileName"])
            if LLM.load_model(data["FileName"]):
                toggle_chatBox(True)
            else:
                modelPickerDLG.close_view("Model Failed to Load")
        # elif data["Loader"] == "MLX":
        #     if MLX.load_model(data["FileName"]):
        #         modelPickerDLG.close_view(data["FileName"])
        #         # open_searchBar("None")
        #         toggle_chatBox(True)
        page.update()

    def _on_load_chat_pressed(e):
        chat.controls = []
        data = e.control.data
        filename = data["FileName"]

        if filename == "None":
            Settings.chatName = "Unnamed Chat"
            LLM.messages.clear()
            chatPickerButt.text = "Unnamed Chat"
        else:
            with open(f"Chats/{filename}", "rt") as f:
                history = json.loads(f.read())
                LLM.messages = history
                for message in history:
                    if message["role"] == "AI":
                        responseChatMessage = ChatMessage(message=Message(Settings.username_AI,message["content"],message_type="chat_message"))
                        chat.controls.append(responseChatMessage)
                        # Settings.chatHistory =
                    elif message["role"] == "user":
                        userMessage = message["content"].split("\nREAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):\n")
                        responseChatMessage = ChatMessage(message=Message(Settings.userName,userMessage[0],message_type="chat_message"))
                        chat.controls.append(responseChatMessage)
            chatPickerButt.text = data["FileName"]
        close_chat_picker(None)
        page.update()

    def edit_text(e):
        pos = e.control.data
        print(f"Position: {pos}")
        for dict in Settings.chatHistory:
            if (dict["ID"] == pos) and (dict["USER"] == Settings.userName):
                editTextField.value = dict["Content"]
                Settings.editID = pos
                page.overlay.append(editTextDLG)
                page.update()

    def rebuild_chat(e):
        chat.controls = []
        LLM.messages = []
        tempChatHistory = []
        for dict in Settings.chatHistory:
            tempChatHistory.append(dict.copy())
        Settings.chatHistory.clear()
        Settings.chatID = 0
        systemMessage = LLM.create_message("system", Settings.system_prompt_default)
        editTextDLG.open = False
        if (Settings.userInfo is not None):
            systemMessage["content"] += f"\nInformation about {Settings.userName}:\n"
            systemMessage["content"] += Settings.userInfo
        LLM.messages.append(systemMessage)
        if Settings.username_AI != "AI" and Settings.firstMessage is not None:
           LLM.messages.append(LLM.create_message("user", ""))
           Settings.chatHistory.append({"USER": Settings.userName, "ID": Settings.chatID, "Content": LLM.create_message("user", "")})
           LLM.messages.append(LLM.create_message("AI", Settings.firstMessage))
           Settings.chatHistory.append({"USER": Settings.username_AI, "ID": Settings.chatID, "Content": LLM.create_message("AI", Settings.firstMessage)})

        text = editTextField.value.strip()
        print(f"Position: {Settings.editID}")
        for dict in Settings.chatHistory:
            if (dict["USER"] == Settings.userName) and (dict["ID"] == Settings.editID):
                send_message_click(str(text))
                break
            elif (dict["USER"] == Settings.userName):
                chat.controls.append(ChatMessage(Message(Settings.userName,dict["Content"],message_type="chat_message")))
                LLM.messages.append(LLM.create_message("user", dict["Content"]))
                Settings.chatHistory.append({"USER": Settings.userName, "ID": Settings.chatID, "Content": new_message.value.strip()})
            elif (dict["USER"] == Settings.username_AI):
                chat.controls.append(ChatMessage(Message(Settings.username_AI,dict["Content"],message_type="chat_message")))
                LLM.messages.append(LLM.create_message("AI", dict["Content"]))
                Settings.chatHistory.append({"USER": Settings.username_AI, "ID": Settings.chatID, "Content": new_message.value.strip()})
                Settings.chatID += 1

        page.update()


    def toggle_chatBox(toggle: bool, message: str = ""):
        if toggle:
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
        do_chat = False
        prompt = ""
        if (isinstance(e, str)):
            chat.controls.append(ChatMessage(Message(Settings.userName, e, message_type="chat_message")))
            Settings.chatHistory.append({"USER": Settings.userName, "ID": Settings.chatID, "Content": new_message.value})
            prompt = e
            do_chat = True
        elif (new_message.value is not None) and (new_message.value.strip() != ""):
            chat.controls.append(ChatMessage(Message(Settings.userName, new_message.value, message_type="chat_message")))
            Settings.chatHistory.append({"USER": Settings.userName, "ID": Settings.chatID, "Content": new_message.value})
            prompt = new_message.value
            do_chat = True

        if (do_chat):
            new_message.value = "Thinking..."
            new_message.disabled = True
            submitButton.disabled = True
            page.update()

            try:
                responseChatMessage = ChatMessage(message=Message(Settings.username_AI, "", message_type="chat_message"))
                chat.controls.append(responseChatMessage)

                # if modelLoader == "MLX":
                #     MLX.generate_response(prompt, responseChatMessage, page, chat)
                # else:
                #     LLM.generate_response(prompt, responseChatMessage, page, chat)

                LLM.generate_response(prompt, responseChatMessage, page, chat)
                chatPickerButt.text = Settings.chatName

                new_message.value = ""
                new_message.disabled = False
                submitButton.disabled = False
                new_message.focus()
                page.update()
            except Exception as ex:
                pass
                # print("EXCPETION:", ex)

    def _on_search_button_pressed(e):
        if Settings.toggle_search():
            searchButton.icon = ft.Icons.SEARCH_ROUNDED
            searchButton.icon_color = ft.Colors.GREEN
        else:
            searchButton.icon = ft.Icons.SEARCH_OFF_ROUNDED
            searchButton.icon_color = ft.Colors.RED
        page.update()

    def _on_theme_button_pressed(e):
        if Settings.theme == "Dark":
            Settings.theme = "Light"
        else:
            Settings.theme = "Dark"
        update_theme()

    def update_theme(theme = None):
        if (theme is not None):
            Settings.userTheme = Themes.list[theme.data]
            Settings.userThemeName = theme.data
            # themeSelectorMenu.close_view(theme.control.data["Name"])
        # page.theme_mode = ft.ThemeMode.LIGHT if Settings.theme == "Light" else ft.ThemeMode.DARK
        page.window.bgcolor = Settings.userTheme[Settings.theme]["Base"]

        for view in appPages:
            appPages[view].bgcolor = Settings.userTheme[Settings.theme]["Base"]
            for control in appPages[view].controls:
                if isinstance(control, ft.Row):
                    for i in control.controls:
                        if isinstance(i, ft.Text):
                            i.color = Settings.userTheme[Settings.theme]["Text"]
                        elif isinstance(i, ft.TextField):
                            i.color = Settings.userTheme[Settings.theme]["Text"]
                            i.bgcolor = Settings.userTheme[Settings.theme]["TextBKG"]
                        elif isinstance(control, ft.IconButton):
                            control.icon_color=Settings.userTheme[Settings.theme]["Icon"]
                if isinstance(control, ft.Text):
                    control.color = Settings.userTheme[Settings.theme]["Text"]
                elif isinstance(control, ft.TextField):
                    control.color = Settings.userTheme[Settings.theme]["Text"]
                    control.bgcolor = Settings.userTheme[Settings.theme]["TextBKG"]
                elif isinstance(control, ft.IconButton):
                    control.icon_color=Settings.userTheme[Settings.theme]["Icon"]

        chat.controls = []
        for dict in Settings.chatHistory:
            if (dict["USER"] == Settings.userName):
                chat.controls.append(ChatMessage(Message(Settings.userName,dict["Content"],message_type="chat_message")))
            elif (dict["USER"] == Settings.username_AI):
                chat.controls.append(ChatMessage(Message(Settings.username_AI,dict["Content"],message_type="chat_message")))

        submitButton.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        settingsButton.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        closeSettingsButton.icon_color = Settings.userTheme[Settings.theme]["Close"]
        quickUnloadModelButton.icon_color = Settings.userTheme[Settings.theme]["QuickUnload"]

        switchUserInfoButt.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        switchUserInfoButt.color = Settings.userTheme[Settings.theme]["Text"]

        loadCharacterButton.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        loadCharacterButton.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        loadCharacterButton.color = Settings.userTheme[Settings.theme]["Text"]

        themeSettingsButton.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        themeSettingsButton.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        themeSettingsButton.color = Settings.userTheme[Settings.theme]["Text"]

        # themeSelectorMenu.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        themeSelectorMenu.fill_color = Settings.userTheme[Settings.theme]["Button"]
        themeSelectorMenu.color = Settings.userTheme[Settings.theme]["Text"]

        chatPickerContainer.bgcolor = Settings.userTheme[Settings.theme]["Sidebar"]
        closeChatPickerButt.icon_color = Settings.userTheme[Settings.theme]["Icon"]

        changeLogText.md_style_sheet=Themes.build_changelog_sheet()
        closeChangeLogButt.icon_color = Settings.userTheme[Settings.theme]["Icon"]

        chatPickerButt.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        chatPickerButt.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        chatPickerButt.color = Settings.userTheme[Settings.theme]["Text"]

        openChangeLogButt.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        openChangeLogButt.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        openChangeLogButt.color = Settings.userTheme[Settings.theme]["Text"]

        openModelSettings.bgcolor = Settings.userTheme[Settings.theme]["Button"]
        openModelSettings.icon_color = Settings.userTheme[Settings.theme]["Icon"]
        openModelSettings.color = Settings.userTheme[Settings.theme]["Text"]
        closeModelSettings.icon_color = Settings.userTheme[Settings.theme]["Icon"]

        if Settings.gpuLayers == -1:
            automaticGPULayerButton.bgcolor = Settings.userTheme[Settings.theme]["AutoGPUEnabled"]
            automaticGPULayerButton.icon_color = "#cdcdcd" if Settings.theme == "Dark" else "#1c1c1c" #Settings.userTheme[Settings.theme]["Icon"]
            automaticGPULayerButton.color = "#cdcdcd" if Settings.theme == "Dark" else "#1c1c1c" #Settings.userTheme[Settings.theme]["Text"]
            gpuLayerSlider.disabled = True
            gpuLayerSlider.active_color = Settings.userTheme[Settings.theme]["Base"]
            gpuLayerSlider.thumb_color = Settings.userTheme[Settings.theme]["Inverse"]
            gpuLayerSlider.overlay_color = Settings.userTheme[Settings.theme]["GPUSliderOverlayActive"]
        else:
            automaticGPULayerButton.bgcolor = Settings.userTheme[Settings.theme]["AutoGPUDisabled"]
            automaticGPULayerButton.icon_color = "#cdcdcd" if Settings.theme == "Dark" else "#1c1c1c" #Settings.userTheme[Settings.theme]["Icon"]
            automaticGPULayerButton.color = "#cdcdcd" if Settings.theme == "Dark" else "#1c1c1c" #Settings.userTheme[Settings.theme]["Text"]
            gpuLayerSlider.disabled = False
            gpuLayerSlider.value = Settings.gpuLayers
            gpuLayerSlider.active_color = Settings.userTheme[Settings.theme]["GPUSliderActive"]
            gpuLayerSlider.thumb_color = Settings.userTheme[Settings.theme]["Inverse"]
            gpuLayerSlider.overlay_color = Settings.userTheme[Settings.theme]["GPUSliderOverlayDisabled"]

        page.update()

    def create_model_buttons(ifilename: str, ifile: str, loader: str):
        return ft.ListTile(title=ft.Text(ifilename), on_click=lambda e: _on_load_model_pressed(e), data={"FileName": ifile, "Loader": loader})

    def create_chat_buttons(ifilename: str, ifile: str, loader: str):
        if (ifilename == "Start New Chat...") and (ifile == "None"):
            return ft.ListTile(title=ft.Text(value=ifilename, color=Settings.userTheme[Settings.theme]["Text"]),
                expand=True, bgcolor=Settings.userTheme[Settings.theme]["TextBKG"],
                on_click=lambda e: _on_load_chat_pressed(e), data={"FileName": ifile, "Loader": loader})
        else:
            return ft.ListTile(title=ft.Text(value=ifilename, color=Settings.userTheme[Settings.theme]["Text"]),
                expand=True, bgcolor=Settings.userTheme[Settings.theme]["TextBKG"],
                trailing=ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=Settings.userTheme[Settings.theme]["Icon"], on_click=update_chat_list, data=ifile),
                on_click=lambda e: _on_load_chat_pressed(e), data={"FileName": ifile, "Loader": loader})

    def update_chat_list(e):
        Path(f"Chats/{e.control.data}").unlink(missing_ok=True)
        chatPickerList.controls.clear()
        chatPickerList.controls = set_chat_buttons()
        page.update()

    def create_theme_buttons(theme: str):
        return ft.DropdownOption(text=theme)

    def set_model_buttons():
        if not os.path.isdir(Settings.modelsPath):
            os.mkdir(Settings.modelsPath)
        modelButtons = []
        for file in os.listdir(Settings.modelsPath):
            if file.endswith(".gguf"):
                filename = file.replace(".gguf", "").replace("-", " ").replace("_", " ")
                modelButtons.append(create_model_buttons(filename, file, "GGUF"))
            # elif (os.path.isdir(Settings.modelsPath + file)) and (Settings.doMLX):
            #     for check in os.listdir(Settings.modelsPath + file):
            #         if check.endswith(".safetensors"):
            #             filename = file.replace("-", " ").replace("_", " ")
            #             modelButtons.append(create_model_buttons(filename, file, "MLX"))
            #             break
        return modelButtons

    def set_chat_buttons():
        if not os.path.isdir("Chats/"):
            os.mkdir("Chats/")
        modelButtons = [create_chat_buttons("Start New Chat...", "None", "None")]
        for file in os.listdir("Chats/"):
            if file.endswith(".json"):
                filename = file.replace(".json", "").replace("-", " ").replace("_", " ")
                modelButtons.append(create_chat_buttons(filename, file, "GGUF"))
        return modelButtons

    def set_theme_buttons():
        modelButtons = []
        for theme in Themes.list:
            modelButtons.append(create_theme_buttons(theme))
        return modelButtons

    def on_window_resize(e):
        # page.update()  # Check if Update Resizes Text Fields
        if (chat.controls is not None) and (chat.controls != []):
            for i in chat.controls:
                # print(i)
                if isinstance(i, ChatMessage):
                    # print("CHAT MESSAGE")
                    for j in i.controls:
                        if isinstance(j, ft.Text):
                            j.width = page.width - 100

        chatPickerContainer.width = (page.width * 0.35)
        changeLogText.width = page.width
        page.update()

    def eject_model(e):
        # print("EJECTING MODEL")
        LLM.unload_model(None)
        modelPickerDLG.close_view("Search Installed Models...")

    def _on_load_card_pressed(e):
        LLM.messages.clear()
        chat.controls.clear()
        if Cards.load_card(characterCardField.value):
            LLM.messages.clear()
            LLM.messages.append(LLM.create_message("system", Settings.system_prompt_default))
            LLM.messages.append(LLM.create_message("user", ""))
            LLM.messages.append(LLM.create_message("AI", Settings.firstMessage))
            chat.controls.append(ChatMessage(message=Message(Settings.username_AI, Settings.firstMessage, message_type="chat_message")))

    def _on_automatic_gpu_pressed(e):
        # print("SETTING GPU LAYERS")
        gpuLayerSlider.value = 0
        if Settings.gpuLayers == -1:
            # print("NON-AUTO")
            Settings.gpuLayers = 0
            gpuLayerSlider.disabled = False
        else:
            # print("AUTO")
            Settings.gpuLayers = -1
            gpuLayerSlider.disabled = True
        # gpuLayerText.value = str(Settings.gpuLayers)
        update_theme()

    def _on_gpuSlider_changed(e):
        Settings.gpuLayers = int(gpuLayerSlider.value)
        # gpuLayerText.value = str(Settings.gpuLayers)
        if LLM.llm is not None:
            Settings.reload_model = True
        # page.update()

    def get_playerInfo():
        if (Settings.userInfo is None):
            return ""
        return Settings.userInfo

    def _on_model_settings_changed(e):
        if temperatureField.value != Settings.temperature:
            Settings.temperature = temperatureField.value
            Settings.reload_model = True

        if topKField.value != Settings.top_K:
            Settings.top_K = topKField.value
            Settings.reload_model = True

        if topPField.value != Settings.top_P:
            Settings.top_P = topPField.value
            Settings.reload_model = True

        if minPField.value != Settings.min_P:
            Settings.min_P = minPField.value
            Settings.reload_model = True

        if penRepeatField.value != Settings.penalty_repeat:
            Settings.penalty_repeat = penRepeatField.value
            Settings.reload_model = True

        if penFrequencyField.value != Settings.penalty_frequency:
            Settings.penalty_frequency = penFrequencyField.value
            Settings.reload_model = True

        if seedField.value != Settings.seed:
            Settings.seed = seedField.value
            Settings.reload_model = True

    firstRunUsername = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
    )

    firstRunDLG = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("User Creation"),
        content=ft.Column(controls=[firstRunUsername], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Start Chatting...", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    editTextField = ft.TextField(
        label=None,
        autofocus=True,
        value="",
        on_submit=rebuild_chat
    )

    editTextDLG = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Edit Text"),
        content=ft.Column(controls=[editTextField], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Confirm", on_click=rebuild_chat), ft.ElevatedButton(text="Cancel", on_click=None)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_model_picker(e):
        modelPickerDLG.controls = set_model_buttons()
        modelPickerDLG.open_view()

    modelPickerDLG = ft.SearchBar(
        bar_hint_text="Search Installed Models...",
        on_tap=lambda e: modelPickerDLG.open_view(),
        # on_tap=lambda e: open_searchBar("modelPickerDLG"),
        controls=set_model_buttons(),
        expand=True,
        visible=True,
    )

    def open_chat_picker(e):
        chatPickerList.controls = set_chat_buttons()
        chatPickerContainer.width = (page.width * 0.35)# if (page.width <= 1000) else (page.width * 0.8)
        page.overlay.clear()
        page.overlay.append(chatStack)
        page.update()

    def close_chat_picker(e):
        page.overlay.clear()
        page.update()

    chatPickerList = ft.ListView(
        expand=True,
        spacing=15,
    )

    closeChatPickerButt = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_color="#AA0000",
        tooltip="Close",
        # on_click=lambda e: page.go("/Chat")
        on_click=close_chat_picker
    )

    chatPickerContainer = ft.Container(
        content=ft.Column(controls=[ft.Row(controls=[closeChatPickerButt, ft.Text(value="Load Previous Chat", size=20)]), chatPickerList]),
        border=ft.border.all(1, ft.Colors.TRANSPARENT),
        border_radius=5,
        padding=10,
        expand=True,
        bgcolor=ft.Colors.BLUE,
        right=20,
        bottom=20,
        top=20,
    )

    chatStack = ft.Stack(
        expand=True,
        controls=[
            ft.Container(bgcolor="#77000000", expand=True),
            chatPickerContainer
        ],

    )

    chatPickerButt = ft.ElevatedButton(
        tooltip="Open Chat Picker",
        on_click=open_chat_picker,
        text="Open Previous Chat",
        bgcolor=Settings.userTheme[Settings.theme]["Base"],
        expand=True
    )

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
        bgcolor=ft.Colors.TRANSPARENT,
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
        icon_color=ft.Colors.RED,
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
        tooltip="Change Theme",
        on_click=_on_theme_button_pressed,
        icon_color="#cdcdcd",
        text="Change Theme",
        bgcolor=Settings.userTheme[Settings.theme]["Base"],
    )

    themeSelectorMenu = ft.Dropdown(
        filled=True,
        value=Settings.userThemeName,
        visible=True,
        options=set_theme_buttons(),
        on_change=update_theme
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
        bgcolor=Settings.userTheme[Settings.theme]["Base"],
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
        on_change_end=_on_gpuSlider_changed,
    )

    temperatureField = ft.TextField(
        # label=str(Settings.temperature),
        value=str(Settings.temperature),
        hint_text="Temperature",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    topKField = ft.TextField(
        value=str(Settings.top_K),
        hint_text="Top K",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    topPField = ft.TextField(
        value=str(Settings.top_P),
        hint_text="Top P",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )
    minPField = ft.TextField(
        value=str(Settings.min_P),
        hint_text="Min P",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    penRepeatField = ft.TextField(
        value=str(Settings.penalty_repeat),
        hint_text="Repeat Penalty",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    penFrequencyField = ft.TextField(
        value=str(Settings.penalty_frequency),
        hint_text="Frequency Penalty",
        tooltip="Recommended Values: 0.5 <-> 1.0",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    seedField = ft.TextField(
        value=str(Settings.seed),
        hint_text="Seed",
        tooltip="Random Seed: -1",
        adaptive=True,
        on_tap_outside=_on_model_settings_changed,
    )

    loadCharacterButton = ft.ElevatedButton(
        icon=ft.Icons.PERSON,
        tooltip="Load Character Card",
        # on_click=lambda e: page.go("/CharacterLoader"),
        on_click=_on_load_card_pressed,
        icon_color="#cdcdcd",
        text="Load Character",
        bgcolor=Settings.userTheme[Settings.theme]["Base"],
    )

    characterCardField = ft.TextField(
        value="",
        hint_text="Path to Character Card",
        tooltip="Use Full Path",
        adaptive=True,
    )

    switchUserInfoButt = ft.ElevatedButton(
        icon=ft.Icons.EDIT_OUTLINED,
        tooltip="Disable Automatic GPU Layers",
        on_click=lambda e: page.go("/UserInfo"),
        icon_color="#cdcdcd",
        text="Edit User Info",
        bgcolor=Settings.userTheme[Settings.theme]["Base"],
    )

    # Add Important User Information like Name, Relationships, Computer Specs, etc.
    # stored in a file to easily be recalled by the LLM.
    # This allows a more personable and enhanced experience. For example:
    # User: "Why won't my MacBook turn on?"
    # AI already knows User has an M1 MacBook Air, and searches for results without you
    # explicitly telling it what device to search for.
    # NOTE: Data does not leave your hard drive.
    userInfoField = ft.TextField(
        value=get_playerInfo(),
        hint_text="Enter Persistant Information to keep across chats",
        tooltip="Enter Persistant Information to keep across chats",
        adaptive=True,
        expand=True,
    )

    def set_userInfo(e):
        if (userInfoField.value is not None) and (userInfoField.value.strip() != ""):
            Settings.userInfo = userInfoField.value
        else:
            Settings.userInfo = None
        # print(userInfoField.value)
        Settings.save_settings()
        page.go("/Settings")

    closeUserInfoButt = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_color=Settings.userTheme[Settings.theme]["Icon"],
        tooltip="Close",
        on_click=set_userInfo
    )

    openChangeLogButt = ft.ElevatedButton(
        text="Changelog",
        icon=ft.Icons.CHANGE_CIRCLE_OUTLINED,
        icon_color=Settings.userTheme[Settings.theme]["Icon"],
        tooltip="Changelog",
        on_click=lambda e: page.go("/Settings/ChangeLog")
    )

    closeChangeLogButt = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_color=Settings.userTheme[Settings.theme]["Icon"],
        tooltip="Close",
        on_click=lambda e: page.go("/Settings")
    )

    def get_changeLog_text():
        text = ""
        with open("changelog", "r") as cl:
            text = cl.read()
        return text


    changeLogText = ft.Markdown(
        value=get_changeLog_text(),
        selectable=False,
        fit_content=True,
        width=page.width,
        soft_line_break=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        md_style_sheet=Themes.build_changelog_sheet(),
    )

    changeLogContainer = ft.Container(
        content=changeLogText,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
    )

    openModelSettings = ft.ElevatedButton(
        text="Model Settings",
        icon=ft.Icons.DEVICE_THERMOSTAT,
        icon_color=Settings.userTheme[Settings.theme]["Icon"],
        tooltip="Changelog",
        on_click=lambda e: page.go("/Settings/ModelSettings")
    )

    closeModelSettings = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_color=Settings.userTheme[Settings.theme]["Icon"],
        tooltip="Close",
        on_click=lambda e: page.go("/Settings")
    )

    appPages = {
        "/Chat": ft.View(
            "/Chat",
            [
                ft.Row(controls=[modelPickerDLG, quickUnloadModelButton, chatPickerButt]),
                chat_container,
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY, controls=[settingsButton, new_message, searchButton, submitButton]),
            ],
            bgcolor=Settings.userTheme[Settings.theme]["Base"],
        ),
        "/UserInfo": ft.View(
            "/UserInfo",
            [
                closeUserInfoButt,
                ft.Text(value="Enter Persistant Information to keep across chats:"),
                userInfoField
            ],
            bgcolor=Settings.userTheme[Settings.theme]["Base"],
        ),
        "/Settings": ft.View(
            "/Settings",
            [
                closeSettingsButton,
                ft.Row(controls=[themeSettingsButton, themeSelectorMenu]),
                ft.Row(controls=[loadCharacterButton, characterCardField]),
                openModelSettings, switchUserInfoButt, openChangeLogButt

            ],
            bgcolor=Settings.userTheme[Settings.theme]["Base"],
        ),
        "/Settings/ModelSettings": ft.View(
            "/Settings/ModelSettings",
            [
                closeModelSettings,
                ft.Row(controls=[automaticGPULayerButton, gpuLayerSlider]),
                ft.Row(controls=[ft.Text(value="Temperature: ", expand=True), temperatureField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Seed: ", expand=True), seedField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Top K: ", expand=True), topKField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Top P: ", expand=True), topPField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Min P: ", expand=True), minPField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Repeat Penalty: ", expand=True), penRepeatField], alignment=ft.MainAxisAlignment.START),
                ft.Row(controls=[ft.Text(value="Frequency Penalty: ", expand=True), penFrequencyField], alignment=ft.MainAxisAlignment.START,),
            ]
        ),
        "/Settings/ChangeLog": ft.View(
            "/Settings/ChangeLog",
            [
                ft.Row(controls=[closeChangeLogButt, ft.Text(value="Changelog", size=48, color=Settings.userTheme[Settings.theme]["Text"],)]),
                changeLogContainer
            ]
        ),
        "/CharacterLoader": ft.View(
            "/CharacterLoader",
            [
                # closeCharButton,
                ft.Text(value="NOT IMPLEMENTED YET", expand=True, text_align=ft.TextAlign.CENTER),
            ],
            bgcolor=Settings.userTheme[Settings.theme]["Base"],
        ),
    }

    def route_change(route):
        page.views.clear()
        page.clean()
        page.update()
        if (route.route == "/Chat"):
            page.title = "WebSearch AI"
        elif (route.route == "/Settings"):
            page.title = "Settings"
        elif (route.route == "/Settings/ChangeLog"):
            page.title = "Changelog"
        elif (route.route == "/UserInfo"):
            page.title = "User Information Editor"

        page.views.append(appPages[route.route])
        if Settings.reload_model:
            toggle_chatBox(False, "Loading Model...")
            LLM.load_model(Settings.loaded_model)
            toggle_chatBox(True, "")
        page.update()

    async def close_window(e):
        if e.data == "close":
            page.open(
                ft.AlertDialog(
                    open=True,
                    modal=True,
                    icon=ft.Icon(name=ft.Icons.WARNING, color="#FF0000"),
                    title="Closing Application...",
                    content=ft.Text("Please Wait.\nUnloading Model..."),
                )
            )
            page.update()
            LLM.unload_model(None)
            LLM.unload_embedder(None)
            Settings.save_settings()
            # await asyncio.sleep(2)
            # time.sleep(2)
            page.window.destroy()

    page.on_resized = on_window_resize
    page.window.on_event = close_window
    page.window.prevent_close = True
    page.on_route_change = route_change
    page.go("/Chat")
    toggle_chatBox(False, "Select a Model to Load...")

    if Settings.userName == "SETME#0074":
        page.overlay.append(firstRunDLG)
    else:
        new_message.prefix = ft.Text(f"{Settings.userName}: ")

    update_theme()

ft.app(target=main, view=ft.AppView.FLET_APP)
