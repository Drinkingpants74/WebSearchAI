import asyncio
import warnings
import flet as ft
# import sys
import gc
import json
import os
import webbrowser
# from time import sleep as timeSleep
from pathlib import Path

import Settings
import LLM
# import Cards
import API
import Themes
import Audio

warnings.filterwarnings("ignore", category=DeprecationWarning)

class SettingsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, updateMainTheme):
        super().__init__()
        self.updateMainTheme = updateMainTheme
        self.parentPage = page
        self.parentPage.on_resize = self.resize
        self.on_dismiss = self.save_settings
        self.title = ft.Text(value="Settings")
        self.expand = True

        # Settings Controls
        self.usernameField = ft.TextField(hint_text="Username", expand=3, multiline=False, max_lines=1, on_change=self.get_app_settingValues)
        self.avatarColorField = ft.TextField(hint_text="Avatar Color (HTML Code: #rrggbb)", expand=3, multiline=False, max_lines=1, on_change=self.get_app_settingValues)
        self.modelPathField = ft.TextField(hint_text="Models Path", expand=3, multiline=False, max_lines=1, on_change=self.get_app_settingValues)
        self.blacklistField = ft.TextField(hint_text="URL Blacklist (Ex: github, huggingface)", expand=3, multiline=True, max_lines=4, on_change=self.get_app_settingValues)

        self.usernameLabel = ft.Text(value="Username: ", expand=1)
        self.avatarColorLabel = ft.Text(value="Avatar Color: ", expand=1)
        self.modelPathLabel = ft.Text(value="Model Path: ", expand=1)
        self.blacklistLabel = ft.Text(value="Blacklist: ", expand=1)
        self.themeLabel = ft.Text(value="Theme: ", expand=1)
        self.TTSLabel = ft.Text(value="Enable TTS: ", expand=1)

        self.themeName = ft.Dropdown(
            options=self.get_themes(),
            on_select=self.set_app_theme,
            value=Settings.userThemeName,
            filled=True,
            border_width=1,
            focused_border_width=3,
            menu_style=ft.MenuStyle()
        )

        self.themeStyle = ft.IconButton(
            icon=ft.Icons.SUNNY if Settings.theme == "Light" else ft.Icons.MODE_NIGHT,
            on_click=self.set_app_style,
            icon_color = Settings.userTheme[Settings.theme]["Icon"]
        )

        self.toggleTTS = ft.IconButton(
            icon=ft.Icons.SPEAKER,
            on_click=self.do_toggleTTS,
            icon_color = "#00ff00" if Settings.useTTS else "#ff0000",
            expand=1
        )

        self.GPULayersSlider = ft.Slider(min=-1, max=99, divisions=101, round=0, expand=True, on_change=self.get_settingValues)
        self.contextSlider = ft.Slider(min=1, max=16, divisions=15, round=0, expand=True, on_change=self.get_settingValues)
        self.temperatureSlider = ft.Slider(min=1, max=40, divisions=39, round=0, expand=True, on_change=self.get_settingValues)
        self.topKSlider = ft.Slider(min=10, max=100, divisions=89, round=0, expand=True, on_change=self.get_settingValues)
        self.minPSlider = ft.Slider(min=0, max=100, divisions=100, round=0, expand=True, on_change=self.get_settingValues)
        self.topPSlider = ft.Slider(min=0, max=100, divisions=100, round=0, expand=True, on_change=self.get_settingValues)
        self.batchSizeSlider = ft.Slider(min=1, max=16, divisions=16, round=0, expand=True, on_change=self.get_settingValues)
        self.seedField = ft.TextField(expand=True, multiline=False, max_lines=1, input_filter=ft.NumbersOnlyInputFilter(), on_change=self.get_settingValues)

        self.GPULayersLabel = ft.Text(value="GPU Layers", expand=True, align=ft.Alignment.CENTER)
        self.contextLabel = ft.Text(value="Context", expand=True, align=ft.Alignment.CENTER)
        self.temperatureLabel = ft.Text(value="Temperature", expand=True, align=ft.Alignment.CENTER)
        self.topKLabel = ft.Text(value="Top K", expand=True, align=ft.Alignment.CENTER)
        self.topPLabel = ft.Text(value="Top P", expand=True, align=ft.Alignment.CENTER)
        self.minPLabel = ft.Text(value="Min P", expand=True, align=ft.Alignment.CENTER)
        self.batchSizeLabel = ft.Text(value="Batch Size", expand=True, align=ft.Alignment.CENTER)
        self.seedLabel = ft.Text(value="Seed", expand=True, align=ft.Alignment.CENTER)

        self.userSettingLabel = ft.Text(value="Coming Soon™", align=ft.Alignment.CENTER, size=64)

        self.Changelog = ft.Markdown(
            value=self.get_changelog()
        )


        self.tabBarView = ft.TabBarView(
            expand=True,
            controls=[
                ft.Container(
                    border=ft.Border.all(1),#, ft.Colors.AMBER),
                    border_radius=15,
                    padding=10,
                    expand=True,
                    content=ft.ListView(
                        controls=[
                            ft.Row(controls=[self.usernameLabel ,self.usernameField]),
                            ft.Row(controls=[self.avatarColorLabel ,self.avatarColorField]),
                            ft.Row(controls=[self.modelPathLabel ,self.modelPathField]),
                            ft.Row(controls=[self.blacklistLabel ,self.blacklistField]),
                            ft.Row(controls=[self.themeLabel, ft.Row(expand=3, controls=[self.themeName, self.themeStyle])]),
                            # ft.Row(controls=[self.TTSLabel, ft.Container(expand=1), self.toggleTTS, ft.Container(expand=4)])
                        ],
                        spacing=10,
                        auto_scroll=False,
                        padding=25,
                )),
                ft.Container(
                    border=ft.Border.all(1),
                    border_radius=15,
                    padding=10,
                    expand=True,
                    content=ft.ListView(
                        controls=[
                            self.userSettingLabel
                        ]
                )),
                ft.Container(
                    border=ft.Border.all(1),#, ft.Colors.AMBER),
                    border_radius=15,
                    padding=10,
                    expand=True,
                    content=ft.ListView(
                        spacing=10,
                        auto_scroll=False,
                        padding=25,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.GPULayersLabel,
                                            self.GPULayersSlider
                                        ]
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.contextLabel,
                                            self.contextSlider
                                        ]
                                    ),
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.temperatureLabel,
                                            self.temperatureSlider
                                        ]
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.topKLabel,
                                            self.topKSlider
                                        ]
                                    ),
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.minPLabel,
                                            self.minPSlider
                                        ]
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.topPLabel,
                                            self.topPSlider
                                        ]
                                    ),
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.batchSizeLabel,
                                            self.batchSizeSlider
                                        ]
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            self.seedLabel,
                                            self.seedField
                                        ]
                                    ),
                                ]
                            ),
                        ]
                )),
                ft.Container(
                    border=ft.Border.all(1),#, ft.Colors.AMBER),
                    border_radius=15,
                    padding=10,
                    expand=True,
                    content=ft.Column(
                        controls=[self.Changelog],
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            ],
        )

        self.AppTab = ft.Tab(label=ft.Text("App Settings"))
        self.UserTab = ft.Tab(label=ft.Text("User Settings"))
        self.ModelTab = ft.Tab(label=ft.Text("Model Settings"))
        self.ChangesTab = ft.Tab(label=ft.Text("Changelog"))

        self.tabBar = ft.TabBar(
            scrollable=False,
            tabs=[
                self.AppTab,
                self.UserTab,
                self.ModelTab,
                self.ChangesTab
            ],
        )


        self.Container = ft.Tabs(
            width=self.parentPage.window.width * 0.7,
            height=self.parentPage.window.height * 0.7,
            length=4,
            content=ft.Column(
                expand=True,
                controls=[
                    self.tabBar,
                    self.tabBarView,
                ],
            ),
        )

        self.content=self.Container
        self.update_theme()
        self.set_settingValues()
        self.update_app_settingValues()

    def resize(self):
        self.Container.width=self.parentPage.window.width * 0.7
        self.Container.height=self.parentPage.window.height * 0.7

    def do_toggleTTS(self):
        Settings.useTTS = not Settings.useTTS
        if (Settings.useTTS):
            self.toggleTTS.icon_color = "#00ff00"
        else:
             self.toggleTTS.icon_color = "#ff0000"

    def get_themes(self):
        themeButtons = []
        for theme in Themes.list:
            themeButtons.append(ft.DropdownOption(key=theme, style=ft.ButtonStyle(color=Settings.userTheme[Settings.theme]["UserInputBackground"])))
        return themeButtons

    def get_styles(self):
        themeButtons = []
        for theme in Settings.userTheme:
            themeButtons.append(ft.DropdownOption(key=theme, style=ft.ButtonStyle(color=Settings.userTheme[Settings.theme]["UserInputBackground"])))
        return themeButtons

    def set_app_theme(self, e: ft.Event):
        Settings.userThemeName = e.data
        Settings.userTheme = Themes.list[str(e.data)]
        self.parentPage.update()
        self.updateMainTheme()
        self.update_theme()

    def set_app_style(self, e: ft.Event):
        if (Settings.theme == "Light"):
            Settings.theme = "Dark"
            self.themeStyle.tooltip = "Toggle Light Mode"
            self.themeStyle.icon = ft.Icons.MODE_NIGHT
        else:
            Settings.theme = "Light"
            self.themeStyle.tooltip = "Toggle Dark Mode"
            self.themeStyle.icon = ft.Icons.SUNNY

        self.parentPage.theme_mode = ft.ThemeMode.DARK if Settings.theme == "Dark" else ft.ThemeMode.LIGHT
        self.parentPage.update()

        self.updateMainTheme()
        self.update_theme()


    def get_changelog(self):
        # changelogWidgets = []
        text = ""
        with open("src/changelog", "r") as cl:
            text = cl.read()

        # chunks = text.split("##")
        # for i in chunks:
        #     changelogWidgets.append(ft.Markdown(value=f"##{i}"))

        return text

    def update_changelog(self):
        self.Changelog.md_style_sheet = Themes.get_markdown_sheet()
        self.Changelog.code_theme = Themes.get_markdown_codeTheme()
        self.Changelog.code_style_sheet = Themes.get_markdown_codeSheet()

    def set_settingValues(self):
        self.GPULayersSlider.value = int(Settings.gpuLayers)
        self.contextSlider.value = int(Settings.ctxSize / 4096)
        self.temperatureSlider.value = int(Settings.temperature * 20)
        self.topKSlider.value = int(Settings.top_K)
        self.minPSlider.value = int(Settings.min_P * 100)
        self.topPSlider.value = int(Settings.top_P * 100)
        self.batchSizeSlider.value = int(Settings.batchSize / 128.0)
        self.seedField.value = str(Settings.seed)
        self.update_settingValues()

    def update_app_settingValues(self, e=None):
        if (Settings.userName != "SETME#0074"):
            self.usernameField.value = Settings.userName

        if (Settings.avatarColor is not None):
            self.avatarColorField.value = Settings.avatarColor

        self.modelPathField.value = Settings.modelsPath
        self.blacklistField.value = Settings.userBlacklist

    def get_app_settingValues(self, e=None):
        if (self.usernameField.value.strip() != ""):
            Settings.userName = self.usernameField.value

        if (len(self.avatarColorField.value.strip()) == 7) or (len(self.avatarColorField.value.strip()) == 9):
            Settings.avatarColor = self.avatarColorField.value

        if (os.path.exists(self.modelPathField.value)):
            Settings.modelsPath = self.modelPathField.value

        Settings.userBlacklist = self.blacklistField.value

    def get_settingValues(self, e=None):
        # settingChanged = False
        if (self.GPULayersSlider.value is not None) and (self.GPULayersSlider.value != Settings.gpuLayers):
            Settings.gpuLayers = int(self.GPULayersSlider.value)
            # settingChanged = True
        if (self.contextSlider.value is not None) and (self.contextSlider.value != Settings.ctxSize):
            Settings.ctxSize = self.contextSlider.value * 4096
            # settingChanged = True
        if (self.temperatureSlider.value is not None) and (self.temperatureSlider.value != Settings.temperature):
            Settings.temperature = round(float(self.temperatureSlider.value * 0.05), 2)
            # settingChanged = True
        if (self.topKSlider.value is not None) and (self.topKSlider.value != Settings.top_K):
            Settings.top_K = int(self.topKSlider.value)
            # settingChanged = True
        if (self.minPSlider.value is not None) and (self.minPSlider.value != Settings.min_P):
            Settings.min_P = round(float(self.minPSlider.value / 100.0), 2)
            # settingChanged = True
        if (self.topPSlider.value is not None) and (self.topPSlider.value != Settings.ctxSize):
            Settings.top_P = round(float(self.topPSlider.value / 100.0), 2)
            # settingChanged = True
        if (self.batchSizeSlider.value is not None) and (self.batchSizeSlider.value != Settings.batchSize):
            Settings.batchSize = int(self.batchSizeSlider.value) * 128.0
            # settingChanged = True
        if (self.seedField.value is not None) and (self.seedField.value != Settings.seed):
            Settings.seed = int(self.seedField.value)
            # settingChanged = True

        self.update_settingValues()


    def save_settings(self, e=None):
        Settings.save_settings()

    def update_settingValues(self):
        if (Settings.gpuLayers == -1):
            self.GPULayersLabel.value = "GPU Layers: Auto"
        else:
            self.GPULayersLabel.value = f"GPU Layers: {Settings.gpuLayers}"
        self.contextLabel.value = f"Context: {Settings.ctxSize}"
        self.temperatureLabel.value = f"Temperature: {Settings.temperature}"
        self.topKLabel.value = f"Top K: {Settings.top_K}"
        self.topPLabel.value = f"Top P: {Settings.top_P}"
        self.minPLabel.value = f"Min P: {Settings.min_P}"
        self.batchSizeLabel.value = f"Batch Size: {Settings.batchSize}"

    def update_theme(self):
        self.update_changelog()

        self.bgcolor = Settings.userTheme[Settings.theme]["Background"]
        self.title.color = Settings.userTheme[Settings.theme]["Text"]

        self.themeStyle.icon_color = Settings.userTheme[Settings.theme]["Icon"]

        self.tabBar.divider_color = Settings.userTheme[Settings.theme]["SettingsTabDivider"]
        self.tabBar.indicator_color = Settings.userTheme[Settings.theme]["SettingsTabIndicator"]
        self.tabBar.label_color = Settings.userTheme[Settings.theme]["SettingsTabLabelSelected"]
        self.tabBar.unselected_label_color = Settings.userTheme[Settings.theme]["SettingsTabLabelUnselected"]
        self.tabBar.overlay_color = Settings.userTheme[Settings.theme]["SettingsTabOverlay"]

        for child in self.tabBarView.controls:
            if (isinstance(child, ft.Container)):
                child.border = ft.Border.all(1, Settings.userTheme[Settings.theme]["ContainerBorderColor"])

        self.themeName.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]
        self.themeName.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.themeName.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.themeName.fill_color = Settings.userTheme[Settings.theme]["UserInputBackground"]
        self.themeName.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        # self.themeName.menu_style.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        for child in self.themeName.options:
            if (child is not None):
                child.style.color = Settings.userTheme[Settings.theme]["UserInputText"]


        self.TTSLabel.color = Settings.userTheme[Settings.theme]["Text"]
        # self.toggleTTS

        self.usernameLabel.color = Settings.userTheme[Settings.theme]["Text"]
        self.avatarColorLabel.color = Settings.userTheme[Settings.theme]["Text"]
        self.modelPathLabel.color = Settings.userTheme[Settings.theme]["Text"]
        self.blacklistLabel.color = Settings.userTheme[Settings.theme]["Text"]
        self.themeLabel.color = Settings.userTheme[Settings.theme]["Text"]
        self.userSettingLabel.color = Settings.userTheme[Settings.theme]["Text"]

        self.usernameField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.usernameField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.usernameField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.usernameField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.usernameField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.avatarColorField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.avatarColorField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.avatarColorField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.avatarColorField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.avatarColorField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.modelPathField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.modelPathField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.modelPathField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.modelPathField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.modelPathField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.blacklistField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.blacklistField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.blacklistField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.blacklistField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.blacklistField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.seedField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.seedField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.seedField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.seedField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.seedField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.GPULayersSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.GPULayersSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.contextSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.contextSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.temperatureSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.temperatureSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.topKSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.topKSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.minPSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.minPSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.topPSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.topPSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.batchSizeSlider.active_color = Settings.userTheme[Settings.theme]["SettingsSliderActive"]
        self.batchSizeSlider.inactive_color = Settings.userTheme[Settings.theme]["SettingsSliderInactive"]

        self.GPULayersLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.contextLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.temperatureLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.topKLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.topPLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.minPLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.batchSizeLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]
        self.seedLabel.color = Settings.userTheme[Settings.theme]["SettingsLabel"]



class LoadModelDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, userInput: ft.TextField):
        super().__init__()
        self.UserInput = userInput
        self.parentPage = page
        self.parentPage.on_resize = self.resize
        self.title = ft.Text(value="Load Model")
        self.expand = True
        self.apiPathField = ft.TextField(
            hint_text="API Address (Ex: 127.0.0.1:3774)",
            value=str(Settings.apiPath),
            expand=True,
            on_change=self.update_models,
            on_submit=self.update_models
        )
        self.apiKeyField = ft.TextField(
            hint_text="API Key (Optional)",
            value=str(Settings.apiKey),
            expand=True,
            on_change=self.update_models,
            on_submit=self.update_models
        )

        self.ModelBar = ft.ListView(
            controls=self.get_models(),
        )
        self.ModelContainer = ft.Container(
            content=self.ModelBar,
            border=ft.Border.all(1),
            border_radius=15,
            padding=10,
            expand=True,
        )
        self.Container = ft.ListView(
            controls=[
                self.apiPathField,
                self.apiKeyField,
                self.ModelContainer,
            ],
            spacing=10,
            # expand=True,
            width=self.parentPage.window.width * 0.7,
            height=self.parentPage.window.height * 0.7
        )

        self.content=self.Container
        self.update_theme()

    def resize(self):
        self.Container.width=self.parentPage.window.width * 0.7
        self.Container.height=self.parentPage.window.height * 0.7

    def build_local_model_button(self, file):
        return ft.ListTile(
            title=file.replace(".gguf", "").replace("-", " ").replace("_", " "),
            on_click=lambda e: self.load_local_model(file),
            # text_color=Settings.userTheme[Settings.theme]["Text"]
        )

    def build_API_model_button(self, file):
        return ft.ListTile(
            title=file.replace(".gguf", "").replace("-", " ").replace("_", " "),
            on_click=lambda e: self.load_API_model(file),
            # text_color=Settings.userTheme[Settings.theme]["Text"]
        )

    def update_models(self, e=None):
        Settings.apiPath = self.apiPathField.value.strip()
        Settings.apiKey = self.apiKeyField.value.strip()
        API.get_authorized()
        self.ModelBar.controls = self.get_models()
        self.parentPage.update()

    def get_models(self, e=None):
        modelButtons = []
        if (Settings.apiPath.strip() == "") or (Settings.apiPath.strip() == "http://127.0.0.1:3774"):
            Settings.apiMode = False
            if not os.path.isdir("src/Models/"):
                os.mkdir("src/Models/")
            for file in os.listdir("src/Models/"):
                if file.endswith(".gguf"):
                    modelButtons.append(self.build_local_model_button(file))
        else:
            Settings.apiMode = True
            try:
                for model in API.get_models():
                    modelButtons.append(self.build_API_model_button(model))
            except Exception as _e:
                pass

        if (len(modelButtons) <= 0):
            if (Settings.apiMode):
                modelButtons.append(ft.Button(content="No Models Found. Click to Refresh.", on_click=self.update_models))
            else:
                modelButtons.append(ft.Button(content="No Models Found. Click to Download.", on_click=self.open_HuggingFace))
        return modelButtons

    def open_HuggingFace(self, e=None):
        webbrowser.open("https://huggingface.co/collections/DrinkingPants74/websearch-ai-models")

    def load_local_model(self, file):
        if (Settings.apiPath.strip() == ""):
            Settings.apiPath = "http://127.0.0.1:3774"
        Settings.apiMode = False
        self.parentPage.pop_dialog()
        self.open=False
        self.UserInput.value = "Loading Model..."
        self.parentPage.update()
        self.parentPage.run_thread(API.get_authorized)
        self.parentPage.run_thread(LLM.load_model, file, self.UserInput, self.parentPage)
        self.parentPage.update()

    def load_API_model(self, file):
        Settings.apiMode = True
        self.parentPage.pop_dialog()
        self.UserInput.value = "Loading Model..."
        self.parentPage.update()
        self.parentPage.run_thread(API.get_authorized)
        self.parentPage.run_thread(LLM.load_model, file, self.UserInput, self.parentPage)
        self.parentPage.update()

    def update_theme(self):
        self.bgcolor = Settings.userTheme[Settings.theme]["Background"]
        self.title.color = Settings.userTheme[Settings.theme]["Text"]

        self.apiPathField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.apiPathField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.apiPathField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.apiPathField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.apiPathField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.apiKeyField.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.apiKeyField.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.apiKeyField.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.apiKeyField.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.apiKeyField.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.ModelContainer.border = ft.Border.all(1, Settings.userTheme[Settings.theme]["ContainerBorderColor"])



class ChatHistoryDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, loadChatFile):
        super().__init__()
        self.loadFile = loadChatFile
        self.parentPage = page
        self.parentPage.on_resize = self.resize
        self.title = ft.Text(value="Chat History")
        self.expand = True
        self.Container = ft.ListView(
            spacing=10,
            width=self.parentPage.window.width * 0.7,
            height=self.parentPage.window.height * 0.7
        )

        self.content=self.Container
        self.set_chat_buttons()
        self.update_theme()

    def resize(self):
        self.Container.width=self.parentPage.window.width * 0.7
        self.Container.height=self.parentPage.window.height * 0.7

    def build_chat_button(self, file):
        return ChatButton(self.load_chat, self.delete_chat, file)

    # def build_chat_button(self, file):
    #     fileName = file.split('_|')[1].replace(".json", "").replace("-", " ").replace("_", " ")
    #     return ft.Button(
    #         content=str(fileName),
    #         on_click=lambda event: self.load_chat(file),
    #         bgcolor=Settings.userTheme[Settings.theme]["ChatButtonBackground"],
    #         color=Settings.userTheme[Settings.theme]["Text"],
    #     )

    def delete_chat(self, file):
        Path(f"src/Chats/{file}").unlink(missing_ok=True)
        self.set_chat_buttons()
        self.update()

    def set_chat_buttons(self):
        self.Container.controls.clear()
        if not os.path.isdir("src/Chats/"):
            os.mkdir("src/Chats/")
        fileList = []
        for file in os.listdir("src/Chats/"):
            if file.endswith(".json"):
                fileList.append(file)
        fileList.sort(reverse=True)
        for file in fileList:
            self.Container.controls.append(self.build_chat_button(file))

    def load_chat(self, e):
        self.parentPage.pop_dialog()
        self.loadFile(e)

    def update_theme(self):
        self.bgcolor = Settings.userTheme[Settings.theme]["Background"]
        self.title.color = Settings.userTheme[Settings.theme]["Text"]


class CharacterCardDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.parentPage = page
        self.parentPage.on_resize = self.resize
        self.title = ft.Text(value="Load A Character")
        self.expand = True

        self.Container = ft.Container(
            width=self.parentPage.window.width * 0.7,
            height=self.parentPage.window.height * 0.7,
            content=ft.Text(value="Coming Soon™", align=ft.Alignment.CENTER, size=64)
        )

        # self.Container = ft.ListView(
        #     spacing=10,
        #     width=self.parentPage.width * 0.7,
        #     height=self.parentPage.height * 0.7
        # )

        self.content=self.Container
        self.update_theme()

    def resize(self):
        self.Container.width=self.parentPage.window.width * 0.7
        self.Container.height=self.parentPage.window.height * 0.7

    def update_theme(self):
        self.bgcolor = Settings.userTheme[Settings.theme]["Background"]
        self.title.color = Settings.userTheme[Settings.theme]["Text"]

class ChatButton(ft.Container):
    def __init__(self, loadChatFunc, deleteFunc, file):
        super().__init__()
        self.load_chat = loadChatFunc
        self.delete_chat = deleteFunc
        self.fileName = file.split('_|')[1].replace(".json", "").replace("-", " ").replace("_", " ")
        self.filePath = file
        self.chatButton = ft.Button(
            content=str(self.fileName),
            on_click=lambda event: self.load_chat(self.filePath),
            bgcolor=Settings.userTheme[Settings.theme]["ChatButtonBackground"],
            color=Settings.userTheme[Settings.theme]["Text"],
            expand=9
        )
        self.deleteButton = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=lambda event: self.delete_chat(self.filePath),
            # bgcolor=Settings.userTheme[Settings.theme]["ChatButtonBackground"],
            icon_color="#ff0000",#Settings.userTheme[Settings.theme]["Text"],
            visible=False,
            expand=1
        )

        self.row = ft.Row(
            controls=[self.chatButton, self.deleteButton],
            spacing=5
        )
        self.content = self.row
        self.on_hover = self.handle_hover
        self.padding = 5


    def handle_hover(self, e):
        self.deleteButton.visible = e.data  # "true" when hovering
        self.update()


