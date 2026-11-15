"""Approved file workspace, using native Qt controls and the original navigation."""
from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QPainterPath, QLinearGradient, QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QTableWidget, QHeaderView, QAbstractItemView, QCheckBox, QSlider,
    QStyle, QStyleOptionComboBox, QStylePainter, QToolButton, QMenu, QAbstractButton,
)
from .widgets import label, button, ComboBox
from .theme import icon, asset, DARK
from .audio import timestamp


def ui_font(size, weight=QFont.Weight.Normal):
    font = QFont('Inter')
    font.setPixelSize(size)
    font.setWeight(weight)
    return font


def transcription_context_styles(c):
    arrow = asset('icons/chevron-down-' + ('dark' if c['bg'] == DARK['bg'] else 'light') + '.svg').as_posix()
    return f'''
        QWidget {{ font-family:"Inter"; font-size:15px; font-weight:400; }}
        QLabel[role="muted"] {{ font-size:14px; color:{c['muted']}; }}
        QLabel#file_context_title {{ font-size:24px; font-weight:700; }}
        QLabel#live_context_title {{ font-size:22px; font-weight:700; }}
        QLabel#file_context_subtitle, QLabel#live_context_subtitle {{ font-size:13px; color:{c['muted']}; }}
        QComboBox {{ font-size:15px; font-weight:400; background:{c['panel']}; border:1px solid {c['line']}; border-radius:10px; padding:7px 10px 7px 12px; min-height:22px; }}
        QComboBox::drop-down {{ width:32px; border:0; background:transparent; }}
        QComboBox::down-arrow {{ image:url("{arrow}"); width:15px; height:15px; }}
        QPlainTextEdit {{ font-size:15px; border:1px solid {c['line']}; border-radius:10px; padding:10px; }}
        QPushButton {{ font-size:15px; font-weight:500; padding:8px; border-radius:10px; }}
        QPushButton[primary="true"] {{ font-weight:600; }}
        QPushButton:disabled {{ background:{c['lavender']}; color:{c['muted']}; border:0; }}
        QPushButton#file_import {{ background:{c['lavender'] if c['bg']==DARK['bg'] else '#F0EBFC'}; color:{'#DAC4FA' if c['bg']==DARK['bg'] else '#5523A2'}; border:1px solid {'#665379' if c['bg']==DARK['bg'] else '#D6C2F3'}; padding:0; font-size:17px; font-weight:600; }}
        QPushButton#file_import:hover {{ background:{c['pink']}; }}
        QPushButton#file_connection, QPushButton#live_connection {{ background:{c['soft'] if c['bg']==DARK['bg'] else '#F0F8F2'}; color:{c['text']}; font-size:14px; font-weight:500; border:0; text-align:left; padding:10px 12px; }}
    '''


def audio_thumbnail(colors):
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(2)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(colors['pink']))
    painter.drawRoundedRect(QRectF(0, 0, 32, 32), 8, 8)
    icon('audio', colors['text'], 20).paint(painter, 6, 6, 20, 20)
    painter.end()
    return QIcon(pixmap)


class PlaybackButton(QAbstractButton):
    """The approved solid play/pause glyph, independent of native icon themes."""
    def __init__(self, colors, callback):
        super().__init__()
        self.colors = colors
        self.playing = False
        self.setFixedSize(52, 52)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(callback)

    def set_playing(self, playing):
        self.playing = playing
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setPen(Qt.PenStyle.NoPen)
        fill = QColor(self.colors['primary'])
        if self.underMouse() and self.isEnabled(): fill = fill.lighter(115)
        if self.colors['bg'] != DARK['bg'] and not self.underMouse():
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor('#3E354C')); gradient.setColorAt(1, QColor('#302B40'))
            p.setBrush(gradient)
        else:
            p.setBrush(fill)
        p.drawEllipse(bounds)
        p.setBrush(QColor(self.colors['on_primary']))
        cx, cy = self.width() / 2, self.height() / 2
        if self.playing:
            for x in (cx - 7, cx + 3): p.drawRoundedRect(QRectF(x, cy - 9, 4, 18), 1, 1)
        else:
            triangle = QPainterPath()
            triangle.moveTo(cx - 5, cy - 10)
            triangle.lineTo(cx + 10, cy)
            triangle.lineTo(cx - 5, cy + 10)
            triangle.closeSubpath()
            p.drawPath(triangle)
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(self.colors['focus']), 1, Qt.PenStyle.DotLine))
            p.drawEllipse(bounds.adjusted(3, 3, -3, -3))


