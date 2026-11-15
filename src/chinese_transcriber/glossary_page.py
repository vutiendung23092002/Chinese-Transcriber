"""Approved course context and glossary editor, backed by the existing store."""
from PySide6.QtCore import Qt, QSize, Signal, QPersistentModelIndex
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionViewItem, QAbstractItemDelegate, QApplication,
    QSizePolicy, QStyle)
from .widgets import label, button
from .theme import icon, DARK


PLACEHOLDERS = ('Nhập thuật ngữ…','Bản dịch ưu tiên…','Ngữ cảnh, cách dùng…')


def glossary_context_styles(c):
    return f'''
        QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
        QLabel[role="muted"] {{font-size:13px;color:{c['muted']};}}
        QLabel#prompts_context_title {{font-size:22px;font-weight:700;}}
        QPushButton#glossary_new {{background:{c['lavender']};color:{c['text']};border:0;border-radius:11px;padding:0 12px;min-height:44px;max-height:44px;font-size:15px;font-weight:600;}}
        QListWidget#glossary_sets {{background:transparent;border:0;padding:0;font-size:15px;}}
        QListWidget#glossary_sets::item {{background:{c['panel']};border:1px solid {c['line']};border-radius:10px;padding:8px 10px;}}
        QListWidget#glossary_sets::item:selected {{background:{c['lavender']};color:{c['text']};border-color:{c['lavender']};}}
        QPushButton#prompts_connection {{background:{c['soft']};color:{c['success']};border:0;text-align:left;padding:10px 12px;font-size:13px;}}
    '''


class EntryDelegate(QStyledItemDelegate):
    draftChanged = Signal()

    def __init__(self,colors,parent):
        super().__init__(parent)
        self.colors=colors; self.editor=None; self.pending=None

    def paint(self,painter,option,index):
        if not index.data(Qt.ItemDataRole.DisplayRole):
            option=QStyleOptionViewItem(option); self.initStyleOption(option,index)
            option.text=PLACEHOLDERS[index.column()]
            option.palette.setColor(QPalette.ColorRole.Text,QColor(self.colors['muted']))
            option.palette.setColor(QPalette.ColorRole.HighlightedText,QColor(self.colors['muted']))
            style=option.widget.style() if option.widget else QApplication.style()
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem,option,painter,option.widget)
        else:
            super().paint(painter,option,index)

    def createEditor(self,parent,option,index):
        editor=super().createEditor(parent,option,index)
        if isinstance(editor,QLineEdit):
            self.editor=editor; persistent=QPersistentModelIndex(index)
            editor.setPlaceholderText(PLACEHOLDERS[index.column()])
            def changed(text):
                self.pending=(persistent,text); self.draftChanged.emit()
            editor.textEdited.connect(changed)
        return editor

    def setModelData(self,editor,model,index):
        self.pending=None
        super().setModelData(editor,model,index)
        self.draftChanged.emit()

    def destroyEditor(self,editor,index):
        if self.editor is editor:
            self.editor=None; self.pending=None
        super().destroyEditor(editor,index)
        self.draftChanged.emit()


