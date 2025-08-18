from PyQt5.QtCore import QThread, pyqtSignal
from app.sru_functions import dnb_sru, dnb_sru_number

## Worker:
class DNBNumberWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, query, metadata, base_url):
        super().__init__()
        self.query = query
        self.metadata = metadata
        self.base_url = base_url

    def run(self):
        try:
            result = dnb_sru_number(self.query, self.metadata, self.base_url)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"FEHLER: {str(e)}")


class DNBSRUThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(bool)

    def __init__(self, query, metadata, base_url, filename):
        super().__init__()
        self.query = query
        self.metadata = metadata
        self.base_url = base_url
        self.filename = filename
        self._is_running = True

    def run(self):
        # Übergabe `is_running` Funktion an `dnb_sru`
        success = dnb_sru(self.query, self.metadata, self.base_url, self.progress_signal, self.filename,
                          self.is_running)
        if self.is_running():
            self.result_signal.emit(success)
        else:
            self.progress_signal.emit(0)

    def stop(self):
        self._is_running = False

    def is_running(self):
        return self._is_running

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.logo_label.setGeometry(self.width() - 60, 10, 50, 50)

