STYLESHEET = """
QMainWindow {
    background-color: #c0c0c0;
}
QMenuBar {
    background-color: #c0c0c0;
    border-bottom: 2px solid #808080;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #000080;
    color: white;
}
QMenu {
    background-color: #c0c0c0;
    border: 2px solid #808080;
}
QMenu::item:selected {
    background-color: #000080;
    color: white;
}
QToolBar {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-top: none;
    spacing: 4px;
    padding: 2px;
}
QToolButton {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-bottom-color: #404040;
    border-right-color: #404040;
    padding: 4px 8px;
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
}
QToolButton:hover {
    background-color: #d4d4d4;
}
QToolButton:pressed {
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #ffffff;
    border-right-color: #ffffff;
}
QStatusBar {
    background-color: #c0c0c0;
    border-top: 2px solid #808080;
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
}
QSplitter::handle {
    background-color: #c0c0c0;
    width: 4px;
}
QListWidget {
    background-color: #ffffff;
    border: 2px solid #808080;
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #d4d4d4;
    border-right-color: #d4d4d4;
    font-family: "Consolas";
    font-size: 11px;
}
QListWidget::item {
    padding: 4px;
}
QListWidget::item:selected {
    background-color: #000080;
    color: white;
}
QPushButton {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-bottom-color: #404040;
    border-right-color: #404040;
    padding: 4px 12px;
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #d4d4d4;
}
QPushButton:pressed {
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #ffffff;
    border-right-color: #ffffff;
}
QPushButton:disabled {
    color: #808080;
    border-top-color: #d4d4d4;
    border-left-color: #d4d4d4;
}
QLabel {
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
}
QGroupBox {
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
    font-weight: bold;
    border: 2px solid #808080;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-bottom-color: #404040;
    border-right-color: #404040;
    margin-top: 12px;
    padding-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QTabWidget::pane {
    border: 2px solid #808080;
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #d4d4d4;
    border-right-color: #d4d4d4;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-bottom: none;
    padding: 4px 12px;
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
    min-width: 60px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom-color: #ffffff;
}
QTabBar::tab:!selected {
    margin-top: 2px;
}
QScrollBar:vertical {
    background-color: #c0c0c0;
    width: 16px;
    border: 2px solid #808080;
}
QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-bottom-color: #404040;
    border-right-color: #404040;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    height: 16px;
}
QCheckBox {
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
    spacing: 4px;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 2px solid #808080;
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #d4d4d4;
    border-right-color: #d4d4d4;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #000080;
}
QProgressBar {
    border: 2px solid #808080;
    border-top-color: #404040;
    border-left-color: #404040;
    border-bottom-color: #d4d4d4;
    border-right-color: #d4d4d4;
    background-color: #ffffff;
    text-align: center;
    font-family: "Microsoft Sans Serif";
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #000080;
}
"""
