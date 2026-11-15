"""Home workspace matching dashboard-approved-v2, backed by the real library."""
from datetime import datetime
from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget, QFrame, QPushButton, QAbstractButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QBoxLayout,
)
from .widgets import label, button
from .file_page import ElidedLabel
from .theme import icon, DARK


def text(text, pixels, weight=400, color=None, wrap=False, elide=False):
    widget = ElidedLabel(text) if elide else label(text, wrap=wrap)
    widget.setStyleSheet(f'font-family:"Inter";font-size:{pixels}px;font-weight:{weight};'
                        + (f'color:{color};' if color else ''))
    return widget


def glyph_badge(glyph, background, foreground, size=60, glyph_size=34):
    widget = label('')
    widget.setFixedSize(size, size)
    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    widget.setStyleSheet(f'background:{background};border-radius:{min(18,size//4)}px')
    widget.setPixmap(icon(glyph, foreground, glyph_size).pixmap(glyph_size, glyph_size))
    return widget


def arrow_button(caption, callback, colors, primary=False):
    control = button('', callback, primary)
    control.setAccessibleName(caption)
    control.setCursor(Qt.CursorShape.PointingHandCursor)
    foreground = colors['on_primary'] if primary else colors['text']
    background = colors['primary'] if primary else 'transparent'
    height = 42 if primary else 34
    control.setStyleSheet(f'QPushButton {{background:{background};border:1px solid transparent;border-radius:12px;padding:0;min-height:{height}px;max-height:{height}px;}} QPushButton:focus {{border-color:{colors["focus"]};}}')
    body = QHBoxLayout(control)
    body.setContentsMargins(20 if primary else 0, 0, 16 if primary else 0, 0)
    body.setSpacing(12)
    words = text(caption, 15 if primary else 16, 700 if primary else 600, foreground)
    body.addWidget(words, 1)
    arrow = label('')
    arrow.setFixedSize(22, 22)
    arrow.setPixmap(icon('arrow', foreground, 22).pixmap(22, 22))
    body.addWidget(arrow)
    for child in (words, arrow): child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    control.ensurePolished()
    control.setFixedSize(164 if primary else 150, 44 if primary else 36)
    return control


class ActionCard(QPushButton):
    def __init__(self, colors, key, glyph, title, description, action, tone, callback):
        super().__init__()
        self.setObjectName('dashboard_action_' + key)
        self.setAccessibleName(action)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.clicked.connect(callback)
        self.colors = colors
        self.background = colors[tone]
        accent = colors['soft'] if colors['bg'] == DARK['bg'] else {
            'pink':'#F5CCD9', 'lavender':'#E0CDF8', 'yellow':'#FFE1AE',
        }[tone]
        self.body = QVBoxLayout(self)
        self.top = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.badge = glyph_badge(glyph, accent, colors['text'], 48, 28)
        self.top.addWidget(self.badge)
        self.heading = text(title, 20, 700, wrap=True)
        self.top.addWidget(self.heading)
        self.body.addLayout(self.top)
        self.description = text(description, 15, color=colors['text'], wrap=True)
        self.description.setMinimumHeight(36)
        self.body.addWidget(self.description)
        self.body.addStretch()
        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer.addWidget(text(action, 14, 700), 1)
        arrow = label('')
        arrow.setFixedSize(20, 20)
        arrow.setPixmap(icon('arrow', colors['text'], 20).pixmap(20, 20))
        footer.addWidget(arrow)
        self.body.addLayout(footer)
        self._compact = None
        self.set_compact(False)
        for child in self.findChildren(QLabel):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_compact(self, compact):
        if self._compact == compact: return
        self._compact = compact
        height = 158 if compact else 188
        self.setStyleSheet(f'''
            QPushButton#{self.objectName()} {{background:{self.background};border:1px solid transparent;border-radius:18px;padding:0;min-height:{height}px;max-height:{height}px;}}
            QPushButton#{self.objectName()}:hover, QPushButton#{self.objectName()}:focus {{border-color:{self.colors['focus']};}}
        ''')
        margin = 10 if compact else 14
        self.body.setContentsMargins(margin, margin, margin, margin)
        self.body.setSpacing(4 if compact else 6)
        self.top.setSpacing(8 if compact else 6)
        self.top.setDirection(QBoxLayout.Direction.LeftToRight if compact else QBoxLayout.Direction.TopToBottom)
        self.badge.setFixedSize(32 if compact else 48, 32 if compact else 48)


class DashboardActions(QWidget):
    """The three approved actions replace the old six-tile sidebar grid."""
    def __init__(self, owner):
        super().__init__()
        self.setObjectName('dashboard_actions')
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.cards = []
        for key, glyph, title, description, action, tone, callback in (
            ('file','file','Dịch file ghi âm','Chép lời và dịch từ file âm thanh.','Chọn file âm thanh','pink',owner.choose_audio),
            ('live','mic','Ghi âm trực tiếp','Theo dõi bài giảng theo từng câu.','Bắt đầu ghi âm','lavender',lambda:owner.navigate('live')),
            ('prompts','book','Chuẩn bị thuật ngữ','Thêm bối cảnh, thuật ngữ môn học.','Soạn bộ thuật ngữ','yellow',lambda:owner.navigate('prompts')),
        ):
            control = ActionCard(owner.colors,key,glyph,title,description,action,tone,callback)
            self.cards.append(control)
            self.body.addWidget(control)
        self.set_compact(owner.height() < 820)

    def set_compact(self, compact):
        self.body.setSpacing(8 if compact else 12)
        for card in self.cards: card.set_compact(compact)


