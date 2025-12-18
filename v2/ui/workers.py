from PyQt5.QtCore import QThread, pyqtSignal


class BaseImportWorker(QThread):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, fn, path: str):
        super().__init__()
        self.fn = fn
        self.path = path

    def run(self):
        try:
            result = self.fn(self.path)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class ImportFolderWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, fn, folder: str):
        super().__init__()
        self.fn = fn
        self.folder = folder

    def run(self):
        try:
            result = self.fn(self.folder, progress=self._emit_progress)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _emit_progress(self, current: int, total: int, message: str):
        self.progress.emit(current, total, message)


class ConsolidateWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object, dict)
    failed = pyqtSignal(str)

    def __init__(self, fn, start_date, end_date):
        super().__init__()
        self.fn = fn
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            result, resumos = self.fn(self.start_date, self.end_date, progress=self._emit_progress)
            self.finished.emit(result, resumos)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _emit_progress(self, step: int, message: str):
        self.progress.emit(step, message)
