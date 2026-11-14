import logging
import traceback
from PySide6.QtCore import QObject, QRunnable, Signal

class TaskSignals(QObject):
    result=Signal(object)
    error=Signal(str)
    progress=Signal(object)
    finished=Signal()

class Task(QRunnable):
    def __init__(self,func):
        super().__init__(); self.func=func; self.signals=TaskSignals()

    def run(self):
        try:
            self.signals.result.emit(self.func(self.signals.progress.emit))
        except Exception as error:
            logging.error('Tác vụ thất bại: %s\n%s',type(error).__name__,traceback.format_exc())
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()
