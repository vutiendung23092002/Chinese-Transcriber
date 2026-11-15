from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QFrame, QSizePolicy, QComboBox, QListView, QStyledItemDelegate, QAbstractItemView, QApplication)
from .theme import icon, asset, LIGHT, DARK, dropdown_popup_stylesheet

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

def tonal_button(text, glyph, colors, callback=None):
    """Compact secondary action with consistent icon spacing and native focus."""
    w = button('', callback)
    w.setProperty('tonal', True)
    w.setAccessibleName(text)
    w.setCursor(Qt.CursorShape.PointingHandCursor)
    w.setFixedHeight(40)
    dark = colors['bg'] == DARK['bg']
    foreground = '#E1D1F0' if dark else '#5C467B'
    background = '#393142' if dark else '#F1EBF8'
    border = '#51445F' if dark else '#E4D9F1'
    hover = '#483954' if dark else '#E9DEF5'
    w.setStyleSheet(f'''
        QPushButton[tonal="true"] {{ background:{background}; border:1px solid {border}; border-radius:10px; padding:0; min-height:38px; max-height:38px; }}
        QPushButton[tonal="true"]:hover {{ background:{hover}; border-color:{colors['focus']}; }}
        QPushButton[tonal="true"]:pressed {{ background:{colors['lavender']}; }}
        QPushButton[tonal="true"]:focus {{ border-color:{colors['focus']}; }}
        QPushButton[tonal="true"] QLabel {{ background:transparent; border:none; color:{foreground}; font-size:14px; font-weight:500; }}
    ''')
    contents = QHBoxLayout(w)
    contents.setContentsMargins(14, 0, 14, 0)
    contents.setSpacing(10)
    contents.addStretch()
    glyph_label = label('')
    glyph_label.setFixedSize(16, 16)
    glyph_label.setPixmap(icon(glyph, foreground, 16).pixmap(16, 16))
    text_label = label(text)
    text_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
    for child in (glyph_label, text_label):
        child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        contents.addWidget(child)
    contents.addStretch()
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

class ComboBox(QComboBox):
    """Shared native selector with a consistently styled, keyboard-accessible list."""

    def __init__(self,parent=None):
        super().__init__(parent)
        # Qt's default roll animation stretches snapshots of translucent popups.
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo,False)
        self._popup_colors=None
        view=QListView(self)
        view.setItemDelegate(QStyledItemDelegate(view))
        view.setUniformItemSizes(True)
        view.setMouseTracking(True)
        view.setTextElideMode(Qt.TextElideMode.ElideRight)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setView(view)
        popup=view.window()
        popup.setObjectName('combo_popup')
        popup.setFrameShape(QFrame.Shape.NoFrame)
        popup.setWindowFlag(Qt.WindowType.FramelessWindowHint,True)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True)
        popup.setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True)
        popup.setStyleSheet('QFrame#combo_popup { background:transparent; border:none; }')
        view.viewport().setAutoFillBackground(False)
        self.setMaxVisibleItems(8)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(5)

    def showPopup(self):
        # Long source/device names can use a wider list without widening the sidebar.
        text_width=max((self.fontMetrics().horizontalAdvance(self.itemText(i)) for i in range(self.count())),default=0)
        self.view().setMinimumWidth(max(self.width(),min(420,text_width+48)))
        colors=getattr(self.window(),'colors',LIGHT)
        file_style=getattr(self.window(),'page',None) in ('file','live')
        if self._popup_colors!=colors or getattr(self,'_popup_file_style',None)!=file_style:
            typography='QListView {font-family:"Inter";font-size:15px;font-weight:400;} QListView::item {min-height:24px;padding:8px 12px;}' if file_style else ''
            self.view().setStyleSheet(dropdown_popup_stylesheet(colors)+typography)
            self._popup_colors=dict(colors)
            self._popup_file_style=file_style
        super().showPopup()

class Rail(QWidget):
    selected = Signal(str)
    BUTTON_STYLE = ('border:0;background:transparent;padding:0;'
                    'min-width:36px;max-width:36px;min-height:36px;max-height:36px')

    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.current = "dashboard"
        self.setObjectName("rail")
        self.setFixedWidth(82)
        self.buttons = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 18, 0, 18)
        layout.setSpacing(20)
        logo = QToolButton()
        logo.setIcon(__import__('PySide6.QtGui', fromlist=['QIcon']).QIcon(str(asset('logo-concepts/03-v2-voice-rhythm.svg'))))
        logo.setIconSize(QSize(40,40))
        logo.setFixedSize(50,44)
        logo.setStyleSheet('border:0;background:transparent;padding:0;'
                          'min-width:50px;max-width:50px;min-height:44px;max-height:44px')
        logo.setToolTip("Chinese Transcriber")
        logo.clicked.connect(lambda: self.selected.emit('dashboard'))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.pill = QWidget()
        self.pill.setFixedWidth(50)
        self.pill.setMinimumHeight(460)
        pill_layout = QVBoxLayout(self.pill)
        pill_layout.setContentsMargins(7, 22, 7, 16)
        pill_layout.setSpacing(12)
        for key, glyph, title in PAGES:
            item = QToolButton()
            item.setObjectName('nav_'+key)
            item.setFixedSize(36, 36)
            item.setStyleSheet(self.BUTTON_STYLE)
            item.setIconSize(QSize(16,16))
            item.setToolTip(title)
            item.setAccessibleName(title)
            item.clicked.connect(lambda checked=False, page=key: self.selected.emit(page))
            pill_layout.addWidget(item)
            self.buttons[key] = (item, glyph)
        pill_layout.addStretch()
        self.profile = QWidget()
        self.profile.setObjectName('rail_profile')
        self.profile.setFixedSize(36,36)
        profile_layout = QHBoxLayout(self.profile)
        profile_layout.setContentsMargins(6,6,6,6)
        profile_layout.setSpacing(0)
        local = label('CT')
        local.setAlignment(Qt.AlignmentFlag.AlignCenter)
        local.setFixedSize(24,24)
        local.setStyleSheet('background:#F2BFCD;color:#473646;border-radius:12px;font-size:9px')
        profile_layout.addWidget(local)
        pill_layout.addWidget(self.profile)
        self.cli = QToolButton()
        self.cli.setObjectName('rail_codex')
        self.cli.setFixedSize(36,36)
        self.cli.setIconSize(QSize(16,16))
        self.cli.setStyleSheet(self.BUTTON_STYLE)
        self.cli.setToolTip('Kết nối Codex CLI')
        self.cli.setAccessibleName('Kết nối Codex CLI')
        self.cli.clicked.connect(lambda: self.selected.emit('settings'))
        pill_layout.addWidget(self.cli)
        layout.addWidget(self.pill, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.apply_colors(colors)

    def apply_colors(self, colors):
        self.colors = colors
        for key, (item, glyph) in self.buttons.items():
            active = key == self.current
            item.setIcon(QIcon() if active else icon(glyph, colors['rail_text']))
            item.setStyleSheet(self.BUTTON_STYLE)
        self.cli.setIcon(icon('terminal', colors['rail_text']))
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
        cy = y + active.y() + active.height()/2
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
