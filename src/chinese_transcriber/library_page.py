"""Approved audio library with real source records and saved versions."""
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication, QScrollArea,
    QStackedWidget, QSizePolicy)
from .widgets import label, button, clear
from .file_page import ElidedLabel, ui_font
from .model_selector import model_name, effort_name
from .theme import icon, DARK
from .audio import timestamp


STATUS = {'complete':'Hoàn tất','running':'Đang xử lý','queued':'Chờ xử lý',
          'failed':'Lỗi','interrupted':'Gián đoạn','partial':'Chưa đầy đủ'}


def library_context_styles(c):
    return f'''
        QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
        QLabel[role="muted"] {{font-size:13px;color:{c['muted']};}}
        QLabel#library_context_title {{font-size:22px;font-weight:700;}}
        QPushButton[library_nav="true"] {{text-align:left;padding:0 12px;min-height:42px;max-height:42px;font-size:15px;border:1px solid {c['line']};border-radius:11px;}}
        QPushButton[library_selected="true"] {{background:{c['lavender']};border-color:{c['lavender']};}}
        QPushButton#library_connection {{background:{c['soft']};color:{c['success']};border:0;text-align:left;padding:10px 12px;font-size:13px;}}
    '''


class LibraryEmptyState(QWidget):
    def __init__(self, colors, details=False, callback=None):
        super().__init__()
        self.details = details; self.filtered = False
        self.setMinimumWidth(0)
        self.body = QVBoxLayout(self); self.body.setContentsMargins(16,16,16,16); self.body.setSpacing(14)
        self.body.addStretch()
        size = 104 if details else 112
        self.badge = label(''); self.badge.setFixedSize(size,size)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet(f"background:{colors['lavender']};border-radius:{size//2 if details else 28}px")
        self.badge.setPixmap(icon('versions' if details else 'audio-file',colors['muted'],56).pixmap(56,56))
        self.body.addWidget(self.badge,0,Qt.AlignmentFlag.AlignHCenter)
        self.heading = label('Chọn một âm thanh' if details else 'Chưa có âm thanh',wrap=True)
        self.heading.setStyleSheet(f'font-size:{24 if details else 28}px;font-weight:700')
        self.description = label('Các bản chép lời và bản dịch đã lưu sẽ xuất hiện tại đây.' if details else 'Nhập file ghi âm để bắt đầu bài học đầu tiên.','muted',True)
        self.description.setStyleSheet(f"font-size:15px;color:{colors['muted']}")
        self.description.setMaximumWidth(340 if details else 380)
        for widget in (self.heading,self.description):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter); self.body.addWidget(widget)
        self.body.setAlignment(self.description,Qt.AlignmentFlag.AlignHCenter)
        self.import_button = None; self.formats = None
        if not details:
            self.import_button = button('Nhập file âm thanh',callback,True)
            self.import_button.setObjectName('library_empty_import')
            self.import_button.setIcon(icon('upload',colors['on_primary'],20)); self.import_button.setIconSize(QSize(20,20))
            self.import_button.setFixedHeight(44)
            self.body.addWidget(self.import_button,0,Qt.AlignmentFlag.AlignHCenter)
            self.formats = label('WAV, MP3, M4A và các định dạng được hỗ trợ','muted',True)
            self.formats.setAlignment(Qt.AlignmentFlag.AlignCenter); self.formats.setStyleSheet(f"font-size:13px;color:{colors['muted']}")
            self.body.addWidget(self.formats)
        self.body.addStretch()
        self.fit_description()

    def set_filtered(self, filtered):
        self.filtered = filtered
        self.heading.setText('Không tìm thấy âm thanh' if filtered else 'Chưa có âm thanh')
        self.description.setText('Thử từ khóa khác hoặc xóa tìm kiếm để xem toàn bộ thư viện.' if filtered else 'Nhập file ghi âm để bắt đầu bài học đầu tiên.')
        self.fit_description()
        self.import_button.setText('Xóa tìm kiếm' if filtered else 'Nhập file âm thanh')
        self.formats.setVisible(not filtered and self.height()>=340)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.fit_description()
        self.badge.setVisible(self.height()>=(280 if self.details else 340))
        if self.formats: self.formats.setVisible(self.height()>=340 and not self.filtered)
        self.body.setSpacing(8 if self.height()<300 else 14)

    def fit_description(self):
        if not hasattr(self,'description'): return
        width=max(1,min(340 if self.details else 380,self.width()-32))
        self.description.setFixedWidth(width)
        self.description.setFixedHeight(max(self.description.fontMetrics().lineSpacing(),self.description.heightForWidth(width)))


