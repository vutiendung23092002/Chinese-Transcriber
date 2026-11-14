from pathlib import Path
import sys
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QFont, QFontDatabase
from PySide6.QtSvg import QSvgRenderer

LIGHT = dict(bg="#F6F5F7", panel="#FFFFFF", soft="#F7F6F8", text="#292633",
             muted="#696471", line="#E9E6ED", primary="#302B40", on_primary="#FFFFFF",
             rail="#292636", rail_text="#C1BBCD", selected="#F2BFCD", pink="#FBE2E9",
             lavender="#EEE5FB", yellow="#FFF0CB", cyan="#DEF1F3", danger="#A13E59",
             success="#3E6455", focus="#8A638D")
DARK = dict(bg="#24212E", panel="#302B3B", soft="#393343", text="#F5F0F6",
            muted="#C3BACD", line="#4B4458", primary="#EDD6E5", on_primary="#302738",
            rail="#211E2B", rail_text="#C8BFD4", selected="#EFC0CF", pink="#503443",
            lavender="#443650", yellow="#4C402C", cyan="#2E4549", danger="#F5BECC",
            success="#C0DEC9", focus="#E5B8D1")
PATHS = {
 "home":'<path d="m3 10 9-7 9 7v10H3zM9 20v-7h6v7"/>',
 "file":'<path d="M14 3H5v18h14V8zM14 3v5h5M8 12h8M8 16h5"/>',
 "mic":'<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11v1a7 7 0 0 0 14 0v-1M12 19v3m-4 0h8"/>',
 "library":'<path d="M4 4h4v16H4zM10 4h4v16h-4zM17 4l4 1-2 15-4-1z"/>',
 "book":'<path d="M12 6c-2-3-7-3-10-2v15c4-1 7-1 10 2 3-3 6-3 10-2V4c-3-1-8-1-10 2v15"/>',
 "settings":'<path d="M9 3h6l1 4 4 1v6l-4 2-1 4H9l-1-4-4-2V8l4-1z"/><circle cx="12" cy="11" r="3"/>',
 "trash":'<path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/>',
 "upload":'<path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5"/>',
 "arrow":'<path d="M5 12h14m-5-5 5 5-5 5"/>',
 "play":'<path d="m8 4 12 8-12 8z"/>',
 "terminal":'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m6 9 4 3-4 3m7 0h5"/>',
 "audio":'<path d="M4 10v4m4-8v12m4-15v18m4-15v12m4-8v4"/>',
 "download":'<path d="M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5"/>',
 "refresh":'<path d="M20 10a8 8 0 0 0-14-5L3 8m0-5v5h5M4 14a8 8 0 0 0 14 5l3-3m0 5v-5h-5"/>',
 "plus":'<path d="M12 5v14M5 12h14"/>',
 "pause":'<path d="M8 5v14M16 5v14"/>',
 "stop":'<rect x="5" y="5" width="14" height="14" rx="1"/>',
 "clock":'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
}

def asset(name: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / "assets" / name

def load_fonts(application):
    for name in ('NotoSans.ttf','NotoSansSC.ttf'):
        path=asset('fonts/'+name)
        if path.is_file(): QFontDatabase.addApplicationFont(str(path))
    font=QFont('Segoe UI' if 'Segoe UI' in QFontDatabase.families() else 'Noto Sans',10)
    font.setFamilies([font.family(),'Noto Sans','Noto Sans SC'])
    application.setFont(font)

def icon(name: str, color: str, size: int = 20) -> QIcon:
    data = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{PATHS.get(name, PATHS["file"])}</svg>'
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(data.encode()))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)

def bubble_icon(name,background,foreground,size=36):
    data=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="{background}"/><g transform="translate(10 10) scale(.83)" fill="none" stroke="{foreground}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{PATHS.get(name,PATHS["file"])}</g></svg>'
    pixmap=QPixmap(size*2,size*2); pixmap.fill(Qt.GlobalColor.transparent)
    renderer=QSvgRenderer(QByteArray(data.encode())); painter=QPainter(pixmap); renderer.render(painter); painter.end(); pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)

def stylesheet(c: dict) -> str:
    return f'''
    QWidget {{ font-family: "Segoe UI", "Noto Sans", "Noto Sans SC"; font-size: 12px; color: {c['text']}; }}
    QMainWindow, QWidget#workspace {{ background: {c['bg']}; }}
    QWidget#context, QWidget#rail {{ background: {c['panel']}; }}
    QFrame#card {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 18px; }}
    QLabel {{ background: transparent; border: none; }}
    QLabel[role="muted"] {{ color: {c['muted']}; font-size: 11px; }}
    QLabel[role="title"] {{ font-size: 24px; font-weight: 600; }}
    QLabel[role="heading"] {{ font-size: 17px; font-weight: 600; }}
    QLabel[role="value"] {{ font-size: 26px; font-weight: 600; }}
    QPushButton, QToolButton {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 10px; padding: 8px 12px; min-height: 18px; }}
    QPushButton:hover {{ background: {c['soft']}; }}
    QPushButton:focus, QComboBox:focus, QLineEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {c['focus']}; }}
    QPushButton[primary="true"] {{ background: {c['primary']}; color: {c['on_primary']}; border-color: {c['primary']}; font-weight: 600; }}
    QPushButton[danger="true"] {{ color: {c['danger']}; }}
    QPushButton:disabled {{ color: {c['muted']}; background: {c['soft']}; }}
    QLineEdit, QComboBox, QPlainTextEdit, QTextEdit, QSpinBox {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 7px; padding: 7px; selection-background-color: {c['selected']}; }}
    QComboBox {{ min-height: 19px; }}
    QComboBox QAbstractItemView {{ background: {c['panel']}; selection-background-color: {c['lavender']}; color: {c['text']}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 9px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {c['line']}; border-radius: 4px; min-height: 25px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QTableWidget {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 10px; gridline-color: {c['line']}; selection-background-color: {c['lavender']}; selection-color: {c['text']}; }}
    QHeaderView::section {{ background: {c['soft']}; border: none; border-bottom: 1px solid {c['line']}; padding: 10px; color: {c['muted']}; }}
    QListWidget {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 10px; padding: 5px; }}
    QListWidget::item {{ padding: 10px; border-radius: 7px; }}
    QListWidget::item:selected {{ background: {c['lavender']}; color: {c['text']}; }}
    QProgressBar {{ background: {c['soft']}; border: none; border-radius: 4px; text-align: center; min-height: 8px; }}
    QProgressBar::chunk {{ background: {c['selected']}; border-radius: 4px; }}
    QStatusBar {{ background: {c['panel']}; color: {c['muted']}; }}
    QToolTip {{ background: {c['rail']}; color: white; border: none; padding: 7px; }}
    '''
