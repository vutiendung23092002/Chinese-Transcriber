"""Native settings overview, matching the approved settings-redesign-v1 image."""
from datetime import datetime, timedelta, timezone
import math

from PySide6.QtCore import Qt, QSize, QPoint, QRectF
from PySide6.QtGui import QColor, QPainter, QFont, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QAbstractButton, QButtonGroup, QProgressBar, QSpinBox, QDialog,
    QDialogButtonBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLayout, QSizePolicy, QApplication)

from .widgets import label, button
from .model_selector import ModelReasoningSelector
from .theme import LIGHT, DARK, icon, asset
from .codex import APPROVED_MODELS, validate_selection
from .models import CATALOG

DOCS_URL='https://learn.chatgpt.com/docs/developer-commands?surface=cli'


def settings_styles(c):
    dark=c['bg']==DARK['bg']
    link='#D2B3F6' if dark else '#8152C7'
    up=asset('icons/chevron-up-'+('dark' if dark else 'light')+'.svg').as_posix()
    down=asset('icons/chevron-down-'+('dark' if dark else 'light')+'.svg').as_posix()
    return f'''
    QDialog#settings_dialog {{ background:{c['bg']}; color:{c['text']}; }}
    QWidget#settings_page, QDialog#settings_dialog {{ font-size:14px; }}
    QWidget#settings_page QLabel, QDialog#settings_dialog QLabel {{ font-size:16px; }}
    QWidget#settings_page QLabel[role="muted"], QDialog#settings_dialog QLabel[role="muted"] {{ font-size:14px; color:{c['muted']}; }}
    QWidget#settings_page QLabel[role="settings_title"] {{ font-size:22px; font-weight:600; }}
    QWidget#settings_page QLabel[role="settings_strong"] {{ font-size:16px; font-weight:600; }}
    QFrame[settings_card="true"] {{ background:{c['panel']}; border:1px solid {c['line']}; border-radius:18px; }}
    QLabel#settings_icon {{ background:{c['lavender']}; border-radius:10px; }}
    QFrame#settings_divider {{ background:{c['line']}; border:none; }}
    QWidget#settings_page QPushButton, QDialog#settings_dialog QPushButton {{ font-size:15px; border-radius:9px; min-height:20px; padding:8px 12px; }}
    QWidget#settings_page QPushButton[settings_link="true"] {{ color:{link}; border:none; background:transparent; padding:4px 0; min-height:20px; text-align:left; }}
    QWidget#settings_page QPushButton[settings_link="true"]:hover {{ color:{c['focus']}; }}
    QWidget#settings_page QPushButton[settings_row="true"] {{ text-align:left; border:none; border-radius:7px; background:transparent; padding:7px 0; min-height:22px; }}
    QWidget#settings_page QPushButton[settings_row="true"]:hover {{ background:{c['soft']}; }}
    QWidget#settings_page QComboBox, QWidget#settings_page QSpinBox {{ font-size:15px; min-height:24px; max-height:24px; padding:8px 8px 8px 12px; }}
    QWidget#settings_page QSpinBox {{ padding-right:24px; border-radius:9px; }}
    QWidget#settings_page QSpinBox::up-button {{ subcontrol-origin:border; subcontrol-position:top right; width:22px; border:none; background:transparent; }}
    QWidget#settings_page QSpinBox::down-button {{ subcontrol-origin:border; subcontrol-position:bottom right; width:22px; border:none; background:transparent; }}
    QWidget#settings_page QSpinBox::up-arrow {{ image:url("{up}"); width:11px; height:11px; }}
    QWidget#settings_page QSpinBox::down-arrow {{ image:url("{down}"); width:11px; height:11px; }}
    QDialog#settings_dialog QTableWidget {{ font-size:14px; }}
    QDialog#settings_dialog QHeaderView::section {{ font-size:13px; }}
    QProgressBar#settings_quota {{ min-height:12px; max-height:12px; border-radius:6px; background:{c['line']}; }}
    QProgressBar#settings_quota::chunk {{ border-radius:6px; background:{'#AA83D9' if dark else '#CDA5F2'}; }}
    QProgressBar#settings_quota[weekly="true"]::chunk {{ background:{'#D095AF' if dark else '#F3BFD1'}; }}
    '''


