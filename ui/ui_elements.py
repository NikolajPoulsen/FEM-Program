from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QToolButton, QStyle, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QTabWidget
from enum import Enum, auto


class ToolButton(QToolButton):
    class ButtonStyle(Enum):
        LARGE = auto()
        SMALL = auto()
        TINY = auto()

    def __init__(self, text: str, style: "ToolButton.ButtonStyle", tooltip: str = "", checkable: bool = False) -> None:
        super().__init__()

        self.setText(str(text))
        self.setCheckable(checkable)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setIcon(icon)

        match style:
            case ToolButton.ButtonStyle.LARGE:
                self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                self.setIconSize(QSize(48, 48))
                self.setFixedSize(80, 80)

            case ToolButton.ButtonStyle.SMALL:
                self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                self.setIconSize(QSize(20, 20))
                self.setFixedSize(80, 24)

            case ToolButton.ButtonStyle.TINY:
                self.setToolButtonStyle(Qt.ToolButtonIconOnly)
                self.setIconSize(QSize(20, 20))
                self.setFixedSize(24, 24)


class SmallButtonColumn(QWidget):
    def __init__(self, buttons: list[ToolButton]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for btn in buttons:
            layout.addWidget(btn)

        layout.addStretch()


class TinyButtonRow(QWidget):
    def __init__(self, buttons: list[ToolButton]):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        for btn in buttons:
            layout.addWidget(btn)

        layout.addStretch()

class RibbonSeparator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFixedHeight(90)
        self.setStyleSheet("margin-left: 5px; margin-right: 5px;")

class RibbonGroup(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 0)
        self.main_layout.setSpacing(2)

        self.content_layout = QHBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        font = self.title_label.font()
        font.setPointSize(8)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: gray;")

        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addWidget(self.title_label)

    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)


class Ribbon(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QTabWidget::pane { border-top: 1px solid lightgray; }")
        self.setFixedHeight(130)

    def add_ribbon_tab(self, title: str) -> QHBoxLayout:
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        self.addTab(tab_widget, title)
        return tab_layout