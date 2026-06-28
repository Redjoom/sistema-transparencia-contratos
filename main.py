import sys
from PyQt5.QtWidgets import QApplication
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Institucional de Transparencia")
    app.setApplicationVersion("1.0")
    app.setStyle("Fusion")

    login = LoginDialog()
    if login.exec_() != LoginDialog.Accepted:
        sys.exit(0)

    user = login.get_user()
    window = MainWindow(user)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