class ElidedLabel(QLabel):
    """Keep the full accessible filename while fitting one visual line."""
    def __init__(self, text, text_width=None):
        super().__init__(text)
        self.text_width = text_width
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setToolTip(text)
        self.setAccessibleName(text)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)

    def sizeHint(self):
        return QSize(220, super().sizeHint().height())

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())

    def display_text(self):
        width = self.contentsRect().width()
        if self.text_width is not None: width = min(width, self.text_width)
        return self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideMiddle, width)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())
        painter.drawText(self.contentsRect(), Qt.AlignmentFlag.AlignVCenter, self.display_text())


class FilenameComboBox(ComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view().setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.currentTextChanged.connect(self.setToolTip)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        rect = self.style().subControlRect(QStyle.ComplexControl.CC_ComboBox, option,
                                          QStyle.SubControl.SC_ComboBoxEditField, self)
        icon_width = self.iconSize().width() + 6 if not option.currentIcon.isNull() else 0
        option.currentText = self.fontMetrics().elidedText(option.currentText, Qt.TextElideMode.ElideMiddle, max(0,rect.width()-icon_width))
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, option)


class NotesSwitch(QCheckBox):
    def __init__(self, colors):
        super().__init__('Ghi chú thuật ngữ')
        self.colors = colors
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def sizeHint(self):
        return QSize(54 + self.fontMetrics().horizontalAdvance(self.text()), 38)

    def hitButton(self, point):
        return self.rect().contains(point)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(ui_font(15))
        y = (self.height() - 24) / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.colors['focus'] if self.isChecked() else self.colors['line']))
        painter.drawRoundedRect(QRectF(0, y, 42, 24), 12, 12)
        painter.setBrush(QColor(self.colors['panel']))
        painter.drawEllipse(QRectF(21 if self.isChecked() else 3, y + 3, 18, 18))
        painter.setPen(QColor(self.colors['text']))
        painter.drawText(self.rect().adjusted(54, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter, self.text())
        if self.hasFocus():
            painter.setPen(QPen(QColor(self.colors['focus']), 1, Qt.PenStyle.DotLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 6, 6)


class WorkflowSteps(QWidget):
    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.completed = 0
        self.setFixedHeight(64)
        self.setStyleSheet('font-family:"Inter";font-size:18px;font-weight:500')
        self.setAccessibleName('Âm thanh → Chép lời → Dịch tiếng Việt')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = self.colors
        painter.setFont(ui_font(18, QFont.Weight.Medium))
        metrics = painter.fontMetrics()
        step = self.width() / 3
        texts = ('Âm thanh', 'Chép lời', 'Dịch tiếng Việt')
        widths = [min(step - 12, 64 + metrics.horizontalAdvance(text)) for text in texts]
        starts = [(i + .5) * step - widths[i] / 2 for i in range(3)]
        cy = self.height() / 2
        for i, text in enumerate(texts):
            x, width = starts[i], widths[i]
            active = i == self.completed
            done = i < self.completed
            painter.setPen(Qt.PenStyle.NoPen)
            if active:
                painter.setBrush(QColor(c['lavender']))
                painter.drawRoundedRect(QRectF(x, cy - 22, width, 44), 22, 22)
            painter.setBrush(QColor(c['lavender'] if done or active else c['soft']))
            if active:
                gradient = QLinearGradient(x, cy - 15, x + 30, cy + 15)
                gradient.setColorAt(0, QColor('#B794E5')); gradient.setColorAt(1, QColor('#8A5AC7'))
                painter.setBrush(gradient)
            painter.drawEllipse(QRectF(x + 10, cy - 15, 30, 30))
            if done:
                icon('check', '#64329B' if c['bg']!=DARK['bg'] else c['primary'], 20).paint(painter, int(x + 15), int(cy - 10), 20, 20)
            else:
                painter.setPen(QColor('#FFFFFF' if active else c['muted']))
                painter.drawText(QRectF(x + 10, cy - 15, 30, 30), Qt.AlignmentFlag.AlignCenter, str(i + 1))
            painter.setPen(QColor(('#6226A6' if c['bg']!=DARK['bg'] else c['primary']) if active else c['text'] if done else c['muted']))
            painter.drawText(QRectF(x + 52, cy - 22, width - 52, 44), Qt.AlignmentFlag.AlignVCenter, text)
            if i < 2:
                start, end = x + width + 12, starts[i + 1] - 12
                if start < end:
                    painter.setPen(QPen(QColor('#D7C8EA' if c['bg']!=DARK['bg'] else c['line']), 1.5))
                    painter.drawLine(int(start), int(cy), int(end), int(cy))


class WaveformSlider(QSlider):
    """Keyboard-accessible seeking over real audio peaks, with an idle baseline."""
    def __init__(self, colors):
        super().__init__(Qt.Orientation.Horizontal)
        self.colors = colors
        self.peaks = []
        self.setFixedHeight(36)
        self.setMinimumWidth(60)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName('Vị trí phát âm thanh')

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        progress = (self.value() - self.minimum()) / max(1, self.maximum() - self.minimum())
        left, span, cy = 5, max(1, self.width() - 10), self.height() / 2
        if self.peaks:
            count = min(len(self.peaks), max(1, int(span / 5)))
            peak_max = max(max(self.peaks), .001)
            for i in range(count):
                start = int(i * len(self.peaks) / count)
                end = max(start + 1, int((i + 1) * len(self.peaks) / count))
                height = max(2, 28 * max(self.peaks[start:end]) / peak_max)
                x = left + i * span / max(1, count - 1)
                color = QColor(self.colors['selected'] if x <= left + span * progress else self.colors['focus'])
                if x > left + span * progress: color.setAlpha(110)
                p.setPen(QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(int(x), int(cy - height / 2), int(x), int(cy + height / 2))
        else:
            p.setPen(QPen(QColor(self.colors['line']), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(left, int(cy), left + span, int(cy))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.colors['selected']))
        p.drawEllipse(QRectF(left + span * progress - 5, cy - 5, 10, 10))
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(self.colors['focus']), 1, Qt.PenStyle.DotLine))
            p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 6, 6)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(),
                                                   int(event.position().x()) - 5, max(1, self.width() - 10))
            self.setValue(value)
            self.sliderMoved.emit(value)
            self.setSliderDown(True)
            self.setFocus()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSliderDown():
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(),
                                                   int(event.position().x()) - 5, max(1, self.width() - 10))
            self.setValue(value)
            self.sliderMoved.emit(value)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setSliderDown(False)
        super().mouseReleaseEvent(event)