class ChatLabel(ft.Row):
    def __init__(self, userName: str, text: str):
        super().__init__()
        self.label = ft.Markdown(value=text, expand=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, selectable=True, soft_line_break=True)
        self.alignment=ft.MainAxisAlignment.START
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls=[
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(userName)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(userName),
                align=ft.Alignment.TOP_CENTER
            ),
            self.label
        ]

        self.update_theme()

    def get_initials(self, userName) -> str:
        if (len(userName) <= 2):
            return userName
        splitname = userName.split(' ')
        if (len(splitname) > 1):
            return splitname[0][0] + splitname[1][0]
        else:
            return splitname[0][0]

    def get_avatar_color(self, userName):
        if (userName == Settings.userName):
            return Settings.avatarColor
        else:
            return Settings.invert_hex_color(Settings.avatarColor)

    def update_label(self, text):
        self.label.value += text

    def update_theme(self):
        self.label.md_style_sheet = Themes.get_markdown_sheet()
        self.label.code_theme = Themes.get_markdown_codeTheme()
        self.label.code_style_sheet = Themes.get_markdown_codeSheet()



class ChatWindow:
    def __init__(self, page: ft.Page):
        self.saveWindowSize = True
        self.page = page
        self.page.title = "WebSearch AI"
        self.page.theme_mode = ft.ThemeMode.DARK if Settings.theme == "Dark" else ft.ThemeMode.LIGHT
        self.page.window.width = Settings.windowWidth
        self.page.window.height = Settings.windowHeight
        self.page.padding = 0
        self.page.spacing = 0
        self.page.on_close=self.on_close
        page.on_keyboard_event = self.on_keyboard
        self.page.update()

        # Initial Widgets

        self.UserInput = ft.TextField(
            hint_text="How can I help?",
            multiline=True,
            min_lines=1,
            max_lines=4,
            shift_enter=True,
            expand=True,
            on_submit=self.send_input,
            border_width=1,
            focused_border_width=3,
            value="Please Load a Model.",
            disabled=True
        )

        self.SearchButton = ft.IconButton(
            icon=ft.Icons.SEARCH_OFF_OUTLINED,
            icon_color="#FF0000",
            on_click=self.toggle_search,
            tooltip="Enable Web Searching"
        )

        self.SubmitButton = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=ft.Colors.BLUE,
            on_click=self.send_input,
            tooltip="Send Message to AI"
        )

        self.STTButton = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color=ft.Colors.BLUE,
            on_click=self.start_STT,
            tooltip="Start Speech-to-Text"
        )

        self.Chat = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
            padding=25,
        )
        self.NavBar = ft.NavigationRail(
            selected_index=0,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icon(icon=ft.Icons.ADD), label=ft.Text(value="New Chat")),
                ft.NavigationRailDestination(icon=ft.Icon(icon=ft.Icons.HISTORY), label=ft.Text(value="History")),
                ft.NavigationRailDestination(icon=ft.Icon(icon=ft.Icons.UPLOAD), label=ft.Text(value="Load Model")),
                ft.NavigationRailDestination(icon=ft.Icon(icon=ft.Icons.CONTACTS), label=ft.Text(value="Load Character")),
                ft.NavigationRailDestination(icon=ft.Icon(icon=ft.Icons.SETTINGS), label=ft.Text(value="Settings")),
            ],
            # height=500,
            # align=ft.Alignment.CENTER,
            # width=100,
            on_change=self._on_change_NavBar,
            expand=True,
            # indicator_color="#00000000"
        )

        self.ChatLayout = ft.Row([
            self.NavBar,
            ft.Container(expand=1),  # Left Spacer
            ft.Container(
                content=self.Chat,
                # border=ft.Border.all(1, ft.Colors.OUTLINE),
                # border_radius=5,
                # width=900,
                expand=8
            ),
            ft.Container(expand=1),  # Right Spacer
        ], expand=True)

        self.InputRow = ft.Row([
            ft.Container(width=120), # Add Space for NavBar
            ft.Container(expand=1), # Left Spacer
            ft.Container(
                content=ft.Row(
                    controls=[
                        self.STTButton,
                        self.SearchButton,
                        self.UserInput,
                        self.SubmitButton
                    ]
                ),
                expand=8
            ),
            ft.Container(expand=1), # Right Spacer
        ])

        self.layout = ft.Column(
            controls=[
                self.ChatLayout,
                self.InputRow
            ],
            expand=True
        )

        self.page.add(self.layout)

        if (Settings.userName == "SETME#0074"):
            self.UserNameInput = ft.TextField(hint_text="Enter Username...", multiline=False, min_lines=1, max_lines=1, expand=True, on_submit=self.update_username)
            self.page.show_dialog(
                ft.AlertDialog(
                    open=True,
                    modal=True,
                    title=ft.Text("Enter Username"),
                    content=self.UserNameInput,
                    # content=ft.Column(controls=[ft.TextField()], tight=True),
                    actions=[ft.Button(content="Confirm Name", on_click=self.update_username)],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
            )

        self.update_theme()

    # Stops Window Size from being set to 800x628 if the Window is closed before being fully open
    async def windowSizeTimer(self):
        # timeSleep(5)
        await asyncio.sleep(5)
        self.saveWindowSize = True

    def update_username(self, e=None):
        success = False
        if (self.UserNameInput.value is not None):
            if (self.UserNameInput.value.strip() != ""):
                Settings.userName = self.UserNameInput.value
                self.page.pop_dialog()
                self.page.update()
                success = True

        if (not success):
            self.UserNameInput.error = "Username Cannot be Empty!"


    async def set_display(self):
        self.page.update()
        await self.page.window.center()
        self.page.update()

    def start_STT(self, e=None):
        if (Settings.apiModelID == "none"):
            return
        if (not Audio.button_pressed):
            Audio.button_pressed = True
            self.UserInput.disabled = True
            self.STTButton.icon_color = ft.Colors.RED
        else:
            Audio.button_pressed = False
            self.STTButton.icon_color = ft.Colors.BLUE
            self.UserInput.value = self.UserInput.value.strip()
            self.UserInput.disabled = False
        self.page.update()
        if (Audio.whisper is None):
            self.page.run_thread(Audio.load_whisper, self.UserInput, self.page, self.update_ai_response)
            self.page.update()


    def send_input(self, e=None):
        if (Settings.apiModelID == "none"):
            return
        message = self.UserInput.value
        self.UserInput.value = "Thinking..."
        self.UserInput.disabled = True
        self.page.update()
        self.page.run_thread(self.send_message, Settings.userName, message)

    def send_message(self, userName, message):
        self.Chat.controls.append(ChatLabel(userName, message))

        # Build LLM Response
        aiResponse = ChatLabel(Settings.username_AI, "")
        self.Chat.controls.append(aiResponse)
        LLM.generate_response(message, aiResponse.label, self.page, self.update_ai_response)
        self.UserInput.value = ""
        self.UserInput.disabled = False
        self.page.update()

    async def update_ai_response(self):
        self.page.update()

    def toggle_search(self, e=None):
        Settings.doSearch = not Settings.doSearch
        if (Settings.doSearch):
            self.SearchButton.icon = ft.Icons.SEARCH_OUTLINED
            self.SearchButton.icon_color = "#00FF00"
            self.SearchButton.tooltip="Disable Web Searching"
        else:
            self.SearchButton.icon = ft.Icons.SEARCH_OFF_OUTLINED
            self.SearchButton.icon_color = "#FF0000"
            self.SearchButton.tooltip = "Enable Web Searching"

    def _on_change_NavBar(self, e):
        self.page.pop_dialog()
        choice = -1
        if (isinstance(e, int)):
            choice = e
        else:
            choice = e.control.selected_index

        if (choice == 0):
            self.start_new_chat()
        elif (choice == 1):
            self.page.show_dialog(ChatHistoryDialog(self.page, self.load_chat_file))
        elif (choice == 2):
            self.page.show_dialog(LoadModelDialog(self.page, self.UserInput))
        elif (choice == 3):
            self.page.show_dialog(CharacterCardDialog(self.page))
        elif (choice == 4):
            self.page.show_dialog(SettingsDialog(self.page, self.update_theme))
        pass

    def reset_chatWindow(self):
        self.Chat.controls.clear()
        self.Chat.update()
        gc.collect()

    def start_new_chat(self):
        self.reset_chatWindow()
        Settings.messages.clear()

    def load_chat_file(self, chatFile):
        self.reset_chatWindow()
        with open(file=f"src/Chats/{chatFile}") as f:
            history = json.loads(f.read())
            Settings.messages = history
            for message in history:
                if (message["role"] == "AI") or (message["role"] == "assistant"):
                    self.Chat.controls.append(ChatLabel(Settings.username_AI, f"**{Settings.username_AI}:** {message['content']}"))
                elif message["role"] == "user":
                    userMessage = message["content"].split("REAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):")
                    self.Chat.controls.append(ChatLabel(Settings.userName, f"**{Settings.userName}:** {userMessage[0]}"))

    def update_theme(self):
        self.page.bgcolor = Settings.userTheme[Settings.theme]["Background"]

        self.NavBar.bgcolor = Settings.userTheme[Settings.theme]["Background"]
        self.NavBar.indicator_color = Settings.userTheme[Settings.theme]["Background"]

        for child in self.NavBar.destinations:
            if (child.icon is not None):
                child.icon.color = Settings.userTheme[Settings.theme]["Icon"]
                child.label.color = Settings.userTheme[Settings.theme]["Text"]
            child.indicator_color = Settings.userTheme[Settings.theme]["NavBarIndicator"]

        for child in self.Chat.controls:
            if (isinstance(child, ChatLabel)):
                child.update_theme()

        if (Settings.doSearch):
            self.SearchButton.icon.color = Settings.userTheme[Settings.theme]["SearchOn"]
        else:
            self.SearchButton.icon.color = Settings.userTheme[Settings.theme]["SearchOff"]

        self.UserInput.cursor_color = Settings.userTheme[Settings.theme]["UserInputCursor"]
        self.UserInput.border_color = Settings.userTheme[Settings.theme]["UserInputBorder"]
        self.UserInput.focused_border_color = Settings.userTheme[Settings.theme]["UserInputBorderFocus"]
        self.UserInput.color = Settings.userTheme[Settings.theme]["UserInputText"]
        self.UserInput.bgcolor = Settings.userTheme[Settings.theme]["UserInputBackground"]

        self.SubmitButton.icon_color = Settings.userTheme[Settings.theme]["SubmitIcon"]

        self.page.update()

    def on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == Settings.keyboard_shortcuts["Settings"]:
            self._on_change_NavBar(4)
        elif e.key == Settings.keyboard_shortcuts["Send Message"]:
            self.page.pop_dialog()
            self.send_input()
        elif e.key == Settings.keyboard_shortcuts["Toggle STT"]:
            self.page.pop_dialog()
            self.start_STT()
        elif e.key == Settings.keyboard_shortcuts["Toggle Search"]:
            self.page.pop_dialog()
            self.toggle_search()

        # elif e.key == "F2":
        #     self._on_change_NavBar(0)
        # elif e.key == "F3":
        #     self._on_change_NavBar(1)
        # elif e.key == "F4":
        #     self._on_change_NavBar(2)
        # elif e.key == "F5":
        #     self._on_change_NavBar(3)


    def on_close(self):
        if (self.saveWindowSize):
            Settings.windowWidth = self.page.window.width
            Settings.windowHeight = self.page.window.height
        LLM.unload_embedder()
        LLM.unload_model()
        API.cleanup()
        Audio.stop_whisper()
        Settings.save_settings()


async def main(page: ft.Page):
    Settings.load_settings()
    cw = ChatWindow(page)
    await cw.set_display()
    page.run_thread(LLM.load_embedder)
    await cw.windowSizeTimer()


if __name__ == "__main__":
    ft.run(main)