class MetricCard(QFrame):
    def __init__(self, colors, key, glyph, title, value):
        super().__init__()
        self.setObjectName('dashboard_stat_' + key)
        self.setMinimumWidth(0)
        self.setMinimumHeight(116)
        self.setStyleSheet(f'QFrame#{self.objectName()} {{background:{colors["panel"]};border:1px solid {colors["line"]};border-radius:20px;}}')
        body = QVBoxLayout(self)
        body.setContentsMargins(20, 16, 20, 16)
        body.setSpacing(12)
        header = QHBoxLayout()
        header.setSpacing(10)
        mark = label('')
        mark.setFixedSize(24, 24)
        mark.setPixmap(icon(glyph, colors['muted'], 24).pixmap(24, 24))
        header.addWidget(mark)
        header.addWidget(text(title, 16, color=colors['text'], elide=True), 1)
        body.addLayout(header)
        self.value = text(value, 30 if key == 'model' else 34, 700, elide=True)
        self.value.setObjectName('dashboard_value_' + key)
        body.addWidget(self.value)


class AudioDropZone(QAbstractButton):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.colors = owner.colors
        self.dragging = False
        self.setObjectName('dashboard_drop_zone')
        self.setAccessibleName('Kéo thả âm thanh để thêm bài học')
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptDrops(True)
        self.setMinimumWidth(0)
        self.setMinimumHeight(194)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.clicked.connect(owner.choose_audio)
        body = QVBoxLayout(self)
        body.setContentsMargins(18, 20, 18, 20)
        body.setSpacing(12)
        body.addStretch()
        mark = label('')
        mark.setFixedSize(46, 46)
        mark.setPixmap(icon('upload', self.colors['text'], 46).pixmap(46, 46))
        body.addWidget(mark, 0, Qt.AlignmentFlag.AlignHCenter)
        self.heading = text('Kéo thả âm thanh để thêm bài học', 24, 700, wrap=True)
        self.description = text('WAV, MP3, M4A và các định dạng được hỗ trợ', 18,
                                color=self.colors['muted'], wrap=True)
        for child in (self.heading, self.description):
            child.setAlignment(Qt.AlignmentFlag.AlignCenter)
            body.addWidget(child)
        body.addStretch()
        for child in self.findChildren(QLabel):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = self.colors
        background = c['soft'] if c['bg'] == DARK['bg'] else '#FBF9FD'
        painter.setBrush(QColor(c['lavender'] if self.dragging or self.isDown() else background))
        painter.setPen(QPen(QColor(c['focus'] if self.dragging or self.hasFocus() else '#C6A8E7'),
                            1.3, Qt.PenStyle.DashLine))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 18, 18)

    def can_import(self, mime):
        urls = mime.urls()
        return (not self.owner.is_busy and not self.owner.recording
                and len(urls) == 1 and urls[0].isLocalFile())

    def dragEnterEvent(self, event):
        self.dragging = self.can_import(event.mimeData())
        if self.dragging: event.acceptProposedAction()
        else: event.ignore()
        self.update()

    def dragLeaveEvent(self, event):
        self.dragging = False
        self.update()
        event.accept()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        self.dragging = False
        self.update()
        if self.can_import(event.mimeData()):
            self.owner.import_audio(event.mimeData().urls()[0].toLocalFile())
            event.acceptProposedAction()
        else:
            event.ignore()


