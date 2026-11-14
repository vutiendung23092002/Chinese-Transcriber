from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QFrame, QSizePolicy)
from .theme import icon, asset

PAGES = [("dashboard", "home", "Trang chủ"), ("file", "file", "Dịch file ghi âm"),
         ("live", "mic", "Ghi âm trực tiếp"), ("library", "library", "Thư viện"),
         ("prompts", "book", "Prompt & Thuật ngữ"), ("settings", "settings", "Cài đặt & Codex"),
         ("trash", "trash", "Thùng rác")]

def label(text, role=None, wrap=False):
    w = QLabel(text)
    if role:
        w.setProperty("role", role)
    w.setWordWrap(wrap)
    w.setTextFormat(Qt.TextFormat.PlainText)
    return w

def button(text, callback=None, primary=False, danger=False):
    w = QPushButton(text)
    w.setProperty("primary", primary)
    w.setProperty("danger", danger)
    if callback:
        w.clicked.connect(callback)
    return w

def box(vertical=True, margins=0, spacing=12):
    widget = QWidget()
    layout = QVBoxLayout(widget) if vertical else QHBoxLayout(widget)
    layout.setContentsMargins(margins, margins, margins, margins)
    layout.setSpacing(spacing)
    return widget, layout

def card(title=None):
    widget = QFrame()
    widget.setObjectName("card")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    if title:
        layout.addWidget(label(title, "heading"))
    return widget, layout

def clear(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout():
            clear(item.layout())

class Rail(QWidget):
    selected = Signal(str)

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.current = "dashboard"
        self.setObjectName("rail")
        self.setFixedWidth(82)
        self.buttons = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 18, 15, 18)
        layout.setSpacing(20)
        logo = QToolButton()
        logo.setIcon(__import__('PySide6.QtGui', fromlist=['QIcon']).QIcon(str(asset('logo-concepts/03-v2-voice-rhythm.svg'))))
        logo.setIconSize(QSize(40,40))
        logo.setFixedSize(50,44)
        logo.setStyleSheet("border:0;background:transparent;padding:0")
        logo.setToolTip("Chinese Transcriber")
        logo.clicked.connect(lambda: self.selected.emit('dashboard'))
        layout.addWidget(logo)
        self.pill = QWidget()
        self.pill.setMinimumHeight(460)
        pill_layout = QVBoxLayout(self.pill)
        pill_layout.setContentsMargins(7, 26, 0, 12)
        pill_layout.setSpacing(7)
        for key, glyph, title in PAGES:
            item = QToolButton()
            item.setObjectName('nav_'+key)
            item.setFixedSize(36, 36)
            item.setIconSize(QSize(16,16))
            item.setToolTip(title)
            item.setAccessibleName(title)
            item.clicked.connect(lambda checked=False, page=key: self.selected.emit(page))
            pill_layout.addWidget(item)
            self.buttons[key] = (item, glyph)
        pill_layout.addStretch()
        local = label('CT')
        local.setAlignment(Qt.AlignmentFlag.AlignCenter)
        local.setFixedSize(24,24)
        local.setStyleSheet('background:#F2BFCD;color:#473646;border-radius:12px;font-size:9px')
        pill_layout.addWidget(local, alignment=Qt.AlignmentFlag.AlignHCenter)
        cli = QToolButton()
        cli.setFixedSize(36,32)
        cli.setStyleSheet('border:0;background:transparent;padding:0')
        cli.setIcon(icon('terminal', colors['rail_text']))
        cli.setToolTip('Kết nối Codex CLI')
        cli.clicked.connect(lambda: self.selected.emit('settings'))
        pill_layout.addWidget(cli)
        layout.addWidget(self.pill, 1)
        self.apply_colors(colors)

    def apply_colors(self, colors):
        self.colors = colors
        for key, (item, glyph) in self.buttons.items():
            active = key == self.current
            item.setIcon(QIcon() if active else icon(glyph, colors['rail_text']))
            item.setStyleSheet('border:0;background:transparent;padding:0')
        self.update()

    def set_page(self, page):
        self.current = page
        self.apply_colors(self.colors)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.pill.geometry()
        x, y, width, height = rect.x(), rect.y(), 50, rect.height()
        path = QPainterPath()
        path.addRoundedRect(x, y, width, height, 25, 25)
        active = self.buttons[self.current][0]
        cy = y + active.geometry().center().y()
        cut = QPainterPath()
        cut.moveTo(x+50,cy-30)
        cut.cubicTo(x+50,cy-22,x+42,cy-22,x+33,cy-22)
        cut.cubicTo(x+20.85,cy-22,x+11,cy-12.15,x+11,cy)
        cut.cubicTo(x+11,cy+12.15,x+20.85,cy+22,x+33,cy+22)
        cut.cubicTo(x+42,cy+22,x+50,cy+22,x+50,cy+30)
        cut.lineTo(x+60,cy+30); cut.lineTo(x+60,cy-30); cut.closeSubpath()
        painter.fillPath(path.subtracted(cut), QColor(self.colors['rail']))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.colors['selected']))
        painter.drawEllipse(int(x+19),int(cy-14),28,28)
        icon(self.buttons[self.current][1], '#453944').paint(painter,int(x+25),int(cy-8),16,16)