class ThemeTile(QAbstractButton):
    def __init__(self,mode,colors,parent=None):
        super().__init__(parent)
        self.mode=mode; self.colors=colors
        self.setCheckable(True); self.setMinimumHeight(132)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName('Giao diện '+('sáng' if mode=='light' else 'tối'))
        self.setObjectName('settings_theme_'+mode)

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c=self.colors; selected=self.isChecked()
        p.setPen(QColor('#BA8EEA' if selected else c['line']))
        p.setBrush(QColor(c['soft'] if selected else c['panel']))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(1,1,-1,-1),10,10)
        preview=LIGHT if self.mode=='light' else DARK
        width=min(self.width()-32,160); height=min(86,self.height()-54)
        r=QRectF((self.width()-width)/2,22,width,height)
        p.setPen(QColor(preview['line'])); p.setBrush(QColor(preview['bg']))
        p.drawRoundedRect(r,8,8)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(preview['panel']))
        p.drawRoundedRect(r.adjusted(6,6,-width+36,-6),4,4)
        p.setBrush(QColor(preview['rail']))
        p.drawRoundedRect(QRectF(r.x()+7,r.y()+10,7,height-20),3.5,3.5)
        p.setBrush(QColor(preview['lavender']))
        for i in range(3):
            p.drawRoundedRect(QRectF(r.x()+47,r.y()+12+i*20,width-59,12),4,4)
        if selected:
            p.setBrush(QColor('#BA8EEA')); p.drawEllipse(QPoint(int(r.right()),int(r.y()+4)),11,11)
            icon('check','#FFFFFF',14).paint(p,int(r.right()-7),int(r.y()-3),14,14)
        font=QFont(self.font()); font.setPixelSize(15); p.setFont(font); p.setPen(QColor(c['text']))
        p.drawText(self.rect().adjusted(0,self.height()-33,0,-7),Qt.AlignmentFlag.AlignCenter,'Sáng' if self.mode=='light' else 'Tối')
        if self.hasFocus():
            p.setPen(QColor(c['focus'])); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(self.rect()).adjusted(3,3,-3,-3),8,8)


