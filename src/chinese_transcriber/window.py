from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QScrollArea, QGridLayout, QApplication)
from .theme import LIGHT, DARK, stylesheet, icon, asset
from .widgets import PAGES, Rail, ComboBox, label, button, box, card, clear

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.colors = dict(LIGHT)
        self.page = 'dashboard'
        self.setWindowTitle('Chinese Transcriber')
        self.setWindowIcon(__import__('PySide6.QtGui',fromlist=['QIcon']).QIcon(str(asset('logo-concepts/03-v2-voice-rhythm.svg'))))
        self.resize(1440,900)
        self.setMinimumSize(1024,700)
        screen=QApplication.primaryScreen()
        if screen and screen.availableGeometry().width()>=1024:
            available=screen.availableGeometry()
            self.resize(min(1440,available.width()-32),max(700,min(900,available.height()-56)))
        root = QWidget(); layout = QHBoxLayout(root)
        layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.setCentralWidget(root)
        self.rail = Rail(self.colors)
        self.rail.selected.connect(self.navigate)
        layout.addWidget(self.rail)
        self.context = QWidget(); self.context.setObjectName('context'); self.context.setFixedWidth(260)
        self.context_layout = QVBoxLayout(self.context)
        self.context_layout.setContentsMargins(17,22,18,16); self.context_layout.setSpacing(12)
        layout.addWidget(self.context)
        self.workspace = QWidget(); self.workspace.setObjectName('workspace')
        self.workspace_layout = QVBoxLayout(self.workspace)
        self.workspace_layout.setContentsMargins(26,24,26,20); self.workspace_layout.setSpacing(18)
        self.header = QHBoxLayout()
        self.heading_block=QWidget(); heading_layout=QVBoxLayout(self.heading_block)
        heading_layout.setContentsMargins(0,0,0,0); heading_layout.setSpacing(5)
        self.title = label('Không gian học tập','title'); heading_layout.addWidget(self.title)
        self.subtitle=label('','muted'); self.subtitle.hide(); heading_layout.addWidget(self.subtitle)
        self.header.addWidget(self.heading_block,1)
        self.workspace_layout.addLayout(self.header)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.content = QWidget(); self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0,0,0,0); self.content_layout.setSpacing(16)
        self.scroll.setWidget(self.content); self.workspace_layout.addWidget(self.scroll,1)
        layout.addWidget(self.workspace,1)
        self.statusBar().showMessage('Sẵn sàng')
        self.setStyleSheet(stylesheet(self.colors))
        self.navigate('dashboard')

    def navigate(self, page):
        self.page = page
        self.rail.set_page(page)
        clear(self.context_layout); clear(self.content_layout)
        self.title.setText(dict((key,title) for key,_,title in PAGES)[page])
        self.context_layout.addWidget(label({'dashboard':'Bạn muốn học gì?','file':'Dịch từ âm thanh',
            'live':'Phiên học trực tiếp','library':'Tài liệu của bạn','prompts':'Ngữ cảnh học tập',
            'settings':'Tùy chỉnh','trash':'Thùng rác'}[page], 'heading'))
        self.context_layout.addWidget(label('Không gian học tập Trung – Việt','muted',True))
        if page == 'dashboard':
            self.dashboard()
        elif page == 'settings':
            panel, body = card('Giao diện')
            choices = ComboBox(); choices.addItems(['Sáng','Tối'])
            choices.setCurrentIndex(1 if self.colors['bg']==DARK['bg'] else 0)
            choices.currentIndexChanged.connect(self.change_theme)
            body.addWidget(choices)
            self.content_layout.addWidget(panel)
        else:
            panel, body = card(self.title.text())
            body.addWidget(label('Chưa có dữ liệu. Nhập âm thanh hoặc tạo phiên ghi âm để bắt đầu.','muted',True))
            self.content_layout.addWidget(panel)
        self.context_layout.addStretch()
        self.context_layout.addWidget(button('Codex CLI · Hướng dẫn đăng nhập',lambda:self.navigate('settings')))
        self.content_layout.addStretch()
        self.scroll.verticalScrollBar().setValue(0)

    def dashboard(self):
        tasks = QGridLayout()
        for i,(page,glyph,text) in enumerate([('file','file','Dịch file'),('live','mic','Ghi trực tiếp'),('library','library','Thư viện'),('prompts','book','Thuật ngữ'),('settings','settings','Cài đặt'),('trash','trash','Thùng rác')]):
            tile = button(text,lambda checked=False,p=page:self.navigate(p))
            tile.setIcon(icon(glyph,self.colors['primary'])); tile.setMinimumHeight(65)
            tasks.addWidget(tile,i//2,i%2)
        self.context_layout.addLayout(tasks)
        self.content_layout.addWidget(label('Hôm nay, bạn muốn học gì?','heading'))
        actions = QHBoxLayout()
        for page,glyph,text,color in [('file','file','Dịch file ghi âm','pink'),('live','mic','Ghi âm trực tiếp','lavender'),('prompts','book','Chuẩn bị thuật ngữ','yellow')]:
            tile = button(text,lambda checked=False,p=page:self.navigate(p))
            tile.setMinimumHeight(145)
            tile.setIcon(icon(glyph,self.colors['text']))
            tile.setStyleSheet(f'background:{self.colors[color]};border:0;border-radius:20px;font-size:15px;font-weight:600')
            actions.addWidget(tile)
        self.content_layout.addLayout(actions)
        stats = QHBoxLayout()
        for title,value in [('File âm thanh','0'),('Bản dịch đã lưu','0'),('Lần dịch gần nhất','—'),('Mô hình mặc định','Chưa chọn')]:
            panel,body=card(); body.addWidget(label(title,'muted')); body.addWidget(label(value,'title')); stats.addWidget(panel)
        self.content_layout.addLayout(stats)
        panel,body=card('Tiếp tục bài học')
        body.addWidget(label('Thư viện của bạn chưa có âm thanh.','muted'))
        body.addWidget(button('Tải file ghi âm',lambda:self.navigate('file'),True))
        self.content_layout.addWidget(panel)

    def change_theme(self,index):
        self.colors = dict(DARK if index else LIGHT)
        self.setStyleSheet(stylesheet(self.colors)); self.rail.apply_colors(self.colors)
        self.navigate(self.page)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        # Columns change only with window size, never with the selected page.
        if hasattr(self,'context'):
            self.context.setFixedWidth(238 if self.width()<1280 else 260)
            self.rail.setFixedWidth(74 if self.width()<1280 else 82)
