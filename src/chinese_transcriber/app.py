import argparse
import os
import sys
import logging
from pathlib import Path
from PySide6.QtCore import QTimer, QLockFile
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from .workspace import WorkspaceWindow
from .storage import Store
from .theme import asset, load_fonts

def main():
    parser=argparse.ArgumentParser(description='Chinese Transcriber')
    parser.add_argument('--data-dir',help='Thư mục dữ liệu riêng')
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--portable',action='store_true',help='Lưu dữ liệu trong thư mục data bên cạnh chương trình')
    parser.add_argument('--self-test-audio',help='Kiểm tra ASR/codec bằng file thật trong thư viện kiểm tra riêng')
    parser.add_argument('--self-test-codex',action='store_true',help='Kiểm tra dịch thật bằng GPT-6 Luna, low')
    args=parser.parse_args()
    if args.data_dir:
        os.environ['CHINESE_TRANSCRIBER_DATA']=os.path.abspath(args.data_dir)
    elif args.portable:
        base=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]
        os.environ['CHINESE_TRANSCRIBER_DATA']=str(base/'data')
    if sys.platform=='win32':
        # Keep source launches under the app's identity instead of pythonw.exe.
        import ctypes
        shell32=ctypes.OleDLL('shell32')
        shell32.SetCurrentProcessExplicitAppUserModelID.argtypes=[ctypes.c_wchar_p]
        shell32.SetCurrentProcessExplicitAppUserModelID('ChineseTranscriber.Desktop')
    app=QApplication(sys.argv[:1]); app.setApplicationName('Chinese Transcriber')
    app.setWindowIcon(QIcon(str(asset('logo-concepts/03-v2-voice-rhythm.svg'))))
    app.setOrganizationName('ChineseTranscriber'); app.setFont(QFont('Segoe UI',10))
    load_fonts(app)
    if args.self_test_audio:
        if not args.data_dir: parser.error('--self-test-audio cần --data-dir riêng')
        from .selftest import validate_runtime
        return validate_runtime(args.data_dir,args.self_test_audio,args.self_test_codex)
    try:
        store=Store()
        lock=QLockFile(str(store.root/'application.lock')); lock.setStaleLockTime(0)
        if not lock.tryLock(100):
            QMessageBox.information(None,'Chinese Transcriber','Thư viện này đang được một cửa sổ khác sử dụng.'); return 1
        logging.basicConfig(filename=store.root/'application.log',encoding='utf-8',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
        store.backup()
        window=WorkspaceWindow(store); window.show()
    except Exception as error:
        QMessageBox.critical(None,'Không thể mở thư viện',str(error)+'\nDữ liệu hiện có không bị tạo lại hoặc xóa.'); return 1
    if args.smoke_test:
        QTimer.singleShot(1500,app.quit)
    result=app.exec(); lock.unlock(); return result

if __name__=='__main__':
    sys.exit(main())