class LessonRow(QFrame):
    def __init__(self, owner, audio):
        super().__init__()
        c = owner.colors
        self.setObjectName('dashboard_lesson')
        self.setMinimumWidth(0)
        self.setStyleSheet(f'QFrame#dashboard_lesson {{background:{c["panel"]};border:1px solid {c["line"]};border-radius:16px;}}')
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(18, 16, 18, 16)
        self.row.setSpacing(16)
        self.row.addWidget(glyph_badge('audio', c['pink'], c['text'], 52, 30))
        words = QVBoxLayout()
        words.setSpacing(6)
        self.filename = text(audio['filename'], 18, 700, elide=True)
        self.filename.text_width = 400
        self.filename.setObjectName('dashboard_filename')
        words.addWidget(self.filename)
        minutes, seconds = divmod(int(audio['duration']), 60)
        extension = audio['filename'].rsplit('.', 1)[-1].upper()
        words.addWidget(text(f'{extension} · {minutes} phút {seconds:02d} giây', 16,
                            color=c['muted'], elide=True))
        self.row.addLayout(words, 1)
        versions = owner.store.versions(audio['id'])
        transcript = owner.store.latest_transcript(audio['id']) or owner.store.latest_transcript(audio['id'], False)
        if versions:
            state = {'complete':'Đã dịch', 'running':'Đang dịch', 'queued':'Chờ dịch',
                     'partial':'Dịch chưa đầy đủ', 'failed':'Dịch lỗi', 'interrupted':'Dịch gián đoạn'}.get(versions[0]['status'], 'Chưa dịch')
        elif transcript:
            state = {'complete':'Đã chép lời', 'running':'Đang chép lời', 'failed':'Chép lời lỗi',
                     'interrupted':'Chép lời gián đoạn'}.get(transcript['status'], 'Chưa chép lời')
        else:
            state = 'Chưa chép lời'
        self.status = text(state, 14, 500)
        self.status.setObjectName('dashboard_lesson_status')
        self.status.setStyleSheet(self.status.styleSheet() + f'background:{c["lavender"]};border-radius:14px;padding:6px 12px')
        self.status.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.status.ensurePolished(); self.status.setFixedHeight(30)
        self.row.addWidget(self.status, 0, Qt.AlignmentFlag.AlignVCenter)
        self.open_button = arrow_button('Mở bài học', lambda:owner.open_audio(audio['id']), c, True)
        self.open_button.setObjectName('dashboard_open_lesson')
        self.row.addWidget(self.open_button, 0, Qt.AlignmentFlag.AlignVCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep the full filename in its tooltip and the row usable on small windows.
        self.status.setVisible(self.width() >= 760)
        self.setToolTip(self.status.text())


class DashboardPage(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setObjectName('dashboard_page')
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        c = owner.colors
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(20)
        self.stats_grid = QGridLayout()
        self.stats_grid.setContentsMargins(0, 0, 0, 0)
        self.stats_grid.setSpacing(16)
        audio = owner.store.list_audio()
        saved = owner.store.one('''SELECT COUNT(*) total,MAX(v.created) latest FROM versions v
            JOIN audio a ON a.id=v.audio_id WHERE v.deleted IS NULL AND a.deleted IS NULL''')
        latest = '—'
        if saved['latest']:
            latest = datetime.fromisoformat(saved['latest']).astimezone().strftime('%d/%m · %H:%M')
        model = owner.store.setting('model')
        display = next((entry['displayName'] for entry in owner.models if entry['model']==model), model or 'Chưa chọn')
        if model and model.startswith('gpt-'): display = 'GPT-' + ' '.join(part.capitalize() for part in model[4:].split('-'))
        self.metrics = {}
        for key, glyph, title, value in (
            ('audio','audio','File âm thanh',str(len(audio))),
            ('versions','file','Bản dịch đã lưu',str(saved['total'])),
            ('latest','clock','Lần dịch gần nhất',latest),
            ('model','cpu','Mô hình mặc định',display),
        ):
            self.metrics[key] = MetricCard(c,key,glyph,title,value)
            if key=='latest' and latest!='—':
                self.metrics[key].value.setStyleSheet('font-family:"Inter";font-size:20px;font-weight:600')
                self.metrics[key].value.setToolTip(datetime.fromisoformat(saved['latest']).astimezone().isoformat())
        self.body.addLayout(self.stats_grid)
        recent = QFrame()
        recent.setObjectName('dashboard_recent')
        recent.setStyleSheet(f'QFrame#dashboard_recent {{background:{c["panel"]};border:1px solid {c["line"]};border-radius:22px;}}')
        recent_body = QVBoxLayout(recent)
        recent_body.setContentsMargins(20, 20, 20, 22)
        recent_body.setSpacing(20)
        heading = QHBoxLayout()
        self.recent_title = text('Tiếp tục bài học', 30, 700, elide=True)
        heading.addWidget(self.recent_title, 1)
        self.library_button = arrow_button('Mở thư viện', lambda:owner.navigate('library'), c)
        self.library_button.setObjectName('dashboard_library')
        heading.addWidget(self.library_button)
        recent_body.addLayout(heading)
        self.lessons = []
        for row in audio[:4]:
            lesson = LessonRow(owner,row)
            self.lessons.append(lesson)
            recent_body.addWidget(lesson)
        if not audio:
            empty = text('Chưa có bài học. Thêm âm thanh để bắt đầu.',16,color=c['muted'],wrap=True)
            empty.setObjectName('dashboard_empty_library')
            recent_body.addWidget(empty)
        self.drop_zone = AudioDropZone(owner)
        self.drop_zone.setFixedHeight(226)
        recent_body.addWidget(self.drop_zone)
        self.body.addWidget(recent)
        self.body.addStretch(1)
        self._narrow = None
        self.reflow(False)

    def reflow(self, narrow):
        if self._narrow == narrow: return
        self._narrow = narrow
        while self.stats_grid.count(): self.stats_grid.takeAt(0)
        for column in range(4): self.stats_grid.setColumnStretch(column, 0)
        for i, metric in enumerate(self.metrics.values()):
            self.stats_grid.addWidget(metric, i//2 if narrow else 0, i%2 if narrow else i)
        for column in range(2 if narrow else 4): self.stats_grid.setColumnStretch(column, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow(self.width() < 850)