class AudioCellDelegate(QStyledItemDelegate):
    def __init__(self, colors, parent):
        super().__init__(parent); self.colors = colors

    def paint(self,painter,option,index):
        row = index.data(Qt.ItemDataRole.UserRole)
        if not row: return super().paint(painter,option,index)
        painter.save()
        background = QStyleOptionViewItem(option); self.initStyleOption(background,index); background.text=''
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem,background,painter,option.widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QColor(self.colors['pink']))
        badge = QRectF(option.rect.x()+12,option.rect.center().y()-18,36,36)
        painter.drawRoundedRect(badge,10,10)
        icon('audio',self.colors['text'],22).paint(painter,int(badge.x()+7),int(badge.y()+7),22,22)
        custom_title = row['title'] and row['title']!=Path(row['filename']).stem
        title = row['title'] if custom_title else row['filename']
        secondary = row['filename'] if custom_title else Path(row['filename']).suffix.removeprefix('.').upper()+' · 1 âm thanh gốc'
        x=option.rect.x()+60; width=max(0,option.rect.width()-72)
        painter.setFont(ui_font(15,QFont.Weight.DemiBold))
        painter.setPen(QColor(self.colors['text']))
        painter.drawText(QRectF(x,option.rect.y()+13,width,24),Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(title,Qt.TextElideMode.ElideMiddle,width))
        painter.setFont(ui_font(13)); painter.setPen(QColor(self.colors['muted']))
        painter.drawText(QRectF(x,option.rect.y()+40,width,20),Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(secondary,Qt.TextElideMode.ElideMiddle,width))
        painter.restore()


