from pathlib import Path
import sys
import json
import os
import traceback
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QTimer, Signal, QThread, QEvent,
    Slot, QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QIntValidator,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QWindow)
from PySide6.QtWidgets import (QApplication, QDial, QDialog, QFrame, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QMenu, QTabWidget, QSlider,
    QGridLayout, QLineEdit, QTextEdit, QVBoxLayout, QWidget)

import LLM
import API
import Settings
import Cards

class LLMWorker(QObject):
    user_update = Signal(str)
    token_update = Signal(str)
    finished = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def generate_response(self, prompt):
        full_response = ""
        response_holder = ""
        try:
            response = LLM.generate_response(prompt, self.user_update)
            count = 0
            self.user_update.emit(f"**{Settings.username_AI}:** ")
            for chunk in response:
                chunk = chunk.strip()
                if (not chunk):
                    continue
                if chunk.startswith("data: "):
                    data = chunk[6:]
                    delta = json.loads(data)
                    if (delta['choices'][0]['finish_reason'] is None):
                        if (delta['choices'][0]['delta']['content'] is None):
                            continue
                        full_response += delta['choices'][0]['delta']['content']
                        count += 1
                        if (count >= 5):
                            self.token_update.emit(response_holder + delta['choices'][0]['delta']['content'])
                            response_holder = ""
                            count = 0
                        else:
                            response_holder += delta['choices'][0]['delta']['content']
                    else:
                        self.token_update.emit(response_holder)
                        Settings.messages.append(LLM.create_message(role="assistant", text=full_response))
                        Settings.store_chat_history(chatName=Settings.chatName, messages=Settings.messages)
                        self.finished.emit(True)
                        break
        except Exception as _e:
            traceback.print_exc()
            self.user_update.emit("GENERATION ERROR!")
            self.finished.emit(False)

    # /v1/Responses Endpoint Usage
    # @Slot(str)
    # def generate_response(self, prompt):
    #     full_response = ""
    #     response_holder = ""
    #     try:
    #         # response = API.send_message(self.prompt)
    #         response = LLM.generate_response(prompt, self.user_update)
    #         count = 0
    #         self.user_update.emit(f"**{Settings.username_AI}:** ")
    #         for chunk in response:
    #             chunk = chunk.strip()
    #             if (not chunk):
    #                 continue
    #             if chunk.startswith("data: "):
    #                 data = chunk[6:]
    #                 delta = json.loads(data)
    #                 if (delta['type'] == 'response.output_text.delta'):
    #                     full_response += delta['delta']
    #                     count += 1
    #                     if (count >= 5):
    #                         self.token_update.emit(response_holder + delta['delta'])
    #                         response_holder = ""
    #                         count = 0
    #                     else:
    #                         response_holder += delta['delta']
    #                 elif (delta['type'] == 'response.completed'):
    #                     self.token_update.emit(response_holder)
    #                     Settings.messages.append(LLM.create_message(role="assistant", text=full_response))
    #                     Settings.store_chat_history(chatName=Settings.chatName, messages=Settings.messages)
    #                     self.finished.emit(True)
    #                     break
    #     except Exception as _e:
    #         traceback.print_exc()
    #         self.user_update.emit("GENERATION ERROR!")
    #         self.finished.emit(False)

