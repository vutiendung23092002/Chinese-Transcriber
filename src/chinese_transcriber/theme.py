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
 "translate":'<path d="M3 5h12M9 2v3m3 0c-1 5-4 8-9 11m2-8 7 7m2 6 4-10 4 10m-6-4h4"/>',
 "download":'<path d="M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5"/>',
 "refresh":'<path d="M20 10a8 8 0 0 0-14-5L3 8m0-5v5h5M4 14a8 8 0 0 0 14 5l3-3m0 5v-5h-5"/>',
 "plus":'<path d="M12 5v14M5 12h14"/>',
 "pause":'<path d="M8 5v14M16 5v14"/>',
 "stop":'<rect x="5" y="5" width="14" height="14" rx="1"/>',
 "clock":'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
 "cube":'<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10M7.5 4.5l9 5"/>',
 "cpu":'<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 1v4m6-4v4M9 19v4m6-4v4M1 9h4m-4 6h4m14-6h4m-4 6h4"/><rect x="9" y="9" width="6" height="6"/>',
 "monitor":'<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M12 17v4m-5 0h10"/>',
 "database":'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0"/>',
 "chart":'<path d="M5 20V10m7 10V4m7 16V8"/>',
 "folder":'<path d="M3 6h6l2 2h10v12H3zM3 6V4h6l2 2h9v2"/>',
 "backup":'<path d="M7 18H5a4 4 0 0 1-1-8 8 8 0 0 1 15-1 5 5 0 0 1 0 10h-2M12 21V11m-4 4 4-4 4 4"/>',
 "info":'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/>',
 "check":'<path d="m5 12 4 4L19 6"/>',
 "bolt":'<path d="m13 2-9 12h7l-1 8 10-13h-7z"/>',
 "record":'<circle cx="12" cy="12" r="4" stroke-width="8"/>',
 "search":'<circle cx="10.5" cy="10.5" r="7.5"/><path d="m16 16 6 6"/>',
 "versions":'<rect x="4" y="5" width="14" height="17" rx="2"/><path d="M8 5V2h11l3 3v13h-4M8 10h6M8 14h7M8 18h5"/>',
 "audio-file":'<path d="M14 2H5v20h15V8zM14 2v6h6M8 13v4m3-7v10m3-8v6m3-4v2"/>',
 "save":'<path d="M4 3h13l4 4v14H3V3zM7 3v7h10V3M7 21v-7h10v7"/>',
 "volume":'<path d="M11 5 6 9H3v6h3l5 4zM15 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
 "volume-off":'<path d="M11 5 6 9H3v6h3l5 4zM16 9l6 6m0-6-6 6"/>',
 "chevron":'<path d="m9 5 7 7-7 7"/>',
}

def asset(name: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / "assets" / name

def load_fonts(application):
    for name in ('Inter.ttf','Inter-Italic.ttf','NotoSans.ttf','NotoSansSC.ttf'):
        path=asset('fonts/'+name)
        if path.is_file(): QFontDatabase.addApplicationFont(str(path))
    font=QFont('Inter' if 'Inter' in QFontDatabase.families() else 'Noto Sans',10)
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

def dropdown_popup_stylesheet(c):
    return f'''
    QListView {{ background: {c['panel']}; color: {c['text']}; border: 1px solid {c['line']}; border-radius: 10px; padding: 5px; outline: 0; selection-background-color: {c['lavender']}; selection-color: {c['text']}; }}
    QListView::item {{ min-height: 24px; padding: 6px 10px; border: none; border-radius: 6px; }}
    QListView::item:hover {{ background: {c['soft']}; }}
    QListView::item:selected {{ background: {c['lavender']}; color: {c['text']}; }}
    QListView::item:disabled {{ color: {c['muted']}; background: transparent; }}
    '''

def stylesheet(c: dict) -> str:
    mode='dark' if c['bg']==DARK['bg'] else 'light'
    arrow_down=asset(f'icons/chevron-down-{mode}.svg').as_posix()
    arrow_up=asset(f'icons/chevron-up-{mode}.svg').as_posix()
    return f'''
    QWidget {{ font-family: "Inter", "Noto Sans", "Noto Sans SC"; font-size: 12px; color: {c['text']}; }}
    QMainWindow, QWidget#workspace, QWidget#context {{ background: {c['bg']}; }}
    QWidget#rail {{ background: {c['panel']}; }}
    QFrame#context_panel {{ background:{c['panel']}; border:1px solid {c['line']}; border-radius:26px; }}
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
    QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 7px; padding: 7px; selection-background-color: {c['selected']}; }}
    QComboBox {{ background: {c['panel']}; border: 1px solid {c['line']}; border-radius: 9px; padding: 6px 8px 6px 12px; min-height: 20px; selection-background-color: {c['lavender']}; }}
    QComboBox:hover {{ border-color: {c['focus']}; background: {c['soft']}; }}
    QComboBox:focus, QComboBox:on {{ border-color: {c['focus']}; background: {c['panel']}; }}
    QComboBox:disabled {{ color: {c['muted']}; background: {c['soft']}; border-color: {c['line']}; }}
    QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 30px; border: none; background: transparent; border-top-right-radius: 9px; border-bottom-right-radius: 9px; }}
    QComboBox::down-arrow {{ image: url("{arrow_down}"); width: 14px; height: 14px; }}
    QComboBox::down-arrow:on {{ image: url("{arrow_up}"); }}
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