class SettingsPage(QWidget):
    def __init__(self,owner):
        super().__init__()
        self.owner=owner; self.colors=owner.colors; self.cards={}; self.nav={}; self.quota_bars=[]
        self._wide=None; self.setObjectName('settings_page'); self.setStyleSheet(settings_styles(self.colors))
        self.grid=QGridLayout(self); self.grid.setContentsMargins(0,0,0,0); self.grid.setSpacing(20)
        self.grid.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.connection_card(); self.quota_card(); self.defaults_card()
        self.appearance_card(); self.asr_card(); self.data_card()
        self.reflow(owner.scroll.viewport().width()>=900)

    def new_card(self,key,height):
        panel=QFrame(); panel.setProperty('settings_card',True); panel.setObjectName('settings_'+key)
        panel.setMinimumHeight(height); panel.setMinimumWidth(0)
        body=QVBoxLayout(panel); body.setContentsMargins(20,18,20,18); body.setSpacing(12)
        self.cards[key]=panel
        return body

    def header(self,body,title,glyph,subtitle=None,badge=None):
        row=QHBoxLayout(); row.setSpacing(12)
        glyph_label=label(''); glyph_label.setObjectName('settings_icon'); glyph_label.setFixedSize(40,40)
        glyph_label.setAlignment(Qt.AlignmentFlag.AlignCenter); glyph_label.setPixmap(icon(glyph,self.colors['text'],23).pixmap(23,23))
        row.addWidget(glyph_label,0,Qt.AlignmentFlag.AlignTop)
        words=QVBoxLayout(); words.setSpacing(3)
        top=QHBoxLayout(); top.setSpacing(10); top.addWidget(label(title,'settings_title'))
        if badge: top.addWidget(badge,0,Qt.AlignmentFlag.AlignVCenter)
        top.addStretch(); words.addLayout(top)
        if subtitle: words.addWidget(label(subtitle,'muted',True))
        row.addLayout(words,1); body.addLayout(row)

    def divider(self,body):
        line=QFrame(); line.setObjectName('settings_divider'); line.setFixedHeight(1); body.addWidget(line)

    def link(self,text,callback):
        control=button(text,callback); control.setProperty('settings_link',True)
        return control

    def connection_card(self):
        b=self.new_card('connection',244); status=self.owner.codex_status
        known='authenticated' in status; logged=status.get('authenticated',False)
        badge=label(('●  Đã đăng nhập' if logged else 'Chưa đăng nhập') if known else 'Chưa kiểm tra')
        badge.setStyleSheet(f"font-size:12px;padding:5px 9px;border-radius:12px;background:{'#E5F4E9' if logged else self.colors['soft']};color:{'#26813C' if logged else self.colors['muted']}")
        self.header(b,'Kết nối Codex','terminal',badge=badge)
        info=QHBoxLayout(); info.setContentsMargins(52,0,0,0)
        details=QVBoxLayout(); details.setSpacing(5)
        details.addWidget(label('Tài khoản ChatGPT' if logged else 'Kết nối tài khoản ChatGPT','settings_strong'))
        version=status.get('version','').removeprefix('codex-cli ')
        details.addWidget(label('Phiên bản '+version if version else 'Chưa xác định phiên bản','muted'))
        info.addLayout(details,1); info.addWidget(button('Đăng nhập lại' if logged else 'Đăng nhập',self.owner.login_codex))
        b.addLayout(info); b.addStretch(); self.divider(b)
        for title,glyph,callback in [('Đường dẫn & chi tiết','info',self.show_connection_details),('Hướng dẫn đăng nhập / Tài liệu','book',self.show_help)]:
            row=button(title.replace('&','&&'),callback); row.setProperty('settings_row',True); row.setIcon(icon(glyph,self.colors['text'],20)); row.setIconSize(QSize(20,20))
            layout=QHBoxLayout(row); layout.setContentsMargins(0,0,4,0); layout.addStretch()
            arrow=label(''); arrow.setPixmap(icon('chevron',self.colors['muted'],14).pixmap(14,14)); arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents); layout.addWidget(arrow)
            b.addWidget(row)
        refresh=button('Kiểm tra kết nối',self.owner.check_codex)
        refresh.setObjectName('settings_check_connection'); refresh.setIcon(icon('refresh',self.colors['text'],16))
        b.addWidget(refresh)

    def quota_card(self):
        b=self.new_card('quota',244); self.header(b,'Hạn mức Codex','chart'); b.addStretch()
        limits=(self.owner.codex_status.get('limits') or {}).get('rateLimits') or {}
        rows=QGridLayout(); rows.setHorizontalSpacing(14); rows.setVerticalSpacing(10)
        rows.setColumnStretch(0,3); rows.setColumnStretch(1,2)
        found=False
        for key in ('primary','secondary'):
            entry=limits.get(key) or {}; value=entry.get('usedPercent')
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value): continue
            found=True; minutes=entry.get('windowDurationMins')
            title='5 giờ' if minutes==300 else 'Hàng tuần' if minutes==10080 else f'{minutes} phút' if minutes else 'Hạn mức'
            row=len(self.quota_bars)*3
            percent=label(f'{value:g}% đã dùng'); percent.setObjectName('settings_quota_percent_'+key)
            reset=label(self.reset_label(entry.get('resetsAt')),'muted'); reset.setObjectName('settings_quota_reset_'+key)
            for text in (percent,reset): text.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
            rows.addWidget(label(title,'settings_strong'),row,0); rows.addWidget(percent,row,1)
            bar=QProgressBar(); bar.setObjectName('settings_quota'); bar.setRange(0,1000); bar.setValue(round(max(0,min(100,value))*10)); bar.setTextVisible(False); bar.setProperty('weekly',key=='secondary'); self.quota_bars.append(bar)
            rows.addWidget(bar,row+1,0); rows.addWidget(reset,row+1,1)
            if row: rows.setRowMinimumHeight(row-1,14)
        if found: b.addLayout(rows,1); b.addStretch()
        if not found:
            missing=label('Chưa đọc được hạn mức. Kiểm tra kết nối để cập nhật số liệu.','muted',True); missing.setObjectName('settings_quota_missing'); b.addWidget(missing); b.addStretch()

    @staticmethod
    def reset_label(timestamp):
        if not timestamp: return 'Chưa có giờ đặt lại'
        zone=timezone(timedelta(hours=7))
        try: reset=datetime.fromtimestamp(timestamp,zone)
        except (TypeError,ValueError,OverflowError,OSError): return 'Chưa có giờ đặt lại'
        return 'Đặt lại '+reset.strftime('%H:%M hôm nay' if reset.date()==datetime.now(zone).date() else '%d/%m · %H:%M')

    def defaults_card(self):
        b=self.new_card('defaults',244); self.header(b,'Mô hình dịch mặc định','cube','Áp dụng cho các bản dịch mới.')
        self.model_selector=ModelReasoningSelector(self.owner.models,self.owner.store.setting('model'),self.owner.store.setting('effort'),self.colors)
        self.model_selector.setFixedWidth(260)
        b.addWidget(self.model_selector,0,Qt.AlignmentFlag.AlignHCenter)
        b.addStretch(); self.divider(b)
        bottom=QHBoxLayout(); bottom.setSpacing(12)
        count=len(self.owner.models); bottom.addWidget(label(f'{count} mô hình khả dụng' if count else 'Chưa có danh sách','muted'))
        bottom.addWidget(self.link('Xem danh sách',self.show_models)); bottom.addStretch()
        self.save_button=button('Lưu mặc định',self.save_defaults,True); self.save_button.setObjectName('settings_save'); bottom.addWidget(self.save_button); b.addLayout(bottom)

    def save_defaults(self):
        try:
            model=self.model_selector.model_id; effort=self.model_selector.effort
            validate_selection(self.owner.models,model,effort)
            self.owner.store.set_setting('model',model); self.owner.store.set_setting('effort',effort)
            self.owner.statusBar().showMessage('Đã lưu mô hình và mức suy luận mặc định.')
        except Exception as error: self.owner.error(error)

    def appearance_card(self):
        b=self.new_card('appearance',244); self.header(b,'Giao diện','monitor','Áp dụng cho toàn bộ ứng dụng.')
        self.theme_group=QButtonGroup(self); row=QHBoxLayout(); row.setSpacing(18)
        for index,mode in enumerate(('light','dark')):
            tile=ThemeTile(mode,self.colors); tile.setChecked((self.colors['bg']==DARK['bg'])==(mode=='dark')); self.theme_group.addButton(tile,index); row.addWidget(tile)
        self.theme_group.idClicked.connect(self.owner.change_theme); b.addLayout(row,1)

    def asr_card(self):
        b=self.new_card('asr',212); self.header(b,'Nhận dạng giọng nói','mic','Chạy cục bộ bằng CPU.')
        states=QHBoxLayout(); states.setSpacing(12)
        for key,title in [('sensevoice','SenseVoice'),('paraformer','Paraformer'),('vad','Silero VAD')]:
            ready=self.owner.model_manager.ready(key); item=label(('✓  ' if ready else '↓  ')+title); item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setStyleSheet(f"font-size:13px;padding:7px 8px;border-radius:9px;background:{'#EAF6EE' if ready and self.colors['bg']==LIGHT['bg'] else self.colors['soft']};color:{'#26813C' if ready and self.colors['bg']==LIGHT['bg'] else self.colors['text']}")
            item.setToolTip(CATALOG[key]['name']+(' · Đã có' if ready else ' · Chưa tải')); states.addWidget(item,1)
        b.addSpacing(8); b.addLayout(states); b.addStretch(); self.divider(b)
        bottom=QHBoxLayout(); bottom.setSpacing(12); bottom.addWidget(label('Luồng CPU'))
        self.threads=QSpinBox(); self.threads.setObjectName('settings_cpu'); self.threads.setRange(1,4); self.threads.setValue(self.owner.store.setting('asr_threads',4)); self.threads.setFixedWidth(78)
        self.threads.valueChanged.connect(lambda value:self.owner.store.set_setting('asr_threads',value)); bottom.addWidget(self.threads); bottom.addStretch(); bottom.addWidget(self.link('Quản lý mô hình',self.show_asr_models)); b.addLayout(bottom)

    def data_card(self):
        b=self.new_card('data',212); self.header(b,'Dữ liệu & sao lưu','database','Âm thanh và bản dịch được lưu trên máy.')
        actions=QHBoxLayout(); actions.setSpacing(12)
        for text,glyph,callback,name in [('Sao lưu ngay','backup',self.owner.backup,'settings_backup'),('Mở thư mục','folder',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.owner.store.root))),'settings_open_folder')]:
            action=button(text,callback); action.setObjectName(name); action.setIcon(icon(glyph,self.colors['text'],19)); action.setIconSize(QSize(19,19)); actions.addWidget(action,1)
            if name=='settings_backup': action.setToolTip('Sao lưu cơ sở dữ liệu; âm thanh được giữ trong thư viện.')
        b.addSpacing(12); b.addLayout(actions); b.addStretch(); self.divider(b)
        if self.owner.recovered: b.addWidget(self.link(f'{len(self.owner.recovered)} tác vụ cần khôi phục',self.show_recovery))
        else: b.addWidget(label('✓  Không có tác vụ gián đoạn.','muted'))

    def add_navigation(self,layout):
        layout.addSpacing(18)
        for key,title,glyph in [('connection','Kết nối Codex','terminal'),('defaults','Mô hình dịch','cube'),('asr','Nhận dạng giọng nói','mic'),('appearance','Giao diện','monitor'),('data','Dữ liệu & sao lưu','database')]:
            item=button(title.replace('&','&&'),lambda checked=False,k=key:self.activate_section(k)); item.setCheckable(True)
            item.setIcon(icon(glyph,self.colors['text'],20)); item.setIconSize(QSize(20,20)); item.setCursor(Qt.CursorShape.PointingHandCursor)
            item.setStyleSheet(f"QPushButton{{text-align:left;font-size:16px;border:0;border-radius:11px;padding:12px 9px;min-height:22px;background:transparent}} QPushButton:hover{{background:{self.colors['soft']};}} QPushButton:checked{{background:{self.colors['lavender']};font-weight:600}}")
            self.nav[key]=item; layout.addWidget(item)
        self.activate_section(getattr(self.owner,'_settings_section','connection'),scroll=False)

    def activate_section(self,key,scroll=True):
        self.owner._settings_section=key
        for name,item in self.nav.items(): item.setChecked(name==key)
        if scroll: self.owner.scroll.verticalScrollBar().setValue(self.cards[key].mapTo(self.owner.content,QPoint(0,0)).y())

    def connection_footer(self):
        wrapper=QWidget(); outer=QVBoxLayout(wrapper); outer.setContentsMargins(0,8,0,0); outer.setSpacing(14)
        line=QFrame(); line.setFixedHeight(1); line.setStyleSheet('background:'+self.colors['line']); outer.addWidget(line)
        row=QHBoxLayout(); row.setSpacing(6)
        logged=self.owner.codex_status.get('authenticated',False)
        dot=label('●'); dot.setStyleSheet('color:'+('#249A3D' if logged else self.colors['muted'])+';font-size:12px'); row.addWidget(dot)
        text=label('Codex đã kết nối' if logged else 'Codex chưa kết nối'); text.setStyleSheet('font-size:12px'); row.addWidget(text,1)
        help_button=button('Hướng dẫn',self.show_help); help_button.setStyleSheet('border:0;background:transparent;padding:0;font-size:12px;color:'+('#D2B3F6' if self.colors['bg']==DARK['bg'] else '#8152C7')); row.addWidget(help_button)
        outer.addLayout(row); return wrapper

    def reflow(self,wide):
        if self._wide==wide: return
        self._wide=wide
        while self.grid.count(): self.grid.takeAt(0)
        for row in range(6): self.grid.setRowStretch(row,0); self.grid.setRowMinimumHeight(row,0)
        keys=('connection','quota','defaults','appearance','asr','data')
        for i,key in enumerate(keys): self.grid.addWidget(self.cards[key],i//2 if wide else i,i%2 if wide else 0)
        self.grid.setColumnStretch(0,11 if wide else 1); self.grid.setColumnStretch(1,10 if wide else 0)
        if wide:
            for i,stretch in enumerate((10,10,9)): self.grid.setRowStretch(i,stretch)
        self.grid.invalidate(); self.updateGeometry()

    def resizeEvent(self,event):
        super().resizeEvent(event); self.reflow(self.width()>=900)

    def dialog(self,title):
        dialog=QDialog(self.owner); dialog.setObjectName('settings_dialog'); dialog.setWindowTitle(title); dialog.resize(650,350); dialog.setStyleSheet(settings_styles(self.colors))
        body=QVBoxLayout(dialog); body.setContentsMargins(24,22,24,22); body.setSpacing(14)
        heading=label(title,'heading'); body.addWidget(heading)
        return dialog,body

    @staticmethod
    def finish_dialog(dialog,body):
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close); close.button(QDialogButtonBox.StandardButton.Close).setText('Đóng')
        close.rejected.connect(dialog.reject); body.addWidget(close); dialog.exec()

    def show_connection_details(self):
        dialog,body=self.dialog('Đường dẫn & chi tiết Codex')
        body.addWidget(label('Đường dẫn codex.exe','muted'))
        path=QLineEdit(self.owner.store.setting('codex_path',self.owner.codex_status.get('path',''))); path.setReadOnly(True); body.addWidget(path)
        def choose():
            self.owner.choose_codex(); path.setText(self.owner.store.setting('codex_path',''))
        body.addWidget(button('Chọn codex.exe',choose)); body.addWidget(label(self.owner.codex_status.get('version','Chưa xác định phiên bản'),'muted',True))
        self.finish_dialog(dialog,body)

    def show_help(self):
        dialog,body=self.dialog('Hướng dẫn kết nối Codex')
        body.addWidget(label('1. Cài Codex CLI hoặc chọn codex.exe có sẵn.\n2. Chạy codex login và hoàn tất đăng nhập trong trình duyệt.\n3. Chọn Kiểm tra kết nối trong ứng dụng.',wrap=True))
        command=QLineEdit('codex login'); command.setReadOnly(True); body.addWidget(command)
        actions=QHBoxLayout(); actions.addWidget(button('Sao chép hướng dẫn',lambda:QApplication.clipboard().setText('codex login\ncodex login status')))
        actions.addWidget(button('Tài liệu chính thức',lambda:QDesktopServices.openUrl(QUrl(DOCS_URL)))); body.addLayout(actions)
        def login(): dialog.accept(); self.owner.login_codex()
        body.addWidget(button('Đăng nhập',login,True)); self.finish_dialog(dialog,body)

    def show_models(self):
        dialog,body=self.dialog('Mô hình được Codex xác nhận'); dialog.resize(850,570)
        def normalized(value): return ''.join(x for x in value.lower() if x.isalnum())
        known={normalized(x['displayName']):x for x in self.owner.models}
        names=list(APPROVED_MODELS)
        names.extend(item['displayName'] for item in self.owner.models if normalized(item['displayName']) not in {normalized(name) for name in APPROVED_MODELS})
        table=QTableWidget(len(names),3); table.setHorizontalHeaderLabels(['Mô hình','Trạng thái','Mức suy luận'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); table.verticalHeader().hide(); table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for row,name in enumerate(names):
            item=known.get(normalized(name)); values=[name,'Khả dụng' if item else 'Chưa xác minh / không khả dụng',', '.join(x['reasoningEffort'] for x in item.get('supportedReasoningEfforts',[])) if item else '—']
            for col,value in enumerate(values): table.setItem(row,col,QTableWidgetItem(value))
            table.setRowHeight(row,46)
        body.addWidget(table); body.addWidget(label('Không tự thay model hoặc mức suy luận khi lựa chọn không được hỗ trợ.','muted',True)); self.finish_dialog(dialog,body)

    def show_asr_models(self):
        dialog,body=self.dialog('Quản lý mô hình nhận dạng')
        body.addWidget(label('Thư mục: '+str(self.owner.model_manager.root),'muted',True))
        def install(key): dialog.accept(); self.owner.install_model(key)
        for key in ('sensevoice','paraformer','vad'):
            row=QHBoxLayout(); row.addWidget(label(CATALOG[key]['name']),1); ready=self.owner.model_manager.ready(key)
            action=button('Đã có' if ready else 'Tải mô hình',lambda checked=False,k=key:install(k)); action.setEnabled(not ready); row.addWidget(action); body.addLayout(row)
        def choose(): dialog.accept(); self.owner.choose_model_dir()
        body.addWidget(button('Chọn thư mục mô hình',choose)); self.finish_dialog(dialog,body)

    def show_recovery(self):
        dialog,body=self.dialog('Khôi phục tác vụ gián đoạn')
        for job in self.owner.recovered:
            def recover(checked=False,item=job): dialog.accept(); self.owner.recover_job(item)
            body.addWidget(button({'recording':'Ghi âm','transcribe':'Chép lời','translate':'Dịch','transcribe_translate':'Chép lời và dịch'}.get(job['kind'],job['kind'])+' · Phục hồi',recover))
        self.finish_dialog(dialog,body)
