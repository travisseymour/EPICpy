from uifiles.loadui import Ui_DialogLoading
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QDialog, QApplication
import sys

from apputils import get_resource


class LoadingWorker(QThread):

    def __init__(self, func: callable):
        QThread.__init__(self)
        self.func = func
        self.result = None

    def __del__(self):
        try:
            self.wait()
        except:
            pass

    def run(self):
        self.result = self.func()


class LoadingSignal(QObject):
    message = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)

    def showMsg(self, msg):
        self.message.emit(msg)


LoadingMessenge = LoadingSignal()


class LoadingWin(QDialog):
    message = pyqtSignal(str)

    def __init__(self, func: callable):
        super(LoadingWin, self).__init__()

        self.func = func
        self.result = None
        self.error = None

        self.ui = Ui_DialogLoading()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # loading icon
        # pixmap = QPixmap(self.context.get_resource('images', 'spinner_rainbow.gif'))
        # self.ui.labelImage.setPixmap(pixmap)

        # loading movie
        movie = QMovie(get_resource('images', 'spinner_rainbow.gif'))
        self.ui.labelImage.setMovie(movie)
        movie.start()

        LoadingMessenge.message.connect(self.set_message)

        self.worker = LoadingWorker(func=self.func)
        self.worker.finished.connect(self.on_close)
        self.worker.start()

        self.exec()

    def set_message(self, message: str):
        self.ui.labelText.setText(message)

    def on_close(self):
        self.result = self.worker.result
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)


    def my_fake_work(*args, **kwargs):
        from PyQt5 import QtTest
        for i in range(8):
            LoadingMessenge.showMsg(f"Loading, Please Wait...\nProcessing task {i}/8")
            print(f"Loading, Please Wait...\nProcessing task {i}/8")
            QtTest.QTest.qWait(1000)
        return True


    loading = LoadingWin(func=my_fake_work)

    print(f"loading func result = {loading.result}, error msg={loading.error}")

    sys.exit(app.exec())
