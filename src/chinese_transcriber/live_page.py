"""Approved live workspace: transport, bilingual transcript and draft speech."""
import math
from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QProgressBar, QSizePolicy, QPlainTextEdit, QTableWidgetItem)
from .widgets import label, button
from .file_page import TranscriptTable, NotesSwitch, ui_font
from .theme import DARK, icon
from .audio import timestamp


class MicrophoneMeter(QProgressBar):
    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.setRange(0, 100); self.setValue(0)
        self.setObjectName('live_microphone_meter')
        self.setAccessibleName('Tín hiệu microphone')
        self.setMinimumWidth(212); self.setFixedHeight(62)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(ui_font(15, QFont.Weight.Medium)); p.setPen(QColor(self.colors['text']))
        p.drawText(self.rect().adjusted(0, 0, 0, -36), Qt.AlignmentFlag.AlignVCenter,
                   f'Tín hiệu microphone: {self.value()}%')
        p.setPen(Qt.PenStyle.NoPen)
        count = max(12, min(24, self.width()//14))
        step = self.width()/count; active = math.ceil(self.value()*count/100)
        for i in range(count):
            p.setBrush(QColor(('#B78BEB' if self.colors['bg']==DARK['bg'] else '#A276D6') if i<active else self.colors['line']))
            p.drawRoundedRect(QRectF(i*step, 36, min(8, step-4), 24), 3, 3)


class LiveTranscriptTable(TranscriptTable):
    def __init__(self, colors):
        super().__init__(colors)
        self.setMinimumHeight(180)
        self.empty_title.setText('Sẵn sàng nghe bài giảng')
        self.empty_description.setText('Bấm Bắt đầu ghi âm để xem nội dung Trung – Việt tại đây.')
        self.empty_description.setStyleSheet(f"font-size:15px;font-weight:400;color:{colors['muted']}")
        self.empty_helper.setText('Âm thanh gốc được lưu cùng phiên học.')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        compact = self.viewport().height()<260
        self.empty_badge.setFixedSize(48 if compact else 88, 48 if compact else 88)
        self.empty_helper.setVisible(self.viewport().height()>=240)
        if self.rowCount():
            self.resizeRowsToContents()
            for row in range(self.rowCount()): self.setRowHeight(row,max(90,self.rowHeight(row)))


class LivePage(QFrame):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner; self.colors = c = owner.colors
        self._narrow = None; self._compact = False
        self.setObjectName('live_workspace')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f'''
            QFrame#live_workspace {{background:{c['panel']};border:1px solid {c['line']};border-radius:20px;}}
            QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
            QFrame#live_transport {{background:{c['soft']};border:0;border-radius:16px;}}
            QLabel[role="muted"] {{font-size:15px;color:{c['muted']};}}
            QLabel#live_clock {{font-size:30px;font-weight:700;}}
            QLabel#live_transcript_title {{font-size:22px;font-weight:700;}}
            QHeaderView {{background:{c['panel']};border:0;}}
            QHeaderView::section {{font-size:15px;font-weight:600;background:{c['lavender'] if c['bg']==DARK['bg'] else '#F3EEFB'};color:{c['text']};padding:12px 16px;border:0;border-bottom:1px solid {c['line']};}}
            QHeaderView::section:first {{border-top-left-radius:12px;}}
            QHeaderView::section:last {{border-top-right-radius:12px;}}
            QTableWidget {{font-size:16px;border-radius:14px;}}
            QPushButton {{font-size:15px;font-weight:500;border-radius:11px;padding:0 12px;min-height:42px;max-height:42px;}}
            QPushButton[primary="true"] {{font-weight:600;}}
            QPushButton:disabled {{background:{c['soft']};color:{c['muted']};border:1px solid {c['line']};}}
            QFrame#live_draft {{background:{c['soft'] if c['bg']==DARK['bg'] else '#FCF9FF'};border:1px dashed {'#776187' if c['bg']==DARK['bg'] else '#D4B6F4'};border-radius:16px;}}
            QPlainTextEdit#live_interim {{background:transparent;border:0;padding:0;font-size:15px;color:{c['text']};}}
        ''')
        self.body = QVBoxLayout(self); self.body.setContentsMargins(20,20,20,20); self.body.setSpacing(18)
        self.transport = QFrame(); self.transport.setObjectName('live_transport')
        self.transport_grid = QGridLayout(self.transport)
        self.transport_grid.setContentsMargins(22,16,22,16)
        self.transport_grid.setHorizontalSpacing(18); self.transport_grid.setVerticalSpacing(10)
        self.status = QWidget(); self.status.setFixedWidth(134)
        status_body = QVBoxLayout(self.status); status_body.setContentsMargins(0,0,0,0); status_body.setSpacing(4)
        state_row = QHBoxLayout(); state_row.setSpacing(8)
        self.status_dot = label(''); self.status_dot.setFixedSize(10,10)
        self.status_text = label('Đang dừng'); self.status_text.setStyleSheet('font-size:14px')
        state_row.addWidget(self.status_dot); state_row.addWidget(self.status_text,1); status_body.addLayout(state_row)
        self.clock = label('00:00'); self.clock.setObjectName('live_clock'); status_body.addWidget(self.clock)
        self.meter = MicrophoneMeter(c)
        self.separators = []
        for _ in range(2):
            line = QFrame(); line.setFixedWidth(1); line.setStyleSheet(f"background:{c['line']};border:0")
            self.separators.append(line)
        self.actions = QWidget()
        action_row = QHBoxLayout(self.actions); action_row.setContentsMargins(0,0,0,0); action_row.setSpacing(10)
        self.record_button = button('Bắt đầu ghi âm', owner.start_recording, True)
        self.record_button.setObjectName('live_record'); self.record_button.setIcon(icon('record',c['selected'],18))
        self.pause_button = button('Tạm dừng', owner.pause_recording)
        self.pause_button.setObjectName('live_pause'); self.pause_button.setIcon(icon('pause',c['text'],18))
        self.stop_button = button('Dừng && lưu', owner.stop_recording)
        self.stop_button.setAccessibleName('Dừng & lưu')
        self.stop_button.setObjectName('live_stop'); self.stop_button.setIcon(icon('stop',c['text'],18))
        for control,width in ((self.record_button,174),(self.pause_button,128),(self.stop_button,138)):
            control.setFixedWidth(width)
            control.setIconSize(QSize(18,18)); action_row.addWidget(control)
        self.body.addWidget(self.transport)
        toolbar = QHBoxLayout(); toolbar.setSpacing(16)
        title = label('Bản chép lời'); title.setObjectName('live_transcript_title')
        toolbar.addWidget(title); toolbar.addStretch()
        toggle_colors = dict(c,focus='#B78BEB' if c['bg']==DARK['bg'] else '#7C33C5')
        self.follow = NotesSwitch(toggle_colors); self.follow.setText('Theo đoạn mới nhất')
        self.follow.setAccessibleName('Theo đoạn mới nhất'); self.follow.setChecked(owner.live_follow)
        self.follow.toggled.connect(self.follow_changed); toolbar.addWidget(self.follow)
        self.body.addLayout(toolbar)
        self.timeline = LiveTranscriptTable(c); self.body.addWidget(self.timeline,1)
        self.timeline.verticalScrollBar().actionTriggered.connect(lambda _:self.follow.setChecked(False))
        self.draft = QFrame(); self.draft.setObjectName('live_draft')
        draft_body = QVBoxLayout(self.draft); draft_body.setContentsMargins(20,14,16,12); draft_body.setSpacing(8)
        draft_heading = QHBoxLayout(); draft_heading.setSpacing(12)
        mic = label(''); mic.setFixedSize(26,26); mic.setPixmap(icon('mic',c['text'],24).pixmap(24,24))
        draft_heading.addWidget(mic)
        draft_title = label('Câu đang nghe'); draft_title.setStyleSheet('font-size:20px;font-weight:700')
        draft_heading.addWidget(draft_title); draft_heading.addStretch()
        badge = label('Chưa chốt'); badge.setStyleSheet(f"font-size:14px;background:{c['lavender']};color:{c['muted']};border-radius:14px;padding:6px 14px")
        draft_heading.addWidget(badge); draft_body.addLayout(draft_heading)
        self.interim = QPlainTextEdit(); self.interim.setObjectName('live_interim')
        self.interim.setReadOnly(True); self.interim.setMinimumHeight(28)
        self.interim.setPlaceholderText('Câu đang nghe sẽ xuất hiện tại đây.')
        self.interim.setAccessibleName('Câu đang nghe · Chưa chốt')
        self.interim.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        draft_body.addWidget(self.interim,1); self.body.addWidget(self.draft)
        self.reflow(False); self.set_compact(False)

    def follow_changed(self, enabled):
        self.owner.live_follow = enabled
        if enabled: self.timeline.scrollToBottom()

    def reflow(self, narrow):
        if self._narrow==narrow: return
        self._narrow = narrow
        grid = self.transport_grid
        while grid.count(): grid.takeAt(0)
        for column in range(5): grid.setColumnStretch(column,0)
        grid.addWidget(self.status,0,0); grid.addWidget(self.separators[0],0,1)
        grid.addWidget(self.meter,0,2); grid.setColumnStretch(2,1)
        self.separators[1].setVisible(not narrow)
        if narrow:
            grid.addWidget(self.actions,1,0,1,3,Qt.AlignmentFlag.AlignRight)
        else:
            grid.addWidget(self.separators[1],0,3); grid.addWidget(self.actions,0,4)

    def set_compact(self, compact):
        self._compact = compact
        margin = 14 if compact else 20
        self.body.setContentsMargins(margin,margin,margin,margin); self.body.setSpacing(10 if compact else 18)
        self.transport_grid.setContentsMargins(16 if compact else 22,10 if compact else 16,16 if compact else 22,10 if compact else 16)
        self.draft.setFixedHeight(96 if compact else 110)
        self.reflow(self.available_width()<(940 if compact else 970))

    def available_width(self):
        # A wide layout can impose a minimum width on the scroll area's child.
        # Use the window's available space so it can reflow before being shrunk.
        margins=self.owner.workspace_layout.contentsMargins()
        return self.owner.width()-self.owner.rail.width()-self.owner.context.width()-margins.left()-margins.right()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow(self.available_width()<(940 if self._compact else 970))

    def set_state(self, state, seconds, level, recording, paused, busy):
        self.status_text.setText(state); self.clock.setText(timestamp(seconds))
        dot = self.colors['success'] if recording and not paused else self.colors['muted']
        self.status_dot.setStyleSheet(f'background:{dot};border-radius:5px')
        self.meter.setValue(max(0,min(100,int(level))) if recording and not paused else 0)
        self.record_button.setEnabled(not recording and not busy)
        self.pause_button.setEnabled(recording and not busy); self.stop_button.setEnabled(recording and not busy)
        self.pause_button.setText('Tiếp tục' if paused else 'Tạm dừng')
        self.pause_button.setIcon(icon('play' if paused else 'pause',self.colors['text'],18))
        if state=='Đang lưu…':
            title,description='Đang lưu phiên học…','Âm thanh và các câu đã chốt đang được lưu.'
        elif paused:
            title,description='Tạm dừng ghi âm','Bấm Tiếp tục để nghe và chép lời tiếp.'
        elif state=='Chờ microphone':
            title,description='Chờ âm thanh từ microphone','Đồng hồ sẽ chạy khi thiết bị bắt đầu gửi âm thanh.'
        elif recording:
            title,description='Đang nghe bài giảng…','Nội dung sẽ xuất hiện khi một câu được chốt.'
        elif busy:
            title,description='Đang xử lý…','Chờ tác vụ hiện tại hoàn tất để bắt đầu ghi âm.'
        else:
            title,description='Sẵn sàng nghe bài giảng','Bấm Bắt đầu ghi âm để xem nội dung Trung – Việt tại đây.'
        self.timeline.empty_title.setText(title); self.timeline.empty_description.setText(description)

    def set_interim(self, text):
        if text!=self.interim.toPlainText():
            self.interim.setPlainText(text)
            self.interim.verticalScrollBar().setValue(self.interim.verticalScrollBar().maximum())

    def set_segments(self, rows, show_notes=False):
        table = self.timeline; position = table.verticalScrollBar().value()
        table.setRowCount(len(rows)); table.empty.setVisible(not rows)
        for i,row in enumerate(rows):
            state = row.get('translation_status','untranslated')
            translated = row.get('vi') or {'queued':'Trong hàng đợi dịch','translating':'Đang dịch…','failed':'Dịch lỗi · Lưu phiên để thử lại'}.get(state,'Đã chốt câu · Chưa kết nối dịch')
            if show_notes and row.get('note'): translated+='\nⓘ '+row['note']
            values = [timestamp(row['start'])+'\n'+timestamp(row['end']),row['zh'],translated]
            changed = False
            for j,text in enumerate(values):
                item = table.item(i,j)
                if item is None or item.text()!=text:
                    item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
                    if j==0 or (j==2 and not row.get('vi')): item.setForeground(QColor(self.colors['muted']))
                    table.setItem(i,j,item); changed = True
            if changed:
                table.resizeRowToContents(i); table.setRowHeight(i,max(90,table.rowHeight(i)))
        if self.follow.isChecked(): table.scrollToBottom()
        else: table.verticalScrollBar().setValue(position)
