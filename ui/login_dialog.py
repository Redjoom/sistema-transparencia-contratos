from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication,
)
from PyQt5.QtCore import Qt
from core.auth import validate


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIT — Inicio de Sesión")
        self.setFixedSize(380, 260)
        self._user = None
        self._build_ui()
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #c0c0c0;
            }
            QLabel {
                font-family: "Microsoft Sans Serif";
                font-size: 11px;
            }
            QLineEdit {
                font-family: "Consolas";
                font-size: 11px;
                padding: 4px;
                border: 2px solid #808080;
                border-top-color: #404040;
                border-left-color: #404040;
                border-bottom-color: #d4d4d4;
                border-right-color: #d4d4d4;
                background-color: #ffffff;
            }
            QPushButton {
                font-family: "Microsoft Sans Serif";
                font-size: 11px;
                padding: 4px 16px;
                background-color: #c0c0c0;
                border: 2px solid #808080;
                border-top-color: #ffffff;
                border-left-color: #ffffff;
                border-bottom-color: #404040;
                border-right-color: #404040;
                min-height: 22px;
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
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("SISTEMA INSTITUCIONAL\nDE TRANSPARENCIA")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Usuario:"))
        self._input_user = QLineEdit()
        self._input_user.setPlaceholderText("admin")
        layout.addWidget(self._input_user)

        layout.addWidget(QLabel("Contraseña:"))
        self._input_pass = QLineEdit()
        self._input_pass.setEchoMode(QLineEdit.Password)
        self._input_pass.setPlaceholderText("admin")
        layout.addWidget(self._input_pass)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_login = QPushButton("Ingresar")
        btn_login.setDefault(True)
        btn_login.clicked.connect(self._on_login)
        btn_layout.addWidget(btn_login)
        layout.addLayout(btn_layout)

        self._input_user.returnPressed.connect(self._input_pass.setFocus)
        self._input_pass.returnPressed.connect(btn_login.click)

    def _on_login(self):
        username = self._input_user.text().strip()
        password = self._input_pass.text()
        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", "Ingresa usuario y contraseña.")
            return
        user = validate(username, password)
        if not user:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")
            return
        self._user = user
        self.accept()

    def get_user(self):
        return self._user
