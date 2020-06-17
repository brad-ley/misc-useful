import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setWindowTitle("FiFiFactory App")
        self.resize(720, 480)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [str(u.toLocalFile()) for u in event.mimeData().urls()]

        for f in files:
            print(f)


def main():

    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