class AudioTable(QTableWidget):
    def __init__(self,colors,empty_callback):
        super().__init__(0,5)
        self.setObjectName('library_audio_table')
        self.setHorizontalHeaderLabels(['Âm thanh','Thời lượng','Ngày nhập','Nguồn','Bản dịch'])
        self.verticalHeader().hide(); self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setMinimumSize(0,190); self.setWordWrap(False)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        for column,width in ((1,96),(2,100),(3,90),(4,76)):
            self.horizontalHeader().setSectionResizeMode(column,QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(column,width)
        self.setItemDelegateForColumn(0,AudioCellDelegate(colors,self))
        self.empty = LibraryEmptyState(colors,callback=empty_callback)
        self.empty.setParent(self.viewport())

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.empty.setGeometry(self.viewport().rect())


class LibraryPage(QFrame):
    def __init__(self,owner):
        super().__init__()
        self.owner=owner; self.colors=c=owner.colors
        self.rows=[]; self.selected_id=None; self.version_cards=[]; self.write_buttons=[]
        self.transcript_button=None; self.compare_button=None; self._narrow=None; self.total=0
        self.setObjectName('library_workspace')
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f'''
            QFrame#library_workspace {{background:{c['panel']};border:1px solid {c['line']};border-radius:20px;}}
            QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
            QLabel[role="muted"] {{font-size:14px;color:{c['muted']};}}
            QLabel#library_heading {{font-size:22px;font-weight:700;}}
            QLabel#library_versions_heading {{font-size:20px;font-weight:700;}}
            QLineEdit#library_search {{font-size:15px;border-radius:12px;padding:8px 12px;}}
            QPushButton {{font-size:15px;border-radius:11px;padding:0 12px;min-height:42px;max-height:42px;}}
            QPushButton[primary="true"] {{font-weight:600;}}
            QTableWidget#library_audio_table {{border:1px solid {c['line']};border-radius:14px;background:{c['panel']};selection-background-color:{c['lavender']};}}
            QHeaderView {{background:{c['panel']};border:0;}}
            QHeaderView::section {{font-size:14px;font-weight:500;background:{c['lavender'] if c['bg']==DARK['bg'] else '#F4EFFA'};color:{c['text']};padding:14px 8px;border:0;border-bottom:1px solid {c['line']};}}
            QHeaderView::section:first {{border-top-left-radius:12px;}}
            QHeaderView::section:last {{border-top-right-radius:12px;}}
            QFrame#library_details {{background:{c['panel']};border:1px solid {c['line']};border-radius:14px;}}
            QFrame[library_version="true"] {{background:{c['soft']};border:1px solid {c['line']};border-radius:12px;}}
        ''')
        self.body=QVBoxLayout(self); self.body.setContentsMargins(20,20,20,20); self.body.setSpacing(20)
        toolbar=QHBoxLayout(); toolbar.setSpacing(14)
        self.search=QLineEdit(); self.search.setObjectName('library_search'); self.search.setMinimumWidth(0)
        self.search.setFixedHeight(44); self.search.setPlaceholderText('Tìm bài giảng, tên file…')
        self.search.setAccessibleName('Tìm bài giảng, tên file')
        self.search.addAction(icon('search',c['muted'],22),QLineEdit.ActionPosition.LeadingPosition)
        self.search.setText(getattr(owner,'_library_query',''))
        self.import_button=button('Nhập file mới',owner.choose_audio,True)
        self.import_button.setObjectName('library_import'); self.import_button.setFixedSize(170,44)
        self.import_button.setIcon(icon('upload',c['on_primary'],20)); self.import_button.setIconSize(QSize(20,20))
        toolbar.addWidget(self.search,1); toolbar.addWidget(self.import_button); self.body.addLayout(toolbar)
        self.grid=QGridLayout(); self.grid.setContentsMargins(0,0,0,0); self.grid.setSpacing(18)
        self.list_section=QWidget(); list_body=QVBoxLayout(self.list_section)
        list_body.setContentsMargins(0,0,0,0); list_body.setSpacing(14)
        heading=QHBoxLayout(); heading.setSpacing(12)
        title=label('Âm thanh'); title.setObjectName('library_heading'); heading.addWidget(title)
        self.count=label('0 nguồn'); self.count.setStyleSheet(f"font-size:13px;background:{c['lavender']};color:{c['muted']};padding:5px 10px;border-radius:13px")
        heading.addWidget(self.count); heading.addStretch(); list_body.addLayout(heading)
        self.table=AudioTable(c,self.empty_action); list_body.addWidget(self.table,1)
        self.details_section=QWidget(); details_section_body=QVBoxLayout(self.details_section)
        details_section_body.setContentsMargins(0,0,0,0); details_section_body.setSpacing(14)
        details_heading=QHBoxLayout(); details_heading.setSpacing(10)
        glyph=label(''); glyph.setFixedSize(26,30); glyph.setPixmap(icon('versions',c['muted'],26).pixmap(26,26)); details_heading.addWidget(glyph)
        title=label('Phiên bản đã lưu'); title.setObjectName('library_versions_heading'); details_heading.addWidget(title); details_heading.addStretch()
        details_section_body.addLayout(details_heading)
        self.details=QFrame(); self.details.setObjectName('library_details'); self.details.setMinimumHeight(170)
        details_layout=QVBoxLayout(self.details); details_layout.setContentsMargins(0,0,0,0)
        self.details_stack=QStackedWidget(); details_layout.addWidget(self.details_stack)
        self.details_empty=LibraryEmptyState(c,details=True); self.details_stack.addWidget(self.details_empty)
        self.details_scroll=QScrollArea(); self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.details_content=QWidget(); self.details_content.setMinimumWidth(0)
        self.details_body=QVBoxLayout(self.details_content); self.details_body.setContentsMargins(16,18,16,18); self.details_body.setSpacing(14)
        self.details_scroll.setWidget(self.details_content); self.details_stack.addWidget(self.details_scroll)
        details_section_body.addWidget(self.details,1)
        self.body.addLayout(self.grid,1)
        self.table.itemSelectionChanged.connect(self.select_row)
        self.table.activated.connect(lambda index:self.open_row(index.row()))
        self.search.textChanged.connect(self.search_changed)
        self.populate(); self.set_compact(owner.height()<820)

    def empty_action(self):
        if self.table.empty.filtered: self.search.clear()
        else: self.owner.choose_audio()

    def search_changed(self,text):
        self.owner._library_query=text; self.populate()

    def show_all(self):
        if self.search.text(): self.search.clear()
        else: self.populate()

    def populate(self):
        all_rows=self.owner.store.list_audio(); self.total=len(all_rows)
        query=self.search.text().strip().casefold()
        self.rows=[row for row in all_rows if query in (row['title']+' '+row['filename']).casefold()]
        preferred=getattr(self.owner,'_library_selected_audio_id',self.owner.audio_id)
        self.table.blockSignals(True); self.table.clearContents(); self.table.setRowCount(len(self.rows))
        for i,row in enumerate(self.rows):
            values=[row['title']+'\n'+row['filename'],timestamp(row['duration']),row['created'][:10],
                    'Tải lên' if row['source']=='upload' else 'Ghi trực tiếp',str(row['version_count'])]
            for j,text in enumerate(values):
                item=QTableWidgetItem(text); item.setData(Qt.ItemDataRole.UserRole,row); item.setToolTip(text)
                if j: item.setForeground(QColor(self.colors['muted']))
                self.table.setItem(i,j,item)
            self.table.setRowHeight(i,76)
        if self.rows:
            index=next((i for i,row in enumerate(self.rows) if row['id']==preferred),0)
            self.table.selectRow(index)
        self.table.blockSignals(False)
        self.count.setText(f'{len(self.rows)} nguồn'); self.count.setToolTip(f'Hiển thị {len(self.rows)}/{self.total} âm thanh')
        self.table.empty.setVisible(not self.rows); self.table.empty.set_filtered(bool(query and self.total))
        self.select_row()

    def open_row(self,index):
        if 0<=index<len(self.rows): self.owner.open_audio(self.rows[index]['id'])

    def select_row(self):
        current=self.table.currentRow()
        self.version_cards=[]; self.write_buttons=[]; self.transcript_button=None; self.compare_button=None
        clear(self.details_body)
        if not 0<=current<len(self.rows):
            self.selected_id=None; self.details_stack.setCurrentIndex(0); self.refresh_busy(); return
        audio=self.rows[current]; self.selected_id=audio['id']; self.owner._library_selected_audio_id=audio['id']
        self.details_stack.setCurrentIndex(1)
        name=ElidedLabel(audio['filename']); name.setStyleSheet('font-size:16px;font-weight:600')
        self.details_body.addWidget(name)
        metadata=label(f"{Path(audio['filename']).suffix.removeprefix('.').upper()} · {timestamp(audio['duration'])} · 1 âm thanh gốc",'muted',True)
        self.details_body.addWidget(metadata)
        actions=QHBoxLayout(); actions.setSpacing(10)
        self.open_button=button('Mở / chép lời',lambda:self.owner.open_audio(audio['id']),True)
        self.open_button.setObjectName('library_open_audio'); actions.addWidget(self.open_button,1)
        self.delete_audio_button=button('',lambda:self.owner.delete_audio(audio['id']),danger=True)
        self.delete_audio_button.setIcon(icon('trash',self.colors['danger'],20)); self.delete_audio_button.setFixedWidth(44)
        self.delete_audio_button.setAccessibleName('Xóa âm thanh'); self.delete_audio_button.setToolTip('Xóa âm thanh')
        actions.addWidget(self.delete_audio_button); self.details_body.addLayout(actions); self.write_buttons.append(self.delete_audio_button)
        transcript=self.owner.store.latest_transcript(audio['id'],True) or self.owner.store.latest_transcript(audio['id'],False)
        if transcript:
            panel,body=self.version_panel('Bản chép lời tiếng Trung',transcript['status'])
            body.addWidget(label(transcript['created'][:10],'muted'))
            self.transcript_button=button('Mở bản chép lời',lambda:self.owner.open_audio(audio['id'],transcript_only=True))
            body.addWidget(self.transcript_button); self.details_body.addWidget(panel)
        versions=self.owner.store.versions(audio['id'])
        for version in versions:
            panel,body=self.version_panel(f"Bản dịch v{version['number']}",version['status'])
            model=model_name(dict(model=version['model'],displayName=version['model']))
            body.addWidget(label(model+' · '+effort_name(version['effort']),'muted',True))
            body.addWidget(label(version['created'][:10],'muted'))
            row=QHBoxLayout(); row.setSpacing(8)
            open_button=button('Mở bản dịch',lambda checked=False,v=version:self.owner.open_audio(v['audio_id'],v['id']))
            delete_button=button('Xóa',lambda checked=False,v=version:self.owner.delete_version(v),danger=True)
            delete_button.setAccessibleName(f"Xóa bản dịch v{version['number']}")
            row.addWidget(open_button,1); row.addWidget(delete_button); body.addLayout(row)
            self.write_buttons.append(delete_button)
            resume=None
            if version['status']!='complete':
                resume=button('Tiếp tục / thử lại',lambda checked=False,v=version:self.owner.resume_translation(v['id']))
                body.addWidget(resume); self.write_buttons.append(resume)
            self.version_cards.append(dict(version=version,panel=panel,open_button=open_button,delete_button=delete_button,resume_button=resume))
            self.details_body.addWidget(panel)
        if not versions:
            self.details_body.addWidget(label('Chưa có bản dịch. Mở âm thanh để chép lời và tạo bản dịch mới.','muted',True))
        if len(versions)>1:
            self.compare_button=button('So sánh hai phiên bản',lambda:self.owner.compare_versions(versions[1],versions[0]))
            self.details_body.addWidget(self.compare_button)
        self.details_body.addStretch(); self.details_scroll.verticalScrollBar().setValue(0); self.refresh_busy()

    def version_panel(self,title,status):
        panel=QFrame(); panel.setProperty('library_version',True)
        body=QVBoxLayout(panel); body.setContentsMargins(12,12,12,12); body.setSpacing(8)
        heading=label(title,wrap=True); heading.setStyleSheet('font-size:16px;font-weight:600'); body.addWidget(heading)
        badge=label(STATUS.get(status,status)); badge.setStyleSheet(f"font-size:13px;color:{self.colors['success'] if status=='complete' else self.colors['danger'] if status=='failed' else self.colors['muted']}")
        body.addWidget(badge)
        return panel,body

    def refresh_busy(self):
        idle=not self.owner.is_busy and not self.owner.recording
        self.import_button.setEnabled(idle)
        self.table.empty.import_button.setEnabled(self.table.empty.filtered or idle)
        for control in self.write_buttons: control.setEnabled(idle)

    def set_compact(self,compact):
        margin=14 if compact else 20
        self.body.setContentsMargins(margin,margin,margin,margin); self.body.setSpacing(14 if compact else 20)
        self.reflow()

    def reflow(self):
        margins=self.owner.workspace_layout.contentsMargins()
        width=self.owner.width()-self.owner.rail.width()-self.owner.context.width()-margins.left()-margins.right()
        narrow=width<900
        if self._narrow==narrow: return
        self._narrow=narrow
        while self.grid.count(): self.grid.takeAt(0)
        for i in range(2): self.grid.setColumnStretch(i,0); self.grid.setRowStretch(i,0)
        if narrow:
            self.grid.addWidget(self.list_section,0,0); self.grid.addWidget(self.details_section,1,0)
            self.grid.setRowStretch(0,11); self.grid.setRowStretch(1,10); self.grid.setColumnStretch(0,1)
        else:
            self.grid.addWidget(self.list_section,0,0); self.grid.addWidget(self.details_section,0,1)
            self.grid.setColumnStretch(0,64); self.grid.setColumnStretch(1,36); self.grid.setRowStretch(0,1)

    def resizeEvent(self,event):
        super().resizeEvent(event); self.reflow()