class GlossaryPage(QFrame):
    def __init__(self,owner,chosen,entries):
        super().__init__()
        self.owner=owner; self.colors=c=owner.colors
        self.setObjectName('glossary_workspace')
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f'''
            QFrame#glossary_workspace {{background:{c['panel']};border:1px solid {c['line']};border-radius:20px;}}
            QWidget {{font-family:"Inter";font-size:15px;font-weight:400;}}
            QLabel[role="muted"] {{font-size:13px;color:{c['muted']};}}
            QLabel[glossary_caption="true"] {{font-size:15px;font-weight:600;}}
            QLabel#glossary_terms_heading {{font-size:22px;font-weight:700;}}
            QLineEdit#glossary_name {{font-size:15px;border:1px solid {c['line']};border-radius:12px;padding:0 12px;}}
            QPlainTextEdit#glossary_context {{font-size:15px;border:1px solid {c['line']};border-radius:12px;padding:12px;}}
            QTableWidget#glossary_entries {{font-size:15px;border:1px solid {c['line']};border-radius:14px;gridline-color:{c['line']};}}
            QTableWidget#glossary_entries::item {{padding:10px 14px;}}
            QTableWidget#glossary_entries QLineEdit {{font-size:15px;padding:6px 10px;border:1px solid {c['focus']};border-radius:5px;}}
            QHeaderView {{background:{c['panel']};border:0;}}
            QHeaderView::section {{font-size:14px;font-weight:600;background:{c['lavender'] if c['bg']==DARK['bg'] else '#F3EFF8'};color:{c['text']};padding:12px 10px;border:0;border-bottom:1px solid {c['line']};}}
            QHeaderView#glossary_columns::section:last {{border-top-right-radius:12px;}}
            QTableCornerButton::section {{background:{c['panel']};border:0;border-bottom:1px solid {c['line']};border-right:1px solid {c['line']};border-top-left-radius:12px;}}
            QPushButton {{font-size:15px;border-radius:11px;padding:0 14px;min-height:42px;max-height:42px;}}
            QPushButton[primary="true"] {{font-weight:600;}}
            QPushButton:disabled {{background:{c['soft']};color:{c['muted']};border:1px solid {c['line']};}}
        ''')
        self.body=QVBoxLayout(self); self.body.setContentsMargins(20,20,20,20); self.body.setSpacing(18)
        name_group=QVBoxLayout(); name_group.setSpacing(8)
        name_heading=QHBoxLayout()
        name_heading.addWidget(self.caption('Tên bộ thuật ngữ')); name_heading.addStretch()
        self.save_status=label('Chưa lưu'); self.save_status.setObjectName('glossary_save_status'); name_heading.addWidget(self.save_status)
        name_group.addLayout(name_heading)
        self.name=QLineEdit(chosen['name'] if chosen else '')
        self.name.setObjectName('glossary_name'); self.name.setMinimumWidth(0); self.name.setFixedHeight(44)
        self.name.setPlaceholderText('Ví dụ: Đại số tuyến tính'); self.name.setAccessibleName('Tên bộ thuật ngữ')
        name_group.addWidget(self.name); self.body.addLayout(name_group)
        context_group=QVBoxLayout(); context_group.setSpacing(8)
        context_group.addWidget(self.caption('Bối cảnh bài giảng'))
        self.context=QPlainTextEdit(chosen['context'] if chosen else '')
        self.context.setObjectName('glossary_context'); self.context.setMinimumWidth(0)
        self.context.setPlaceholderText('Môn học, chủ đề, cách dịch mong muốn…'); self.context.setAccessibleName('Bối cảnh bài giảng')
        context_group.addWidget(self.context)
        self.context_helper=label('Bối cảnh này được dùng cùng bộ thuật ngữ khi dịch.','muted',True)
        context_group.addWidget(self.context_helper); self.body.addLayout(context_group)
        toolbar=QHBoxLayout(); toolbar.setSpacing(12)
        title=label('Thuật ngữ ưu tiên'); title.setObjectName('glossary_terms_heading'); toolbar.addWidget(title)
        self.count=label('0 thuật ngữ'); self.count.setStyleSheet(f"font-size:13px;background:{c['soft']};color:{c['muted']};padding:6px 12px;border-radius:14px")
        self.count.setFixedHeight(28)
        toolbar.addWidget(self.count); toolbar.addStretch()
        self.add_button=button('Thêm dòng',self.add_row); self.add_button.setObjectName('glossary_add')
        self.add_button.setIcon(icon('plus',c['text'],18)); self.add_button.setIconSize(QSize(18,18)); self.add_button.setFixedWidth(140)
        toolbar.addWidget(self.add_button); self.body.addLayout(toolbar)
        self.table=QTableWidget(len(entries)+1,3); self.table.setObjectName('glossary_entries')
        self.table.horizontalHeader().setObjectName('glossary_columns')
        self.table.setHorizontalHeaderLabels(['Tiếng Trung','Tiếng Việt ưu tiên','Ghi chú'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setDefaultSectionSize(52); self.table.verticalHeader().setMinimumWidth(36)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setMinimumSize(0,180); self.table.setWordWrap(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.delegate=EntryDelegate(c,self.table); self.table.setItemDelegate(self.delegate)
        for i,item in enumerate(entries):
            for j,key in enumerate(('zh','vi','note')): self.table.setItem(i,j,QTableWidgetItem(item.get(key,'')))
        self.body.addWidget(self.table,1)
        footer=QHBoxLayout(); footer.setSpacing(12)
        self.hint=QWidget(); hint_row=QHBoxLayout(self.hint); hint_row.setContentsMargins(0,0,0,0); hint_row.setSpacing(8)
        info=label(''); info.setFixedSize(20,20); info.setPixmap(icon('info',c['muted'],20).pixmap(20,20)); hint_row.addWidget(info)
        hint_row.addWidget(label('Nhấp đúp vào ô để chỉnh sửa.','muted'))
        footer.addWidget(self.hint); footer.addStretch()
        self.delete_button=button('Xóa dòng chọn',self.delete_rows); self.delete_button.setObjectName('glossary_delete')
        self.delete_button.setIcon(icon('trash',c['muted'],18)); self.delete_button.setFixedWidth(190)
        self.save_button=button('Lưu bộ thuật ngữ',owner.save_glossary,True); self.save_button.setObjectName('glossary_save')
        self.save_button.setIcon(icon('save',c['on_primary'],20)); self.save_button.setIconSize(QSize(20,20)); self.save_button.setFixedWidth(200)
        footer.addWidget(self.delete_button); footer.addWidget(self.save_button); self.body.addLayout(footer)
        self.name.textChanged.connect(self.refresh_state); self.context.textChanged.connect(self.refresh_state)
        self.table.itemChanged.connect(self.refresh_state); self.table.itemSelectionChanged.connect(self.refresh_state)
        self.delegate.draftChanged.connect(self.refresh_state)
        self.set_compact(owner.height()<820)

    @staticmethod
    def caption(text):
        widget=label(text); widget.setProperty('glossary_caption',True); return widget

    def row_values(self):
        rows=[[self.table.item(i,j).text() if self.table.item(i,j) else '' for j in range(3)] for i in range(self.table.rowCount())]
        if self.delegate.pending:
            index,text=self.delegate.pending
            if index.isValid() and index.row()<len(rows): rows[index.row()][index.column()]=text
        return rows

    def current_state(self):
        return [self.name.text(),self.context.toPlainText(),[row for row in self.row_values() if any(row)]]

    def commit_editor(self):
        editor=self.delegate.editor
        if editor is not None:
            self.table.commitData(editor)
            self.table.closeEditor(editor,QAbstractItemDelegate.EndEditHint.NoHint)

    def refresh_state(self,*args):
        rows=self.row_values(); complete=sum(bool(row[0].strip() and row[1].strip()) for row in rows)
        incomplete=sum(bool(any(x.strip() for x in row)) and not bool(row[0].strip() and row[1].strip()) for row in rows)
        self.count.setText(f'{complete} thuật ngữ'); self.count.setToolTip(f'{complete} dòng đủ Trung/Việt; {incomplete} dòng chưa hoàn tất.')
        saved=bool(self.owner.glossary_id) and self.current_state()==self.owner.glossary_clean
        self.save_status.setText('Đã lưu' if saved else 'Chưa lưu')
        c=self.colors
        self.save_status.setStyleSheet(f"font-size:13px;background:{c['soft'] if saved else c['lavender']};color:{c['success'] if saved else c['text']};padding:6px 14px;border-radius:14px")
        self.delete_button.setEnabled(bool(self.table.selectedIndexes()))

    def add_row(self):
        self.commit_editor(); row=self.table.rowCount(); self.table.insertRow(row)
        self.table.setCurrentCell(row,0); self.table.scrollTo(self.table.model().index(row,0))
        self.table.setFocus(); self.refresh_state()

    def delete_rows(self):
        self.commit_editor()
        rows=sorted({index.row() for index in self.table.selectedIndexes()},reverse=True)
        for row in rows: self.table.removeRow(row)
        if not self.table.rowCount(): self.table.insertRow(0)
        self.table.clearSelection(); self.refresh_state()

    def available_width(self):
        margins=self.owner.workspace_layout.contentsMargins()
        return self.owner.width()-self.owner.rail.width()-self.owner.context.width()-margins.left()-margins.right()

    def set_compact(self,compact):
        margin=14 if compact else 20
        self.body.setContentsMargins(margin,margin,margin,margin); self.body.setSpacing(10 if compact else 18)
        self.context.setFixedHeight(76 if compact else 140); self.context_helper.setVisible(not compact)
        self.hint.setVisible(self.available_width()>=820)

    def resizeEvent(self,event):
        super().resizeEvent(event); self.hint.setVisible(self.available_width()>=820)