class TranscriptTable(QTableWidget):
    def __init__(self, colors):
        super().__init__(0, 3)
        self.setObjectName('bilingual_timeline')
        self.setHorizontalHeaderLabels(['Mốc giờ', 'TIẾNG TRUNG', 'TIẾNG VIỆT'])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 110)
        for column in (1, 2):
            self.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.verticalHeader().hide()
        self.setWordWrap(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setMinimumHeight(220)
        self.empty = QWidget(self.viewport())
        self.empty.setObjectName('transcript_empty')
        self.empty.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(self.empty)
        self.empty_layout = layout
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        layout.addStretch()
        badge = label(''); self.empty_badge = badge
        badge.setFixedSize(88, 88)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{colors['lavender']};border-radius:20px")
        badge.setPixmap(icon('audio', '#9B76D0' if colors['bg']!=DARK['bg'] else colors['focus'], 44).pixmap(44, 44))
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignHCenter)
        self.empty_title = label('Sẵn sàng chép lời', wrap=True)
        self.empty_title.setStyleSheet('font-family:"Inter";font-size:30px;font-weight:700')
        self.empty_description = label('Bắt đầu chép lời để xem nội dung Trung – Việt tại đây.', 'muted', True)
        self.empty_description.setStyleSheet(f"font-size:17px;font-weight:400;color:{colors['muted']}")
        for text in (self.empty_title, self.empty_description):
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(text)
        helper = label('Âm thanh gốc luôn được giữ lại', 'muted', True); self.empty_helper = helper
        helper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        helper.setStyleSheet(f"font-size:16px;font-style:italic;color:{colors['muted']}")
        layout.addWidget(helper)
        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty.setGeometry(self.viewport().rect())
        compact = self.viewport().height() < 260
        self.empty_badge.setFixedSize(56 if compact else 88, 56 if compact else 88)
        self.empty_helper.setVisible(self.viewport().height() >= 210)
        self.empty_layout.setSpacing(8 if compact else 12)