class MarkdownLabel(QWidget):
    currentLabel = None
    labelType = None
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.VBoxLayout = QVBoxLayout()
        self.VBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.VBoxLayout.setSpacing(0)
        self.setLayout(self.VBoxLayout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.VBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.build_chat(text)


    def build_chat(self, text):
        inCodeBlock = False
        splitText = text.split(" ")
        textSnippet = ""
        for word in splitText:
            # enterCheck = 0
            # for singleWord in word.split("\n"):
            for singleWord in word.splitlines(keepends=True):
                if (singleWord == ""):
                    continue
                else:
                    if ('```' in singleWord):
                        if (inCodeBlock):
                            inCodeBlock = False
                            textSnippet += singleWord
                            # print(f"Code Block: {textSnippet}")
                            self.currentLabel = self.create_code_block(textSnippet)
                            self.layout().addWidget(self.currentLabel)
                            textSnippet = ""
                        else:
                            inCodeBlock = True
                            # print(f"Label: {textSnippet}")
                            self.currentLabel = self.create_text_label(textSnippet)
                            self.layout().addWidget(self.currentLabel)
                            textSnippet = singleWord
                    elif ("{{char}}" in singleWord):
                        # print(f"CHAR: {singleWord}")
                        textSnippet += singleWord.replace("{{char}}", Settings.username_AI) + " "
                    elif ("{{user}}" in singleWord):
                        # print(f"USER: {singleWord}")
                        textSnippet += singleWord.replace("{{user}}", Settings.userName) + " "
                    else:
                        textSnippet += (singleWord + " ")

        self.currentLabel = self.create_text_label(textSnippet)
        self.layout().addWidget(self.currentLabel)
        # print(f"Label: {textSnippet}")
        textSnippet = ""


    def create_text_label(self, text):
        self.labelType = "Label"
        label = QLabel()
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        label.setTextFormat(Qt.TextFormat.MarkdownText)
        label.setText(str(text))
        font = QFont()
        font.setPointSize(18)
        label.setFont(font)
        # label.setContentsMargins(0,0,0,0)
        # label.setStyleSheet("QLabel { margin: 0px; padding: 0px; }")

        return label

    def create_code_block(self, text):
        self.labelType = "TextEdit"
        label = QTextEdit()
        # label.setFrameStyle(QFrame.Shape.NoFrame)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        label.setMarkdown(str(text))
        font = QFont()
        font.setPointSize(18)
        label.setFont(font)
        label.document().setDocumentMargin(5)
        label.setContentsMargins(0,0,0,25)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        label.setStyleSheet("""QTextEdit { background-color: #2b2b2b; border: none; }""")

        def update_size():
            doc_height = label.document().size().height()
            label.setFixedHeight(int(doc_height + 10))

        label.document().documentLayout().documentSizeChanged.connect(update_size)
        update_size()

        return label

    def append_text(self, text):
        if (self.labelType == "TextEdit"):
            self.currentLabel.setMarkdown(self.currentLabel.toMarkdown() + str(text))
        elif (self.labelType == "Label"):
            self.currentLabel.setText(self.currentLabel.text() + str(text))

    def set_text(self, text):
        if (self.labelType == "TextEdit"):
            self.currentLabel.setMarkdown(str(text))
        elif (self.labelType == "Label"):
            self.currentLabel.setText(str(text))


class ChatTextEdit(QTextEdit):
    returnPressed = Signal()
    changeSize = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,50)
        self.textChanged.connect(self.adjust_height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMinimumHeight(54)  # Minimum single-line height
        self.setMaximumHeight(109)  # Cap it so it doesn't grow forever

    def adjust_height(self):
        doc_height = self.document().size().height()
        new_height = min(max(int(doc_height) + 10, 54), 109)
        self.setMinimumHeight(new_height)
        self.setMaximumHeight(new_height)
        # self.setFixedHeight(int(doc_height) + 10)  # +10 for padding
        self.changeSize.emit()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Shift+Enter = new line (default behavior)
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            # Plain Enter = send message
            else:
                self.returnPressed.emit()
                event.accept()
        else:
            super().keyPressEvent(event)


class ChatHistoryButton(QPushButton):
    load_chat = Signal(str)
    delete_chat = Signal(str)

    def __init__(self, filePath, parent=None):
        super().__init__(parent)
        self.file = filePath
        filename_split = filePath.split("_|")
        if (len(filename_split) > 1):
            filename = filename_split[1].replace(".json", "").replace("-", " ").replace("_", " ")
        else:
            filename = filePath.replace(".json", "").replace("-", " ").replace("_", " ")
        self.setObjectName(f"{filename}")
        self.setText(filename)
        self.clicked.connect(self._on_click)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        self.setStyleSheet("""
            QPushButton { text-align: left; padding: 8px; border: none; }
            QPushButton:hover { background: #333; border-radius: 4px; }
        """)

    def _on_click(self):
        self.load_chat.emit(self.file)

    def _show_menu(self, pos):
        menu = QMenu(self)
        delete_act = menu.addAction("Delete")
        if menu.exec(self.mapToGlobal(pos)) == delete_act:
            self.delete_chat.emit(self.file)


class ModelButton(QPushButton):
    load_model = Signal(str)

    def __init__(self, filePath, parent=None):
        super().__init__(parent)
        self.file = filePath
        filename = filePath.replace(".gguf", "").replace("-", " ").replace("_", " ")
        self.setObjectName(f"{filename}")
        self.setText(filename)
        self.clicked.connect(self._on_click)
        self.setStyleSheet("""
            QPushButton { text-align: left; padding: 8px; border: none; }
            QPushButton:hover { background: #333; border-radius: 4px; }
        """)

    def _on_click(self):
        self.load_model.emit(self.file)


class CharacterCardButton(QPushButton):
    load_character = Signal(str)

    def __init__(self, filePath, filename, parent=None):
        super().__init__(parent)
        self.file = filePath
        self.setObjectName(f"{filename}")
        self.setText(filename)
        icon = QPixmap()
        icon.load(filePath)
        size = QSize()
        size.setHeight(96)
        size.setWidth(96)
        self.setIconSize(size)
        self.setIcon(icon)
        self.clicked.connect(self._on_click)
        self.setStyleSheet("""
            QPushButton { text-align: left; padding: 8px; border: none; }
            QPushButton:hover { background: #333; border-radius: 4px; }
        """)

    def _on_click(self):
        self.load_character.emit(self.file)

# Designer Classes

class Ui_ModelPicker(QObject):
    def __init__(self, mainWindow: QDialog) -> None:
        super().__init__()
        self.dialog = mainWindow
        self.setupUi(mainWindow)
        self.APIAddressEdit.setText(f"{Settings.apiPath}")
        self.APIAddressEdit.textChanged.connect(self.update_api)
        self.tabWidget.currentChanged.connect(self.create_modelButtons)
        self.update_api()
        self.create_modelButtons()

    def setupUi(self, ModelPicker):
        if not ModelPicker.objectName():
            ModelPicker.setObjectName(u"ModelPicker")
        ModelPicker.resize(525, 325)
        palette = QPalette()
        brush = QBrush(QColor(28, 28, 28, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        ModelPicker.setPalette(palette)
        self.verticalLayout = QVBoxLayout(ModelPicker)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(ModelPicker)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Tab_Models = QWidget()
        self.Tab_Models.setObjectName(u"Tab_Models")
        self.verticalLayout_3 = QVBoxLayout(self.Tab_Models)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.Tab_Models)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.ModelVBox = QWidget()
        self.ModelVBox.setObjectName(u"ModelVBox")
        self.ModelVBox.setGeometry(QRect(0, 0, 453, 244))
        self.verticalLayout_4 = QVBoxLayout(self.ModelVBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea.setWidget(self.ModelVBox)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.Tab_Models, "")
        self.Tab_API = QWidget()
        self.Tab_API.setObjectName(u"Tab_API")
        self.gridLayout = QGridLayout(self.Tab_API)
        self.gridLayout.setObjectName(u"gridLayout")
        self.APIKeyLabel = QLabel(self.Tab_API)
        self.APIKeyLabel.setObjectName(u"APIKeyLabel")
        font = QFont()
        font.setPointSize(18)
        self.APIKeyLabel.setFont(font)
        self.APIKeyLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout.addWidget(self.APIKeyLabel, 3, 0, 1, 1)

        self.APIKeyEdit = QLineEdit(self.Tab_API)
        self.APIKeyEdit.setObjectName(u"APIKeyEdit")
        palette1 = QPalette()
        brush1 = QBrush(QColor(255, 255, 255, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        brush2 = QBrush(QColor(42, 42, 42, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush2)
        brush3 = QBrush(QColor(35, 35, 35, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush3)
        brush4 = QBrush(QColor(14, 14, 14, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush4)
        brush5 = QBrush(QColor(19, 19, 19, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush5)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush1)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush4)
        brush7 = QBrush(QColor(255, 255, 220, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush6)
        brush8 = QBrush(QColor(255, 255, 255, 127))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush8)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush6)
#endif
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush3)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush5)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush6)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush8)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush6)
#endif
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush2)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush3)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush5)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush6)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush6)
        brush9 = QBrush(QColor(14, 14, 14, 127))
        brush9.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush9)
#endif
        brush10 = QBrush(QColor(20, 20, 20, 255))
        brush10.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush10)
