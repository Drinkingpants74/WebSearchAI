# Themes for Users to Select From
import flet as ft
import Settings

default = {
    "Dark": {
        "Base": "#1c1c1c",
        "Close": "#cdcdcd",
        "QuickUnload": "#bb0000",
        "AutoGPUEnabled": "#009900",
        "AutoGPUDisabled": "#990000",
        "GPUSliderOverlayActive": "#cdcdcd44",
        "GPUSliderOverlayDisabled": "#44cdcdcd",
        "GPUSliderActive": "#9900cc",
        "Text": "#cdcdcd",
        "TextBKG": "#000000",
        "Inverse": "#cdcdcd",
        "Icon": "#cdcdcd",
        "Button": "#000000",
        "Sidebar": "#0D0D0D"
    },
    "Light": {
        "Base": "#cdcdcd",
        "Close": "#aa0000",
        "QuickUnload": "#ff3333",
        "AutoGPUEnabled": "#4dff4d",
        "AutoGPUDisabled": "#ff4d4d",
        "GPUSliderOverlayActive": "#1c1c1c44",
        "GPUSliderOverlayDisabled": "#441c1c1c",
        "GPUSliderActive": "#00ffff",
        "Text": "#1c1c1c",
        "TextBKG": "#ffffff",
        "Inverse": "#1c1c1c",
        "Icon": "#1c1c1c",
        "Button": "#ffffff",
        "Sidebar": "#ADADAD"
    }
}

midnight = {
    "Dark": {
        "Base": "#051923",
        "Close": "#cdcdcd",
        "QuickUnload": "#bb0000",
        "AutoGPUEnabled": "#009900",
        "AutoGPUDisabled": "#990000",
        "GPUSliderOverlayActive": "#cdcdcd44",
        "GPUSliderOverlayDisabled": "#44cdcdcd",
        "GPUSliderActive": "#006494",
        "Text": "#00a6fb",
        "TextBKG": "#0a1128",
        "Inverse": "#00a6fb",
        "Icon": "#00a6fb",
        "Button": "#006494",
        "Sidebar": "#0B354B"
    },
    "Light": {
        "Base": "#00a6fb",
        "Close": "#ff3333",#"#aa0000",
        "QuickUnload": "#ff3333",
        "AutoGPUEnabled": "#4dff4d",
        "AutoGPUDisabled": "#ff4d4d",
        "GPUSliderOverlayActive": "#1c1c1c44",
        "GPUSliderOverlayDisabled": "#441c1c1c",
        "GPUSliderActive": "#006494",
        "Text": "#051923",
        "TextBKG": "#bfdbf7",
        "Inverse": "#051923",
        "Icon": "#051923",
        "Button": "#006494",
        "Sidebar": "#2EB9FF"
    }
}


list = { "Default": default, "Midnight": midnight }

def build_md_sheet():
    return ft.MarkdownStyleSheet(
        p_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=16),
        strong_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=16),
        h1_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=48),
        h2_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=32),
        list_bullet_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=16),
    )


def build_changelog_sheet():
    return ft.MarkdownStyleSheet(
        p_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=20),
        strong_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=20),
        h1_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=64),
        h2_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=32),
        list_bullet_text_style=ft.TextStyle(color=Settings.userTheme[Settings.theme]["Text"], size=20),

    )