class FilePage(QFrame):
    def __init__(self, owner, audio):
        super().__init__()
        self.setObjectName('card')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        c = owner.colors
        arrow = asset('icons/chevron-down-' + ('dark' if c['bg']==DARK['bg'] else 'light') + '.svg').as_posix()
        self.setStyleSheet(f'''
            QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
            QLabel[role="muted"] {{font-size:14px;color:{c['muted']};}}
            QComboBox {{font-size:15px;font-weight:400;border:1px solid {c['line']};border-radius:10px;padding:8px 10px 8px 12px;min-height:22px;}}
            QComboBox::drop-down {{width:32px;border:0;background:transparent;}}
            QComboBox::down-arrow {{image:url("{arrow}");width:15px;height:15px;}}
            QHeaderView::section {{font-size:15px;font-weight:400;background:{c['lavender'] if c['bg']==DARK['bg'] else '#F3EEFB'};color:{c['text']};padding:12px 16px;border:0;border-bottom:1px solid {c['line']};}}
            QToolButton#file_export {{font-size:16px;font-weight:500;padding:8px 14px;border:1px solid {c['line']};border-radius:11px;}}
            QToolButton#file_export::menu-indicator {{image:url("{arrow}");width:15px;height:15px;subcontrol-origin:padding;subcontrol-position:right center;right:12px;}}
            QMenu {{font-family:"Inter";font-size:15px;background:{c['panel']};border:1px solid {c['line']};padding:6px;border-radius:10px;}}
            QMenu::item {{padding:10px 16px;border-radius:6px;}}
            QMenu::item:selected {{background:{c['lavender']};}}
        ''')
        body = QVBoxLayout(self)
        self.body = body
        body.setContentsMargins(22, 22, 22, 22)
        body.setSpacing(16)
        header = QHBoxLayout()
        header.setSpacing(16)
        badge = label(''); self.audio_badge = badge
        badge.setFixedSize(60, 60)
        badge.setStyleSheet(f"background:{c['pink']};border-radius:14px")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(icon('audio', c['text'], 32).pixmap(32, 32))
        header.addWidget(badge)
        words = QVBoxLayout()
        words.setSpacing(5)
        self.filename = ElidedLabel(audio['filename'] if audio else 'Chọn âm thanh để bắt đầu', text_width=480)
        self.filename.setObjectName('file_name')
        self.filename.setStyleSheet('font-size:22px;font-weight:700')
        words.addWidget(self.filename)
        metadata = f"{audio['filename'].rsplit('.', 1)[-1].upper()} · {int(audio['duration'])//60} phút {int(audio['duration'])%60:02d} giây · 1 âm thanh gốc" if audio else 'Chọn file hoặc kéo thả âm thanh vào cửa sổ'
        subtitle = ElidedLabel(metadata)
        subtitle.setStyleSheet(f"color:{c['muted']};font-size:15px")
        words.addWidget(subtitle)
        header.addLayout(words, 1)
        export = QToolButton()
        export.setObjectName('file_export')
        export.setText('Xuất văn bản')
        export.setToolTip('Xuất văn bản')
        export.setAccessibleName('Xuất văn bản')
        export.setIcon(icon('download', c['text'], 18))
        export.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(export)
        self.export_zh = menu.addAction('Tiếng Trung (.txt)', lambda: owner.export('zh'))
        self.export_vi = menu.addAction('Tiếng Việt (.txt)', lambda: owner.export('vi'))
        export.setMenu(menu)
        export.setFixedSize(196, 44)
        export.setIconSize(QSize(20, 20))
        self.export_button = export
        header.addWidget(export)
        body.addLayout(header)
        self.steps = WorkflowSteps(c)
        body.addWidget(self.steps)
        self.divider(body, c)
        toolbar = QHBoxLayout()
        self.versions = ComboBox()
        self.versions.setObjectName('file_versions')
        self.versions.setMinimumWidth(180)
        self.versions.setMaximumWidth(280)
        self.versions.addItem('Bản chép lời', None)
        if audio:
            for version in owner.store.versions(audio['id']):
                self.versions.addItem(f"v{version['number']} · {version['model']}", version['id'])
        self.versions.setCurrentIndex(max(0, self.versions.findData(owner.version_id)))
        self.versions.activated.connect(lambda _: owner.open_audio(owner.audio_id, self.versions.currentData(), transcript_only=self.versions.currentData() is None) if owner.audio_id else None)
        toolbar.addWidget(self.versions)
        toolbar.addStretch()
        self.notes_toggle = NotesSwitch(c)
        self.notes_toggle.setChecked(owner.store.setting('show_notes', False))
        self.notes_toggle.toggled.connect(owner.toggle_notes)
        toolbar.addWidget(self.notes_toggle)
        body.addLayout(toolbar)
        self.timeline = TranscriptTable(c)
        body.addWidget(self.timeline, 1)
        self.divider(body, c)
        body.addWidget(label('Âm thanh gốc', 'muted'))
        player = QHBoxLayout()
        player.setSpacing(12)
        self.play_button = PlaybackButton(c, owner.toggle_play)
        player.addWidget(self.play_button)
        self.play_label = label(timestamp(owner.player.position() / 1000), 'muted')
        self.play_label.setMinimumWidth(34)
        player.addWidget(self.play_label)
        self.seek_slider = WaveformSlider(c)
        self.seek_slider.setRange(0, max(1, int((audio or {}).get('duration', 0) * 1000)))
        self.seek_slider.setValue(owner.player.position())
        self.seek_slider.sliderMoved.connect(owner.player.setPosition)
        self.seek_slider.actionTriggered.connect(lambda _: owner.player.setPosition(self.seek_slider.sliderPosition()))
        player.addWidget(self.seek_slider, 1)
        self.duration_label = label(timestamp((audio or {}).get('duration', 0)), 'muted')
        player.addWidget(self.duration_label)
        speed = ComboBox()
        speed.setObjectName('playback_speed')
        for rate in (.75, 1., 1.25, 1.5):
            speed.addItem(f'{rate:g}×', rate)
        speed.setCurrentIndex(max(0, speed.findData(owner.player.playbackRate())))
        speed.setFixedWidth(86)
        speed.setAccessibleName('Tốc độ phát')
        speed.currentIndexChanged.connect(lambda _: owner.player.setPlaybackRate(speed.currentData()))
        player.addWidget(speed)
        self.volume_button = button('')
        self.volume_button.setFixedSize(36, 36)
        self.volume_button.setStyleSheet('border:0;background:transparent;padding:0')
        self.volume_button.clicked.connect(lambda: (owner.audio_output.setMuted(not owner.audio_output.isMuted()), owner.refresh_player()))
        player.addWidget(self.volume_button)
        self.play_button.setEnabled(bool(audio))
        self.seek_slider.setEnabled(bool(audio))
        speed.setEnabled(bool(audio))
        self.volume_button.setEnabled(bool(audio))
        body.addLayout(player)

    def set_compact(self, compact):
        margin = 14 if compact else 22
        self.body.setContentsMargins(margin, margin, margin, margin)
        self.body.setSpacing(8 if compact else 16)
        self.audio_badge.setFixedSize(52 if compact else 60, 52 if compact else 60)
        self.steps.setFixedHeight(52 if compact else 64)
        self.play_button.setFixedSize(48 if compact else 52, 48 if compact else 52)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, 'export_button'): return
        narrow = self.width() < 780
        self.export_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly if narrow else Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.export_button.setFixedWidth(48 if narrow else 196)

    @staticmethod
    def divider(body, colors):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{colors['line']};border:0")
        body.addWidget(line)