#endif
        self.APIKeyEdit.setPalette(palette1)

        self.gridLayout.addWidget(self.APIKeyEdit, 2, 0, 1, 1)

        self.APIAddressEdit = QLineEdit(self.Tab_API)
        self.APIAddressEdit.setObjectName(u"APIAddressEdit")
        palette2 = QPalette()
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush3)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush4)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush5)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush6)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush4)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush7)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush6)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush8)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush6)
#endif
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush3)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush4)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush5)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush6)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush4)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush7)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush6)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush8)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush6)
#endif
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush3)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush4)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush5)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush4)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush1)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush4)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush6)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush7)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush6)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush10)
#endif
        self.APIAddressEdit.setPalette(palette2)

        self.gridLayout.addWidget(self.APIAddressEdit, 0, 0, 1, 1)

        self.APIAddressLabel = QLabel(self.Tab_API)
        self.APIAddressLabel.setObjectName(u"APIAddressLabel")
        self.APIAddressLabel.setFont(font)
        self.APIAddressLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout.addWidget(self.APIAddressLabel, 1, 0, 1, 1)

        self.tabWidget.addTab(self.Tab_API, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(ModelPicker)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(ModelPicker)
    # setupUi

    def retranslateUi(self, ModelPicker):
        ModelPicker.setWindowTitle(QCoreApplication.translate("ModelPicker", u"Model Picker", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Models), QCoreApplication.translate("ModelPicker", u"Models", None))
        self.APIKeyLabel.setText(QCoreApplication.translate("ModelPicker", u"API Key", None))
        self.APIAddressLabel.setText(QCoreApplication.translate("ModelPicker", u"API Address\n"
"Ex: http://127.0.0.1:PORT", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_API), QCoreApplication.translate("ModelPicker", u"API", None))
    # retranslateUi

    def create_modelButtons(self):
        for _i in range(self.ModelVBox.layout().count()):
            self.ModelVBox.layout().takeAt(0).widget().deleteLater()
        if (Settings.apiMode):
            try:
                for model in API.get_models():
                    button = ModelButton(model)
                    button.load_model.connect(self.set_model_api)
                    self.ModelVBox.layout().addWidget(button)
            except Exception as _e:
                label = QLabel()
                label.setText("API Not Connected")
                self.ModelVBox.layout().addWidget(label)
        else:
            if not os.path.isdir(Settings.modelsPath):
                os.mkdir(Settings.modelsPath)
            for file in os.listdir(Settings.modelsPath):
                if file.endswith(".gguf"):
                    button = ModelButton(file)
                    button.load_model.connect(self.load_model)
                    self.ModelVBox.layout().addWidget(button)


    def update_api(self):
        tempPath = self.APIAddressEdit.text()
        # print(f"TP: {tempPath}")
        if (tempPath.strip() == "") or (tempPath.strip() == "http://127.0.0.1:3774"):
            # print("LOCAL")
            Settings.apiMode = False
            Settings.apiPath = "http://127.0.0.1:3774"
        else:
            # print("API")
            try:
                if (API.get_models(tempPath)):
                    Settings.apiMode = True
                    Settings.apiPath = str(tempPath)
            except Exception as _e:
                Settings.apiMode = False
                Settings.apiPath = "http://127.0.0.1:3774"

    def load_model(self, file: str):
        self.dialog.close()
        LLM.load_model(file)

    def set_model_api(self, file: str):
        self.dialog.close()
        Settings.apiModelID = file
        LLM.unload_model()

class Ui_Settings(QObject):
    character_loaded = Signal()

    def __init__(self, mainWindow: QDialog) -> None:
        super().__init__()
        self.dialog = mainWindow
        self.setupUi(mainWindow)
        self.set_widgets()
        self.set_changelog()
        self.set_cards()

    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(720, 500)
        self.verticalLayout = QVBoxLayout(Settings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Settings)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Tab_App = QWidget()
        self.Tab_App.setObjectName(u"Tab_App")
        self.verticalLayout_2 = QVBoxLayout(self.Tab_App)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.UsernameLabel = QLabel(self.Tab_App)
        self.UsernameLabel.setObjectName(u"UsernameLabel")
        font = QFont()
        font.setPointSize(15)
        self.UsernameLabel.setFont(font)
        self.UsernameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.UsernameLabel)

        self.UsernameInput = QLineEdit(self.Tab_App)
        self.UsernameInput.setObjectName(u"UsernameInput")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.UsernameInput.setPalette(palette)

        self.verticalLayout_2.addWidget(self.UsernameInput)

        self.AvatarColorLabel = QLabel(self.Tab_App)
        self.AvatarColorLabel.setObjectName(u"AvatarColorLabel")
        self.AvatarColorLabel.setFont(font)
        self.AvatarColorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.AvatarColorLabel)

        self.AvatarColorInput = QLineEdit(self.Tab_App)
        self.AvatarColorInput.setObjectName(u"AvatarColorInput")
        palette1 = QPalette()
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.AvatarColorInput.setPalette(palette1)

        self.verticalLayout_2.addWidget(self.AvatarColorInput)

        self.ModelPathLabel = QLabel(self.Tab_App)
        self.ModelPathLabel.setObjectName(u"ModelPathLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ModelPathLabel.sizePolicy().hasHeightForWidth())
        self.ModelPathLabel.setSizePolicy(sizePolicy)
        self.ModelPathLabel.setFont(font)
        self.ModelPathLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.ModelPathLabel)

        self.ModelPathInput = QLineEdit(self.Tab_App)
        self.ModelPathInput.setObjectName(u"ModelPathInput")
        palette2 = QPalette()
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.ModelPathInput.setPalette(palette2)

        self.verticalLayout_2.addWidget(self.ModelPathInput)

        self.BlackListLabel = QLabel(self.Tab_App)
        self.BlackListLabel.setObjectName(u"BlackListLabel")
        self.BlackListLabel.setFont(font)
        self.BlackListLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.BlackListLabel)

        self.BlackListInput = QTextEdit(self.Tab_App)
        self.BlackListInput.setObjectName(u"BlackListInput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.BlackListInput.sizePolicy().hasHeightForWidth())
        self.BlackListInput.setSizePolicy(sizePolicy1)
        palette3 = QPalette()
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.BlackListInput.setPalette(palette3)

        self.verticalLayout_2.addWidget(self.BlackListInput)

        self.tabWidget.addTab(self.Tab_App, "")
        self.Tab_User = QWidget()
        self.Tab_User.setObjectName(u"Tab_User")
        self.verticalLayout_4 = QVBoxLayout(self.Tab_User)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label = QLabel(self.Tab_User)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setPointSize(48)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label)

        self.tabWidget.addTab(self.Tab_User, "")
        self.Tab_Cards = QWidget()
        self.Tab_Cards.setObjectName(u"Tab_Cards")
        self.verticalLayout_3 = QVBoxLayout(self.Tab_Cards)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.CardScroller = QScrollArea(self.Tab_Cards)
        self.CardScroller.setObjectName(u"CardScroller")
        self.CardScroller.setWidgetResizable(True)
        self.CardScrollerContents = QWidget()
        self.CardScrollerContents.setObjectName(u"CardScrollerContents")
        self.CardScrollerContents.setGeometry(QRect(0, 0, 648, 419))
        self.gridLayout_2 = QGridLayout(self.CardScrollerContents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.CardScroller.setWidget(self.CardScrollerContents)

        self.verticalLayout_3.addWidget(self.CardScroller)

        self.tabWidget.addTab(self.Tab_Cards, "")
        self.Tab_Model = QWidget()
        self.Tab_Model.setObjectName(u"Tab_Model")
        self.gridLayout = QGridLayout(self.Tab_Model)
        self.gridLayout.setObjectName(u"gridLayout")
        self.SeedLabel = QLabel(self.Tab_Model)
        self.SeedLabel.setObjectName(u"SeedLabel")
        self.SeedLabel.setFont(font)
        self.SeedLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.SeedLabel, 0, 3, 1, 1)

        self.PenRepeatLabel = QLabel(self.Tab_Model)
        self.PenRepeatLabel.setObjectName(u"PenRepeatLabel")
        self.PenRepeatLabel.setFont(font)
        self.PenRepeatLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.PenRepeatLabel, 9, 0, 1, 1)

        self.SeedInput = QLineEdit(self.Tab_Model)
        self.SeedInput.setObjectName(u"SeedInput")

        self.gridLayout.addWidget(self.SeedInput, 1, 3, 1, 1)

        self.ContextSlider = QSlider(self.Tab_Model)
        self.ContextSlider.setObjectName(u"ContextSlider")
        self.ContextSlider.setMinimum(1)
        self.ContextSlider.setMaximum(32)
        self.ContextSlider.setSingleStep(1)
        self.ContextSlider.setValue(1)
        self.ContextSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.ContextSlider, 3, 3, 1, 1)

        self.BatchSizeSlider = QSlider(self.Tab_Model)
        self.BatchSizeSlider.setObjectName(u"BatchSizeSlider")
        self.BatchSizeSlider.setMinimum(1)
        self.BatchSizeSlider.setMaximum(16)
        self.BatchSizeSlider.setValue(4)
        self.BatchSizeSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.BatchSizeSlider, 8, 3, 1, 1)

        self.TopPSlider = QSlider(self.Tab_Model)
        self.TopPSlider.setObjectName(u"TopPSlider")
        self.TopPSlider.setMaximum(100)
        self.TopPSlider.setSingleStep(5)
        self.TopPSlider.setValue(95)
        self.TopPSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.TopPSlider, 6, 0, 1, 1)

        self.TemperatureLabel = QLabel(self.Tab_Model)
        self.TemperatureLabel.setObjectName(u"TemperatureLabel")
        font2 = QFont()
        font2.setFamilies([u".AppleSystemUIFont"])
        font2.setPointSize(15)
        self.TemperatureLabel.setFont(font2)
        self.TemperatureLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.TemperatureLabel, 2, 0, 1, 2)

        self.PenRepeatSlider = QSlider(self.Tab_Model)
        self.PenRepeatSlider.setObjectName(u"PenRepeatSlider")
        self.PenRepeatSlider.setMaximum(40)
        self.PenRepeatSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.PenRepeatSlider, 10, 0, 1, 1)

        self.GPULayerLabel = QLabel(self.Tab_Model)
        self.GPULayerLabel.setObjectName(u"GPULayerLabel")
        self.GPULayerLabel.setFont(font)
        self.GPULayerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.GPULayerLabel, 0, 0, 1, 1)

        self.TemperatureSlider = QSlider(self.Tab_Model)
        self.TemperatureSlider.setObjectName(u"TemperatureSlider")
        self.TemperatureSlider.setMinimum(1)
        self.TemperatureSlider.setMaximum(40)
        self.TemperatureSlider.setSingleStep(1)
        self.TemperatureSlider.setValue(20)
        self.TemperatureSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.TemperatureSlider, 3, 0, 1, 1)

        self.ContextLabel = QLabel(self.Tab_Model)
        self.ContextLabel.setObjectName(u"ContextLabel")
        self.ContextLabel.setFont(font)
        self.ContextLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.ContextLabel, 2, 2, 1, 2)

        self.TopKSlider = QSlider(self.Tab_Model)
        self.TopKSlider.setObjectName(u"TopKSlider")
        self.TopKSlider.setMinimum(10)
        self.TopKSlider.setMaximum(100)
        self.TopKSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.TopKSlider, 8, 0, 1, 1)

        self.GPULayersSlider = QSlider(self.Tab_Model)
        self.GPULayersSlider.setObjectName(u"GPULayersSlider")
        self.GPULayersSlider.setMinimum(-1)
        self.GPULayersSlider.setValue(-1)
        self.GPULayersSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.GPULayersSlider, 1, 0, 1, 1)

        self.TopPLabel = QLabel(self.Tab_Model)
        self.TopPLabel.setObjectName(u"TopPLabel")
        self.TopPLabel.setFont(font)
        self.TopPLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.TopPLabel, 5, 0, 1, 1)

        self.BatchSizeLabel = QLabel(self.Tab_Model)
        self.BatchSizeLabel.setObjectName(u"BatchSizeLabel")
        self.BatchSizeLabel.setFont(font)
        self.BatchSizeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.BatchSizeLabel, 7, 3, 1, 1)

        self.TopKLabel = QLabel(self.Tab_Model)
        self.TopKLabel.setObjectName(u"TopKLabel")
        self.TopKLabel.setFont(font)
        self.TopKLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.TopKLabel, 7, 0, 1, 1)

        self.PenFreqSlider = QSlider(self.Tab_Model)
        self.PenFreqSlider.setObjectName(u"PenFreqSlider")
        self.PenFreqSlider.setMaximum(40)
        self.PenFreqSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.PenFreqSlider, 10, 3, 1, 1)

        self.PenFreqLabel = QLabel(self.Tab_Model)
        self.PenFreqLabel.setObjectName(u"PenFreqLabel")
        self.PenFreqLabel.setFont(font)
        self.PenFreqLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.PenFreqLabel, 9, 3, 1, 1)

        self.MinPSlider = QSlider(self.Tab_Model)
        self.MinPSlider.setObjectName(u"MinPSlider")
        self.MinPSlider.setMaximum(100)
        self.MinPSlider.setSingleStep(5)
        self.MinPSlider.setValue(5)
        self.MinPSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.MinPSlider, 6, 3, 1, 1)

        self.MinPLabel = QLabel(self.Tab_Model)
        self.MinPLabel.setObjectName(u"MinPLabel")
        self.MinPLabel.setFont(font)
        self.MinPLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.MinPLabel, 5, 3, 1, 1)

        self.tabWidget.addTab(self.Tab_Model, "")
        self.Tab_Changelog = QWidget()
        self.Tab_Changelog.setObjectName(u"Tab_Changelog")
        self.verticalLayout_5 = QVBoxLayout(self.Tab_Changelog)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.scrollArea = QScrollArea(self.Tab_Changelog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 648, 419))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.ChangelogLabel = QLabel(self.scrollAreaWidgetContents)
        self.ChangelogLabel.setObjectName(u"ChangelogLabel")
        self.ChangelogLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_6.addWidget(self.ChangelogLabel)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_5.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.Tab_Changelog, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(Settings)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"Settings", None))
        self.UsernameLabel.setText(QCoreApplication.translate("Settings", u"Username", None))
        self.AvatarColorLabel.setText(QCoreApplication.translate("Settings", u"Avatar Color", None))
        self.ModelPathLabel.setText(QCoreApplication.translate("Settings", u"Models Path", None))
        self.BlackListLabel.setText(QCoreApplication.translate("Settings", u"URL BlackList", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_App), QCoreApplication.translate("Settings", u"App Settings", None))
        self.label.setText(QCoreApplication.translate("Settings", u"COMING SOON", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_User), QCoreApplication.translate("Settings", u"User Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Cards), QCoreApplication.translate("Settings", u"Character Cards", None))
        self.SeedLabel.setText(QCoreApplication.translate("Settings", u"Seed", None))
        self.PenRepeatLabel.setText(QCoreApplication.translate("Settings", u"Repeat Penalty", None))
        self.SeedInput.setPlaceholderText(QCoreApplication.translate("Settings", u"Random Seed: -1", None))
        self.TemperatureLabel.setText(QCoreApplication.translate("Settings", u"Temperature", None))
        self.GPULayerLabel.setText(QCoreApplication.translate("Settings", u"GPU Layers", None))
        self.ContextLabel.setText(QCoreApplication.translate("Settings", u"Context", None))
        self.TopPLabel.setText(QCoreApplication.translate("Settings", u"Top P", None))
        self.BatchSizeLabel.setText(QCoreApplication.translate("Settings", u"Batch Size", None))
        self.TopKLabel.setText(QCoreApplication.translate("Settings", u"Top K", None))
        self.PenFreqLabel.setText(QCoreApplication.translate("Settings", u"Frequency Penalty", None))
        self.MinPLabel.setText(QCoreApplication.translate("Settings", u"Min P", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Model), QCoreApplication.translate("Settings", u"Model Settings", None))
        self.ChangelogLabel.setText(QCoreApplication.translate("Settings", u"Changelog", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_Changelog), QCoreApplication.translate("Settings", u"Changelog", None))
    # retranslateUi


    def set_widgets(self):
        self.AvatarColorInput.setText(str(Settings.avatarColor))
        self.UsernameInput.setText(str(Settings.userName))
        self.ModelPathInput.setText(str(Settings.modelsPath))

        self.AvatarColorInput.textChanged.connect(self.update_user_settings)
        self.UsernameInput.textChanged.connect(self.update_user_settings)
        self.ModelPathInput.textChanged.connect(self.update_user_settings)

        if (Settings.gpuLayers == -1):
            self.GPULayerLabel.setText("GPU Layers: Auto")
        else:
            self.GPULayerLabel.setText(f"GPU Layers: {Settings.gpuLayers}")
        self.GPULayersSlider.setValue(int(Settings.gpuLayers))
        self.TemperatureLabel.setText(f"Temperature: {Settings.temperature}")
        self.TemperatureSlider.setValue(int(Settings.temperature * 20.0))
        self.ContextLabel.setText(f"Context: {Settings.ctxSize}")
        self.ContextSlider.setValue(int(Settings.ctxSize / 4096.0))
        self.TopPLabel.setText(f"Top P: {Settings.top_P}")
        self.TopPSlider.setValue(int(Settings.top_P * 100.0))
        self.TopKLabel.setText(f"Top K: {Settings.top_K}")
        self.TopKSlider.setValue(int(Settings.top_K))
        self.MinPLabel.setText(f"Min P: {Settings.min_P}")
        self.MinPSlider.setValue(int(Settings.min_P * 100.0))
        self.PenRepeatLabel.setText(f"Repeat Penalty: {Settings.penalty_repeat}")
        self.PenRepeatSlider.setValue(int(Settings.penalty_repeat * 20.0))
        self.PenFreqLabel.setText(f"Freq Penalty: {Settings.penalty_frequency}")
        self.PenFreqSlider.setValue(int(Settings.penalty_frequency * 20.0))
        self.BatchSizeLabel.setText(f"Batch Size: {Settings.batchSize}")
        self.BatchSizeSlider.setValue(int(Settings.batchSize / 128.0))

        self.GPULayersSlider.valueChanged.connect(self.update_model_settings)
        self.TemperatureSlider.valueChanged.connect(self.update_model_settings)
        self.ContextSlider.valueChanged.connect(self.update_model_settings)
        self.TopPSlider.valueChanged.connect(self.update_model_settings)
        self.TopKSlider.valueChanged.connect(self.update_model_settings)
        self.MinPSlider.valueChanged.connect(self.update_model_settings)
        self.PenRepeatSlider.valueChanged.connect(self.update_model_settings)
        self.PenFreqSlider.valueChanged.connect(self.update_model_settings)
        self.BatchSizeSlider.valueChanged.connect(self.update_model_settings)

        self.SeedInput.setValidator(QIntValidator())
        self.SeedInput.setText(str(Settings.seed))
        self.SeedInput.textChanged.connect(self.update_user_settings)

        blacklistText = ""
        for url in Settings.userBlacklist:
            blacklistText += f"{url}, "

        self.BlackListInput.setText(blacklistText)

    def set_widgets_text(self):
        if (Settings.gpuLayers == -1):
            self.GPULayerLabel.setText("GPU Layers: Auto")
        else:
            self.GPULayerLabel.setText(f"GPU Layers: {Settings.gpuLayers}")
        self.TemperatureLabel.setText(f"Temperature: {Settings.temperature}")
        self.ContextLabel.setText(f"Context: {Settings.ctxSize}")
        self.TopPLabel.setText(f"Top P: {Settings.top_P}")
        self.TopKLabel.setText(f"Top K: {Settings.top_K}")
        self.MinPLabel.setText(f"Min P: {Settings.min_P}")
        self.PenRepeatLabel.setText(f"Repeat Penalty: {Settings.penalty_repeat}")
        self.PenFreqLabel.setText(f"Freq Penalty: {Settings.penalty_frequency}")
        self.BatchSizeLabel.setText(f"Batch Size: {Settings.batchSize}")

    def update_model_settings(self):
        Settings.gpuLayers = int(self.GPULayersSlider.value())
        Settings.temperature = round(float(self.TemperatureSlider.value() * 0.05), 2)
        Settings.ctxSize = self.ContextSlider.value() * 4 * 1024
        Settings.top_P = round(float(self.TopPSlider.value() / 100.0), 2)
        Settings.top_K = int(self.TopKSlider.value())
        Settings.min_P = round(float(self.MinPSlider.value() / 100.0), 2)
        Settings.penalty_repeat = round(float(self.PenRepeatSlider.value() * 0.05), 2)
        Settings.penalty_frequency = round(float(self.PenFreqSlider.value() * 0.05), 2)
        Settings.batchSize = int(self.BatchSizeSlider.value() * 128)
        self.set_widgets_text()

    def update_user_settings(self):
        if (self.SeedInput.text() != "-"):
            Settings.seed = int(self.SeedInput.text())
        if (os.path.isdir(self.ModelPathInput.text())):
            Settings.modelsPath = self.ModelPathInput.text()
        Settings.userName = self.UsernameInput.text()
        Settings.avatarColor = self.AvatarColorInput.text()

    def set_changelog(self):
        with open("changelog", "r") as cl:
            self.ChangelogLabel.setTextFormat(Qt.TextFormat.MarkdownText)
            self.ChangelogLabel.setText(cl.read())

    def set_cards(self):
        if not os.path.isdir(Settings.cardsPath):
            os.mkdir(Settings.cardsPath)
        fileList = []
        for file in os.listdir(Settings.cardsPath):
            if file.endswith(".png"):
                fileList.append(file)

        fileList.sort()
        row = 0
        col = 0
        for card in fileList:
            button = CharacterCardButton(f"{Settings.cardsPath}{card}", Cards.get_card_name(f"{Settings.cardsPath}{card}"))
            button.load_character.connect(self.load_char_card)
            self.CardScrollerContents.layout().addWidget(button, row, col)
            col += 1
            if (col == 3):
                col = 0
                row += 1

    def load_char_card(self, filepath):
        # print(filepath)
        if (Cards.load_card(filepath)):
            self.character_loaded.emit()
            self.dialog.close()




class Ui_ChatWindow(QObject):
    firstResize = False
    generate_response = Signal(str)
    def __init__(self, MainWindow) -> None:
        super().__init__()
        self.setupUi(MainWindow)
        self.ChatContainerContents.setLayout(QVBoxLayout())
        self.ChatContainerContents.layout().setContentsMargins(0,0,0,200)
        self.ChatContainerContents.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ChatHistoryScrollContents.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ChatContainerContents.layout().setSpacing(15)
        self.setup_chatHistory_Buttons()
        self.mainWindow = MainWindow
        self.mainWindow.installEventFilter(self)
        self.toggle_searchButton()
        self.SubmitButton.setIcon(QIcon("Icons/Send_Message.svg"))

        self.LLMThread = QThread()
        self.LLMWorker = LLMWorker()
        self.LLMWorker.moveToThread(self.LLMThread)
        self.LLMWorker.user_update.connect(self.set_assistant_label)
        self.LLMWorker.token_update.connect(self.update_assistant_label)
        self.LLMWorker.finished.connect(self.response_done)
        self.generate_response.connect(self.LLMWorker.generate_response)
        self.LLMThread.start()

        self.UserInput.returnPressed.connect(self.send_message)
        self.SubmitButton.clicked.connect(self.send_message)
        self.UserInput.changeSize.connect(self.resize_userInput)
        self.NewChatButton.clicked.connect(lambda: self.load_prev_chat("None"))
        self.ModelPickerButton.clicked.connect(self.launch_modelPicker)
        self.SettingsButton.clicked.connect(self.launch_settings)
        self.SearchButton.clicked.connect(self.toggle_search)

        QTimer.singleShot(50, self.resize_input_panel)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        palette = QPalette()
        brush = QBrush(QColor(28, 28, 28, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        MainWindow.setPalette(palette)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.UserInputPanel = QFrame(self.centralwidget)
        self.UserInputPanel.setObjectName(u"UserInputPanel")
        self.UserInputPanel.setGeometry(QRect(350, 590, 860, 54))
        palette1 = QPalette()
        brush1 = QBrush(QColor(50, 50, 50, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.UserInputPanel.setPalette(palette1)
        self.UserInputPanel.setAutoFillBackground(True)
        self.UserInputPanel.setFrameShape(QFrame.Shape.NoFrame)
        self.UserInputPanel.setFrameShadow(QFrame.Shadow.Plain)
        self.UserInputPanel.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.UserInputPanel)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.SearchButton = QPushButton(self.UserInputPanel)
        self.SearchButton.setObjectName(u"SearchButton")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch))
        self.SearchButton.setIcon(icon)
        self.SearchButton.setIconSize(QSize(32, 32))
        self.SearchButton.setFlat(True)

        self.horizontalLayout.addWidget(self.SearchButton)

        # self.UserInput = QTextEdit(self.UserInputPanel)
        self.UserInput = ChatTextEdit(self.UserInputPanel)
        self.UserInput.setObjectName(u"UserInput")
        palette2 = QPalette()
        brush2 = QBrush(QColor(23, 23, 23, 0))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush2)
        self.UserInput.setPalette(palette2)
        self.UserInput.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.UserInput)

        self.SubmitButton = QPushButton(self.UserInputPanel)
        self.SubmitButton.setObjectName(u"SubmitButton")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailSend))
        self.SubmitButton.setIcon(icon1)
        self.SubmitButton.setIconSize(QSize(32, 32))
        self.SubmitButton.setFlat(True)

        self.horizontalLayout.addWidget(self.SubmitButton)

        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.MainWidget = QWidget(self.centralwidget)
        self.MainWidget.setObjectName(u"MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.MainWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.SideBarPanel = QWidget(self.MainWidget)
        self.SideBarPanel.setObjectName(u"SideBarPanel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.SideBarPanel.sizePolicy().hasHeightForWidth())
        self.SideBarPanel.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.SideBarPanel)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.NewChatButton = QPushButton(self.SideBarPanel)
        self.NewChatButton.setObjectName(u"NewChatButton")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew))
        self.NewChatButton.setIcon(icon2)

        self.verticalLayout.addWidget(self.NewChatButton)

        self.ChatHistoryScroll = QScrollArea(self.SideBarPanel)
        self.ChatHistoryScroll.setObjectName(u"ChatHistoryScroll")
        sizePolicy.setHeightForWidth(self.ChatHistoryScroll.sizePolicy().hasHeightForWidth())
        self.ChatHistoryScroll.setSizePolicy(sizePolicy)
        self.ChatHistoryScroll.setFrameShape(QFrame.Shape.Box)
        self.ChatHistoryScroll.setLineWidth(1)
        self.ChatHistoryScroll.setWidgetResizable(True)
        self.ChatHistoryScrollContents = QWidget()
        self.ChatHistoryScrollContents.setObjectName(u"ChatHistoryScrollContents")
        self.ChatHistoryScrollContents.setGeometry(QRect(0, 0, 245, 578))
        sizePolicy.setHeightForWidth(self.ChatHistoryScrollContents.sizePolicy().hasHeightForWidth())
        self.ChatHistoryScrollContents.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.ChatHistoryScrollContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.ChatLabelPersist = QLabel(self.ChatHistoryScrollContents)
        self.ChatLabelPersist.setObjectName(u"ChatLabelPersist")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.ChatLabelPersist.sizePolicy().hasHeightForWidth())
        self.ChatLabelPersist.setSizePolicy(sizePolicy2)
        self.ChatLabelPersist.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ChatLabelPersist.setFrameShape(QFrame.Shape.NoFrame)
        self.ChatLabelPersist.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_2.addWidget(self.ChatLabelPersist)

        self.ChatHistoryScroll.setWidget(self.ChatHistoryScrollContents)

        self.verticalLayout.addWidget(self.ChatHistoryScroll)

        self.ModelPickerButton = QPushButton(self.SideBarPanel)
        self.ModelPickerButton.setObjectName(u"ModelPickerButton")

        self.verticalLayout.addWidget(self.ModelPickerButton)

        self.SettingsButton = QPushButton(self.SideBarPanel)
        self.SettingsButton.setObjectName(u"SettingsButton")
        self.SettingsButton.setMinimumSize(QSize(0, 0))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemShutdown))
        self.SettingsButton.setIcon(icon3)
        self.SettingsButton.setIconSize(QSize(16, 16))

        self.verticalLayout.addWidget(self.SettingsButton)


        self.horizontalLayout_2.addWidget(self.SideBarPanel)

        self.ChatContainer = QScrollArea(self.MainWidget)
        self.ChatContainer.setObjectName(u"ChatContainer")
        self.ChatContainer.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(4)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.ChatContainer.sizePolicy().hasHeightForWidth())
        self.ChatContainer.setSizePolicy(sizePolicy3)
        palette3 = QPalette()
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush2)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush2)
        self.ChatContainer.setPalette(palette3)
        self.ChatContainer.setFrameShadow(QFrame.Shadow.Plain)
        self.ChatContainer.setLineWidth(0)
        self.ChatContainer.setWidgetResizable(True)
        self.ChatContainerContents = QWidget()
        self.ChatContainerContents.setObjectName(u"ChatContainerContents")
        self.ChatContainerContents.setGeometry(QRect(0, 0, 995, 694))
        sizePolicy.setHeightForWidth(self.ChatContainerContents.sizePolicy().hasHeightForWidth())
        self.ChatContainerContents.setSizePolicy(sizePolicy)
        self.ChatContainer.setWidget(self.ChatContainerContents)

        self.horizontalLayout_2.addWidget(self.ChatContainer)


        self.verticalLayout_3.addWidget(self.MainWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.MainWidget.raise_()
        self.UserInputPanel.raise_()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WebSearch AI", None))
        self.SearchButton.setText("")
        self.SubmitButton.setText("")
        self.NewChatButton.setText(QCoreApplication.translate("MainWindow", u"New Chat", None))
        self.ChatLabelPersist.setText(QCoreApplication.translate("MainWindow", u"Previous Chats:", None))
        self.ModelPickerButton.setText(QCoreApplication.translate("MainWindow", u"Load Model", None))
        self.SettingsButton.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

    def send_message(self):
        self.UserInput.setReadOnly(True)
        userPrompt = self.UserInput.document().toPlainText()
        self.build_user_chat(self.UserInput.document().toMarkdown())
        self.UserInput.setText("Thinking...")
        self.resize_userInput()
        self.ai_textLabel = self.build_AI_chat("")
        self.generate_response.emit(userPrompt)
        # self.LLMWorker.generate_response(userPrompt)

    def build_user_chat(self, message: str):
        textWidget = QWidget()
        textWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        textHBox = QHBoxLayout()
        textHBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        textHBox.setSpacing(5)
        textHBox.setContentsMargins(5,5,5,5)
        icon_label = QLabel(self.get_userInitials())
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Settings.avatarColor};
                color: white;
                border-radius: 16px;
                font-weight: bold;
            }}
        """)
        text = MarkdownLabel(f"**{Settings.userName}:** {message}")
        textHBox.layout().addWidget(icon_label)
        textHBox.setAlignment(icon_label, Qt.AlignmentFlag.AlignTop)
        textHBox.setAlignment(text, Qt.AlignmentFlag.AlignTop)
        textHBox.layout().addWidget(text)
        textWidget.setLayout(textHBox)
        textHBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        textHBox.setSizeConstraints(QLayout.SizeConstraint.SetMaximumSize, QLayout.SizeConstraint.SetMinAndMaxSize)
        self.ChatContainerContents.layout().addWidget(textWidget)

    def build_AI_chat(self, message: str):
        textWidget = QWidget()
        textWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        textHBox = QHBoxLayout()
        textHBox.setSpacing(5)
        textHBox.setContentsMargins(5,5,5,5)
        icon_label = QLabel()
        if (Settings.cardPath is not None):
            icon_label.setPixmap(QPixmap(Settings.cardPath).scaled(32, 32))
        else:
            icon_label.setText("AI")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(32, 32)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Settings.invert_hex_color(Settings.avatarColor)};
                    color: white;
                    border-radius: 16px;
                    font-weight: bold;
                }}
            """)

        text = MarkdownLabel(f"**{Settings.username_AI}:** {message}")
        textHBox.layout().addWidget(icon_label)
        textHBox.setAlignment(icon_label, Qt.AlignmentFlag.AlignTop)
        textHBox.setAlignment(text, Qt.AlignmentFlag.AlignTop)
        textHBox.layout().addWidget(text)
        # textHBox.addStretch(1)
        textWidget.setLayout(textHBox)
        textHBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        textHBox.setSizeConstraints(QLayout.SizeConstraint.SetMaximumSize, QLayout.SizeConstraint.SetMinAndMaxSize)
        self.ChatContainerContents.layout().addWidget(textWidget)
        return text

    def update_assistant_label(self, text):
        self.ai_textLabel.append_text(text)

    def set_assistant_label(self, text):
        self.ai_textLabel.set_text(text)

    def response_done(self, value):
        if (value):
            self.setup_chatHistory_Buttons()
            self.UserInput.setText("")
            self.resize_userInput()
            self.UserInput.setReadOnly(False)

    def resize_userInput(self):
        self.UserInputPanel.setFixedHeight(self.UserInput.height() + 10)

    def get_userInitials(self) -> str:
        splitname = Settings.userName.split(" ")
        if (len(splitname) > 1):
            return splitname[0][0] + splitname[1][0]
        else:
            return splitname[0][0]

    def setup_chatHistory_Buttons(self):
        for _i in range(self.ChatHistoryScrollContents.layout().count() - 1):
            self.ChatHistoryScrollContents.layout().takeAt(1).widget().deleteLater()
        if not os.path.isdir("Chats/"):
            os.mkdir("Chats/")
        fileList = []
        for file in os.listdir("Chats/"):
            if file.endswith(".json"):
                fileList.append(file)
        fileList.sort(reverse=True)
        for file in fileList:
            button = ChatHistoryButton(file)
            button.load_chat.connect(self.load_prev_chat)
            button.delete_chat.connect(self.delete_chatHistory_file)
            self.ChatHistoryScrollContents.layout().addWidget(button)

    def delete_chatHistory_file(self, file):
        Path(f"Chats/{file}").unlink(missing_ok=True)
        self.setup_chatHistory_Buttons()

    def load_prev_chat(self, filename: str):
        for _i in range(self.ChatContainerContents.layout().count()):
            self.ChatContainerContents.layout().takeAt(0).widget().deleteLater()

        if (filename != "None"):
            with open(f"Chats/{filename}", "rt") as f:
                history = json.loads(f.read())
                Settings.messages = history
                for message in history:
                    if (message["role"] == "AI") or (message["role"] == "assistant"):
                        MarkdownLabel(message["content"])
                        self.build_AI_chat(message["content"])
                    elif message["role"] == "user":
                        userMessage = message["content"].split("REAL-TIME WEB SEARCH RESULTS (FACTUAL INFORMATION):")
                        self.build_user_chat(userMessage[0])
        else:
            Settings.chatName = "Unnamed Chat"
            Settings.messages.clear()

    def toggle_search(self):
        Settings.doSearch = not Settings.doSearch
        self.toggle_searchButton()

    def toggle_searchButton(self):
        if (Settings.doSearch):
            self.SearchButton.setIcon(QIcon("Icons/Search_ON.svg"))
        else:
            self.SearchButton.setIcon(QIcon("Icons/Search_OFF.svg"))

    def launch_modelPicker(self):
        self.modelDialog = QDialog()
        self.dialogWindow = Ui_ModelPicker(self.modelDialog)
        self.modelDialog.exec()

    def launch_settings(self):
        self.settingsDialog = QDialog()
        self.settingsWindow = Ui_Settings(self.settingsDialog)
        self.settingsWindow.character_loaded.connect(self.load_character_card)
        self.settingsDialog.exec()

    def load_character_card(self):
        # Clear Chat
        for _i in range(self.ChatContainerContents.layout().count()):
            self.ChatContainerContents.layout().takeAt(0).widget().deleteLater()
        # Set First Message
        self.build_AI_chat(str(Settings.firstMessage))
        pass

    def eventFilter(self, obj, event):
        if (obj == self.mainWindow) and (event.type() == QEvent.Type.Resize) and (not self.firstResize):
            self.firstResize = True
        elif (obj == self.mainWindow) and (event.type() == QEvent.Type.Resize) and (self.firstResize):
            self.resize_input_panel()
            # for _i in range(self.ChatContainerContents.layout().count()):
            #     print(self.ChatContainerContents.layout().takeAt(0).widget())

        return False

    def resize_input_panel(self):
        x = self.SideBarPanel.width() + (self.mainWindow.width() * .1)
        y = (self.mainWindow.height() * .8)
        w = (self.mainWindow.width() - self.SideBarPanel.width()) * 0.75
        self.UserInputPanel.setGeometry(int(x),int(y),int(w),int(self.UserInput.height() + 10))

    def closeEvent(self):
        LLM.unload_embedder()
        LLM.unload_model()
        Settings.save_settings()
        self.LLMThread.quit()
        self.LLMThread.wait()

if __name__ == "__main__":
    Settings.load_settings()

    app = QApplication([])
    app.setApplicationName("WebSearch AI")
    app.setApplicationDisplayName("WebSearch AI")
    # app.setWindowIcon(QIcon("Icons/icon.png")) # Create New Icon
    mainWindow = QMainWindow()
    chatWindow = Ui_ChatWindow(mainWindow)
    mainWindow.show()
    app.aboutToQuit.connect(chatWindow.closeEvent)

    LLM.load_embedder()

    sys.exit(app.exec())
