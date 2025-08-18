import sys
from PyQt5.QtWidgets import QApplication
from ui_layout import SRUQueryApp


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SRUQueryApp()
    window.show()
    sys.exit(app.exec_())
