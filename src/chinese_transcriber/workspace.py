from __future__ import annotations
import json
import os
from pathlib import Path
import threading
from PySide6.QtCore import Qt, QThreadPool, QTimer, QUrl, QSize, QObject, Signal
from PySide6.QtGui import QDesktopServices, QStandardItemModel, QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QComboBox,
    QPlainTextEdit,QLineEdit,QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem,
    QHeaderView,QAbstractItemView,QListWidget,QListWidgetItem,QDialog,QDialogButtonBox,
    QCheckBox,QInputDialog,QSlider,QSpinBox,QProgressBar,QApplication,QToolButton,QSplitter)
from .window import MainWindow
from .widgets import PAGES,label,button,box,card,clear
from .theme import LIGHT,DARK,stylesheet,icon,bubble_icon
from .storage import Store
from .audio import audio_info,timestamp,export_txt
from .workers import Task
from .models import ModelManager, CATALOG
from .asr import transcribe_job
from .recording import LiveSession, materialize_recording
from .codex import APPROVED_MODELS, capabilities,find_codex,validate_selection,translate_version

class LiveSignals(QObject):
    event=Signal(object)

STATUS={'complete':'Hoàn tất','running':'Đang xử lý','queued':'Chờ xử lý','failed':'Lỗi','interrupted':'Gián đoạn','partial':'Chưa đầy đủ'}

def state_name(value): return STATUS.get(value,value)

class WorkspaceWindow(MainWindow):
    def __init__(self,store=None):
        self._ready=False
        self.store=store or Store()
        self.audio_id=None; self.transcript_id=None; self.version_id=None
        self.glossary_id=None; self.tasks=set(); self.cancel_event=threading.Event()
        self.glossary_clean=None
        self.models=[]; self.codex_status={}; self.is_busy=False; self.recording=None
        import sys
        bundled=Path(sys.executable).parent/'models' if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]/'models'
        self.model_manager=ModelManager(self.store.setting('model_dir',str(bundled if bundled.is_dir() else self.store.root/'models')))
        self.live_signals=LiveSignals(); self.live_signals.event.connect(self.live_event)
        self.live_segments=[]; self.live_interim=''; self.record_timer=None
        self.pool=QThreadPool(); self.pool.setMaxThreadCount(3)
        super().__init__()
        self.colors=dict(DARK if self.store.setting('theme','light')=='dark' else LIGHT)
        self.setStyleSheet(stylesheet(self.colors)); self.rail.apply_colors(self.colors)
        self.player=QMediaPlayer(self); self.audio_output=QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self.playback_position)
        self.player.errorOccurred.connect(lambda *args:self.statusBar().showMessage(self.player.errorString()))
        self.activity=label('','muted'); self.statusBar().addPermanentWidget(self.activity)
        self.cancel_button=button('Dừng tác vụ',self.cancel_work)
        self.cancel_button.setStyleSheet('padding:2px 8px;min-height:14px;font-size:11px'); self.cancel_button.hide()
        self.statusBar().addPermanentWidget(self.cancel_button)
        self.setAcceptDrops(True)
        self._ready=True
        self.recovered=self.store.recover_jobs()
        self.navigate('dashboard')
        if self.recovered: self.statusBar().showMessage(f'Có {len(self.recovered)} tác vụ gián đoạn. Mở Cài đặt để khôi phục.')
        if not os.environ.get('CHINESE_TRANSCRIBER_NO_PROBE'): QTimer.singleShot(300,self.check_codex)

    def error(self,message):
        QMessageBox.warning(self,'Chinese Transcriber',str(message))

    def submit(self,func,done=None,progress=None,busy=True,error_handler=None):
        if busy and self.is_busy:
            self.error('Một tác vụ đang chạy. Bạn vẫn có thể xem thư viện; hãy chờ hoặc dừng tác vụ trước.'); return
        task=Task(func); self.tasks.add(task)
        if busy:
            self.is_busy=True; self.cancel_button.show(); self.activity.setText('Đang xử lý…')
        task.signals.error.connect(error_handler or self.error)
        if done: task.signals.result.connect(done)
        if progress: task.signals.progress.connect(progress)
        def finish():
            self.tasks.discard(task)
            if busy: self.is_busy=False
            if busy:
                self.cancel_button.hide()
                if not self.recording: self.activity.setText('')
        task.signals.finished.connect(finish)
        self.pool.start(task)

    def navigate(self,page):
        if not self._ready: return super().navigate(page)
        if not self.confirm_glossary_changes():
            self.rail.set_page(self.page); return
        self.capture_options()
        self.page=page; self.rail.set_page(page)
        clear(self.context_layout); clear(self.content_layout)
        while self.header.count()>1:
            item=self.header.takeAt(1)
            if item.widget(): item.widget().deleteLater()
        self.title.setText(dict((key,title) for key,_,title in PAGES)[page])
        titles={'dashboard':'Bạn muốn học gì?','file':'Dịch từ âm thanh','live':'Phiên học trực tiếp',
            'library':'Tài liệu của bạn','prompts':'Ngữ cảnh học tập','settings':'Tùy chỉnh','trash':'Thùng rác'}
        self.context_layout.addWidget(label(titles[page],'heading'))
        self.context_layout.addWidget(label('Không gian học tập Trung – Việt','muted',True))
        self.context_layout.setSpacing(8)
        self.option_widgets=None
        getattr(self,'show_'+page)()
        self.context_layout.addStretch()
        self.context_layout.addWidget(button('Codex CLI · '+self.codex_status.get('login_label','Kết nối'),lambda:self.navigate('settings')))
        self.content_layout.addStretch()
        self.scroll.verticalScrollBar().setValue(0)

    def capture_options(self):
        widgets=getattr(self,'option_widgets',None)
        if widgets:
            context,glossary,model,effort=widgets
            try:
                self.store.set_setting('context',context.toPlainText())
                self.store.set_setting('glossary_id',glossary.currentData())
                if model.currentData(): self.store.set_setting('model',model.currentData())
                if effort.currentData(): self.store.set_setting('effort',effort.currentData())
            except RuntimeError:
                pass

    def context_action(self,text,page):
        self.context_layout.addWidget(button(text,lambda:self.navigate(page)))

    def show_dashboard(self):
        tasks=QGridLayout()
        for i,(key,glyph,title) in enumerate([('file','file','Dịch file'),('live','mic','Ghi trực tiếp'),('library','library','Thư viện'),('prompts','book','Thuật ngữ'),('settings','settings','Cài đặt'),('trash','trash','Thùng rác')]):
            tile=QToolButton(); tile.setText(title); tile.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            tile.setIcon(bubble_icon(glyph,self.colors[['pink','lavender','cyan','yellow','soft','soft'][i]],self.colors['primary']))
            tile.setIconSize(QSize(34,34)); tile.clicked.connect(lambda checked=False,p=key:self.navigate(p))
            tile.setStyleSheet('QToolButton{min-height:74px;min-width:78px;border-radius:16px;padding:10px 4px;font-size:10px}')
            tasks.addWidget(tile,i//2,i%2)
        self.context_layout.addLayout(tasks)
        self.content_layout.addWidget(label('Hôm nay, bạn muốn học gì?','heading'))
        actions=QHBoxLayout()
        for key,glyph,title,color in [('file','file','Dịch file ghi âm','pink'),('live','mic','Ghi âm trực tiếp','lavender'),('prompts','book','Chuẩn bị thuật ngữ','yellow')]:
            tile=button('',lambda checked=False,p=key:self.navigate(p))
            tile.setStyleSheet(f"QPushButton{{background:{self.colors[color]};border:0;border-radius:20px;min-height:145px;padding:0}}")
            inner=QVBoxLayout(tile); inner.setContentsMargins(18,18,18,18); inner.setSpacing(9)
            glyph_label=label(''); glyph_label.setPixmap(icon(glyph,self.colors['text'],26).pixmap(26,26)); inner.addWidget(glyph_label)
            heading=label(title); heading.setStyleSheet('font-size:15px;font-weight:600'); inner.addWidget(heading)
            subtitle=label({'file':'Từ âm thanh tiếng Trung đến bản dịch tiếng Việt.','live':'Theo dõi lời giảng qua từng câu đã chốt.','prompts':'Giữ đúng từ chuyên ngành trong mỗi bản dịch.'}[key],'muted',True)
            inner.addWidget(subtitle); inner.addStretch()
            for child in (glyph_label,heading,subtitle): child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            actions.addWidget(tile)
        self.content_layout.addLayout(actions)
        audio=self.store.list_audio()
        versions=self.store.rows('SELECT v.* FROM versions v JOIN audio a ON a.id=v.audio_id WHERE v.deleted IS NULL AND a.deleted IS NULL ORDER BY v.created DESC')
        stats=QHBoxLayout()
        for title,value in [('File âm thanh',str(len(audio))),('Bản dịch đã lưu',str(len(versions))),('Lần dịch gần nhất',versions[0]['created'][11:16] if versions else '—'),('Mô hình mặc định',self.store.setting('model','Chưa chọn'))]:
            panel,body=card(); body.addWidget(label(title,'muted')); body.addWidget(label(value,'heading' if title=='Mô hình mặc định' else 'value',True)); stats.addWidget(panel)
        self.content_layout.addLayout(stats)
        panel,body=card('Tiếp tục bài học')
        if not audio: body.addWidget(label('Thư viện chưa có âm thanh. Tải file hoặc ghi âm để bắt đầu.','muted',True))
        for row in audio[:4]:
            body.addWidget(button(f"{row['title']} · {timestamp(row['duration'])} · {row['version_count']} bản dịch",lambda checked=False,a=row['id']:self.open_audio(a)))
        self.content_layout.addWidget(panel)

    def choose_audio(self):
        if self.is_busy or self.recording:
            self.error('Hãy kết thúc tác vụ hiện tại trước khi nhập nguồn mới.'); return
        filename,_=QFileDialog.getOpenFileName(self,'Chọn âm thanh','','Âm thanh (*.wav *.mp3 *.m4a *.flac *.ogg *.aac *.wma *.opus);;Tất cả file (*)')
        if filename: self.import_audio(filename)

    def import_audio(self,filename):
        self.statusBar().showMessage('Đang kiểm tra và nhập âm thanh…')
        def work(progress):
            duration=audio_info(filename)
            return self.store.import_audio(filename,duration)
        def done(result):
            row,created=result
            if row['deleted']:
                self.error('Âm thanh này đã nằm trong Thùng rác. Khôi phục để dùng lại, không cần nhập bản sao.'); self.navigate('trash'); return
            self.open_audio(row['id'])
            self.statusBar().showMessage('Đã nhập âm thanh.' if created else 'File đã có trong thư viện. Đang dùng lại âm thanh gốc.')
        self.submit(work,done)

    def open_audio(self,audio_id,version_id=None):
        self.audio_id=audio_id; self.version_id=version_id
        if version_id:
            row=self.store.one('SELECT * FROM versions WHERE id=?',(version_id,)); self.transcript_id=row['transcript_id']
        else:
            versions=self.store.versions(audio_id)
            if versions:
                self.version_id=versions[0]['id']; self.transcript_id=versions[0]['transcript_id']
            else:
                transcript=self.store.latest_transcript(audio_id,True) or self.store.latest_transcript(audio_id,False)
                self.transcript_id=transcript['id'] if transcript else None
        self.player.setSource(QUrl.fromLocalFile(str(self.store.audio_path(audio_id))))
        self.navigate('file')

    def field(self,layout,title,widget):
        layout.addWidget(label(title,'muted')); layout.addWidget(widget)

    def options(self):
        context=QPlainTextEdit(self.store.setting('context','')); context.setFixedHeight(58); context.setAcceptDrops(False)
        glossary=QComboBox(); glossary.addItem('Không áp dụng',None)
        for row in self.store.rows('SELECT * FROM glossaries ORDER BY name'):
            glossary.addItem(row['name'],row['id'])
        index=glossary.findData(self.store.setting('glossary_id')); glossary.setCurrentIndex(max(0,index))
        model=QComboBox(); model.setObjectName('model_select')
        effort=QComboBox(); effort.setObjectName('effort_select')
        available=self.models
        if available:
            for item in available:
                model.addItem(item['displayName'],item['model'])
            def normalized(text): return ''.join(c for c in text.lower() if c.isalnum())
            returned={normalized(x['displayName']) for x in available}
            for requested in APPROVED_MODELS:
                if normalized(requested) not in returned:
                    model.addItem(requested+' · Không khả dụng',None)
                    model.model().item(model.count()-1).setEnabled(False)
        else: model.addItem('Kiểm tra Codex để đọc model',None)
        previous_model=self.store.setting('model'); index=model.findData(previous_model)
        if previous_model and index<0:
            model.addItem(previous_model+' · Không khả dụng',previous_model); index=model.count()-1; model.model().item(index).setEnabled(False)
        model.setCurrentIndex(max(0,index))
        def efforts():
            effort.clear()
            item=next((x for x in available if x['model']==model.currentData()),None)
            if item:
                for option in item.get('supportedReasoningEfforts',[]):
                    value=option['reasoningEffort']; effort.addItem(value,value)
                chosen=self.store.setting('effort',item.get('defaultReasoningEffort')) if model.currentData()==self.store.setting('model') else item.get('defaultReasoningEffort')
                choice=effort.findData(chosen)
                if chosen and choice<0:
                    effort.addItem(chosen+' · Không khả dụng',chosen); choice=effort.count()-1; effort.model().item(choice).setEnabled(False)
                effort.setCurrentIndex(max(0,choice))
            else: effort.addItem('Chưa xác minh',None)
        model.currentIndexChanged.connect(efforts); efforts()
        self.field(self.context_layout,'Bối cảnh bài giảng',context)
        self.field(self.context_layout,'Bộ thuật ngữ',glossary)
        self.field(self.context_layout,'Mô hình dịch',model)
        self.field(self.context_layout,'Mức suy luận',effort)
        self.option_widgets=(context,glossary,model,effort)

    def show_file(self):
        self.context_layout.addWidget(button('↑  Kéo thả hoặc chọn âm thanh',self.choose_audio))
        source=QComboBox(); source.addItem('Chọn từ thư viện',None)
        for row in self.store.list_audio(): source.addItem(row['filename'],row['id'])
        source.setCurrentIndex(max(0,source.findData(self.audio_id)))
        source.activated.connect(lambda _:self.open_audio(source.currentData()) if source.currentData() else None)
        self.context_layout.addWidget(source)
        self.options()
        self.context_layout.addWidget(button('1. Chép lời tiếng Trung',self.transcribe))
        self.context_layout.addWidget(button('2. Tạo bản dịch mới',self.translate,True))
        if self.is_busy: self.context_layout.addWidget(button('Dừng tác vụ',self.cancel_work))
        self.header.addWidget(button('Trung TXT',lambda:self.export('zh')))
        self.header.addWidget(button('Việt TXT',lambda:self.export('vi')))
        audio=self.store.one('SELECT * FROM audio WHERE id=?',(self.audio_id,)) if self.audio_id else None
        panel,body=card(audio['title'] if audio else 'Chọn âm thanh để bắt đầu')
        if audio:
            body.addWidget(label(f"{audio['filename']} · {timestamp(audio['duration'])} · 1 âm thanh gốc",'muted',True))
            versions=QComboBox(); versions.addItem('Bản chép lời',None)
            for v in self.store.versions(self.audio_id): versions.addItem(f"v{v['number']} · {v['model']} · {state_name(v['status'])}",v['id'])
            versions.setCurrentIndex(max(0,versions.findData(self.version_id)))
            versions.activated.connect(lambda _:self.open_audio(self.audio_id,versions.currentData()))
            body.addWidget(versions)
        if self.transcript_id:
            transcript=self.store.one('SELECT status,engine FROM transcripts WHERE id=?',(self.transcript_id,))
            if transcript: body.addWidget(label(f"Chép lời: {state_name(transcript['status'])} · {transcript['engine']} · Mốc giờ theo ranh giới lời nói",'muted',True))
        self.notes_toggle=QCheckBox('Hiện ghi chú thuật ngữ'); self.notes_toggle.setChecked(self.store.setting('show_notes',False))
        self.notes_toggle.toggled.connect(self.toggle_notes); body.addWidget(self.notes_toggle)
        self.timeline=QTableWidget(0,3); self.timeline.setObjectName('bilingual_timeline')
        self.timeline.setHorizontalHeaderLabels(['Mốc giờ','ZH · TIẾNG TRUNG','VI · TIẾNG VIỆT'])
        self.timeline.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.timeline.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.timeline.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        self.timeline.verticalHeader().hide(); self.timeline.setWordWrap(True)
        self.timeline.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.timeline.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.timeline.setMinimumHeight(360)
        self.timeline.cellDoubleClicked.connect(self.edit_segment)
        self.timeline.cellClicked.connect(self.seek_segment)
        body.addWidget(self.timeline)
        player_row=QHBoxLayout(); player_row.addWidget(button('▶ / Ⅱ',self.toggle_play))
        self.play_label=label('00:00','muted'); player_row.addWidget(self.play_label)
        self.seek_slider=QSlider(Qt.Orientation.Horizontal); self.seek_slider.setRange(0,max(1,int((audio or {}).get('duration',0)*1000)))
        self.seek_slider.sliderMoved.connect(self.player.setPosition); player_row.addWidget(self.seek_slider,1)
        speed=QComboBox(); speed.addItems(['0.75×','1×','1.25×','1.5×']); speed.setCurrentIndex(1)
        speed.currentIndexChanged.connect(lambda i:self.player.setPlaybackRate([.75,1,1.25,1.5][i])); player_row.addWidget(speed)
        body.addLayout(player_row); self.content_layout.addWidget(panel)
        self.fill_timeline()

    def fill_timeline(self):
        if not hasattr(self,'timeline') or self.page not in ('file','live'): return
        rows=self.store.segments(self.transcript_id,self.version_id) if self.transcript_id else []
        self.timeline_rows=rows; self.timeline.setRowCount(len(rows))
        states={'queued':'Chờ dịch','translating':'Đang dịch…','failed':'Dịch lỗi · Thử lại trong thư viện','untranslated':'Chưa dịch'}
        for i,row in enumerate(rows):
            vi=row['vi'] if row['translation_status']=='complete' else states.get(row['translation_status'],'Chưa dịch')
            if row['note'] and self.store.setting('show_notes',False): vi+='\n\nⓘ '+row['note']
            for j,text in enumerate([timestamp(row['start'])+'\n'+timestamp(row['end']),row['zh'],vi]):
                item=QTableWidgetItem(text); item.setToolTip(row.get('error','') or row.get('note',''))
                font=QFont('Noto Sans SC' if j==1 else 'Noto Sans'); font.setPixelSize(18 if j==1 else 14 if j==2 else 11); item.setFont(font)
                self.timeline.setItem(i,j,item)
            self.timeline.setRowHeight(i,max(100,self.timeline.rowHeight(i)))
        self.timeline.resizeRowsToContents()
        for i in range(len(rows)): self.timeline.setRowHeight(i,max(95,self.timeline.rowHeight(i)+14))

    def toggle_play(self):
        if not self.audio_id: return
        if self.player.playbackState()==QMediaPlayer.PlaybackState.PlayingState: self.player.pause()
        else: self.player.play()

    def toggle_notes(self,checked):
        self.store.set_setting('show_notes',checked)
        if self.page=='file': self.fill_timeline()

    def playback_position(self,position):
        if self.page=='file' and hasattr(self,'seek_slider'):
            self.play_label.setText(timestamp(position/1000))
            if not self.seek_slider.isSliderDown(): self.seek_slider.setValue(position)
            for i,row in enumerate(getattr(self,'timeline_rows',[])):
                if row['start']<=position/1000<row['end']:
                    self.timeline.selectRow(i); break

    def seek_segment(self,row,column):
        segment=self.timeline_rows[row]
        self.player.setPosition(int(segment['start']*1000))

    def edit_segment(self,row,column):
        if column not in (1,2) or self.is_busy or self.recording: return
        original=self.timeline_rows[row]
        if column==1:
            # Editing Chinese creates a new transcript, preserving all older version alignments.
            text,ok=QInputDialog.getMultiLineText(self,'Sửa chép lời · tạo bản mới','Tiếng Trung',original['zh'])
            if not ok or not text.strip(): return
            new=self.store.new_transcript(self.audio_id,'manual-edit')
            for item in self.timeline_rows:
                self.store.append_segment(new,item['start'],item['end'],text if item['id']==original['id'] else item['zh'],item['timing'])
            self.store.set_transcript_status(new,'complete'); self.transcript_id=new; self.version_id=None
        elif self.version_id:
            text,ok=QInputDialog.getMultiLineText(self,'Hiệu đính bản dịch · tạo phiên bản mới','Tiếng Việt',original['vi'])
            if not ok or not text.strip(): return
            old=self.store.one('SELECT * FROM versions WHERE id=?',(self.version_id,))
            new=self.store.new_version(self.audio_id,self.transcript_id,old['model'],old['effort'],old['context'],json.loads(old['glossary']))
            for item in self.timeline_rows:
                if item['id']==original['id'] or item['translation_status']=='complete':
                    self.store.translation_result(new,item['id'],text if item['id']==original['id'] else item['vi'],item['note'])
            self.store.set_version_status(new,'complete' if all(x['translation_status']=='complete' for x in self.store.segments(self.transcript_id,new)) else 'partial')
            self.version_id=new
        self.navigate('file')

    def export(self,language):
        if not self.transcript_id: self.error('Chưa có bản chép lời.'); return
        if language=='vi' and not self.version_id: self.error('Chưa có bản dịch.'); return
        audio=self.store.one('SELECT * FROM audio WHERE id=?',(self.audio_id,))
        version=self.store.one('SELECT number FROM versions WHERE id=?',(self.version_id,)) if self.version_id else None
        name=Path(audio['filename']).stem+f"_v{version['number'] if version else 'transcript'}_{language}.txt"
        path,_=QFileDialog.getSaveFileName(self,'Xuất TXT UTF-8',name,'Văn bản (*.txt)')
        if not path: return
        try:
            export_txt(self.store,self.transcript_id,self.version_id,path,language)
            self.statusBar().showMessage('Đã xuất '+path)
        except Exception as error: self.error(error)

    def show_library(self):
        self.context_action('Tất cả âm thanh','library'); self.context_action('Nhập âm thanh mới','file'); self.context_action('Thùng rác','trash')
        self.context_layout.addWidget(label('Mỗi nguồn chỉ lưu một lần. Các phiên bản cùng dùng âm thanh gốc.','muted',True))
        self.header.addWidget(button('Nhập file mới',self.choose_audio,True))
        search=QLineEdit(); search.setPlaceholderText('Tìm bài giảng, tên file…'); self.content_layout.addWidget(search)
        table=QTableWidget(0,5); table.setHorizontalHeaderLabels(['Âm thanh','Thời lượng','Ngày nhập','Nguồn','Bản dịch'])
        table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().hide(); table.setMinimumHeight(230)
        details,detail_layout=card('Các phiên bản')
        def select():
            current=table.currentRow()
            if current<0: return
            audio=table.item(current,0).data(Qt.ItemDataRole.UserRole)
            clear(detail_layout); detail_layout.addWidget(label(audio['filename']+' · 1 âm thanh gốc','heading',True))
            row=QHBoxLayout(); row.addWidget(button('Mở / chép lời',lambda:self.open_audio(audio['id'])))
            row.addWidget(button('Xóa âm thanh',lambda:self.delete_audio(audio['id']),danger=True)); detail_layout.addLayout(row)
            versions=self.store.versions(audio['id'])
            for version in versions:
                item,item_layout=card(f"v{version['number']} · {version['model']}")
                item_layout.addWidget(label(f"{version['effort']} · {version['created']} · {state_name(version['status'])}",'muted',True))
                actions=QHBoxLayout(); actions.addWidget(button('Mở bản dịch',lambda checked=False,v=version:self.open_audio(v['audio_id'],v['id'])))
                actions.addWidget(button('Xóa bản dịch',lambda checked=False,v=version:self.delete_version(v),danger=True))
                item_layout.addLayout(actions)
                if version['status']!='complete': item_layout.addWidget(button('Tiếp tục / thử lại',lambda checked=False,v=version:self.resume_translation(v['id'])))
                detail_layout.addWidget(item)
            if len(versions)>1: detail_layout.addWidget(button('So sánh hai phiên bản',lambda:self.compare_versions(versions[1],versions[0])))
        def populate():
            rows=[x for x in self.store.list_audio() if search.text().casefold() in (x['title']+' '+x['filename']).casefold()]
            table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                values=[row['title']+'\n'+row['filename'],timestamp(row['duration']),row['created'][:10],'Tải lên' if row['source']=='upload' else 'Ghi trực tiếp',str(row['version_count'])]
                for j,text in enumerate(values):
                    item=QTableWidgetItem(text); item.setData(Qt.ItemDataRole.UserRole,row); table.setItem(i,j,item)
                table.setRowHeight(i,64)
            if rows: table.selectRow(0); select()
            else: clear(detail_layout); detail_layout.addWidget(label('Chưa có âm thanh phù hợp.','muted'))
        table.itemSelectionChanged.connect(select); table.cellDoubleClicked.connect(lambda r,c:self.open_audio(table.item(r,0).data(Qt.ItemDataRole.UserRole)['id']))
        search.textChanged.connect(populate); populate()
        split=QSplitter(Qt.Orientation.Horizontal if self.width()>=1250 else Qt.Orientation.Vertical)
        split.addWidget(table); split.addWidget(details); split.setStretchFactor(0,3); split.setStretchFactor(1,2)
        split.setSizes([650,360]); self.content_layout.addWidget(split)

    def delete_audio(self,audio_id):
        if self.is_busy or self.recording: self.error('Hãy dừng tác vụ trước khi xóa.'); return
        audio=self.store.one('SELECT * FROM audio WHERE id=?',(audio_id,)); versions=self.store.versions(audio_id)
        msg=f"Chuyển {audio['filename']} và {len(versions)} bản dịch liên quan vào Thùng rác?\n"+'\n'.join(f"v{x['number']} · {x['model']}" for x in versions)+'\nBạn có thể khôi phục trước khi xóa vĩnh viễn.'
        if QMessageBox.question(self,'Xóa âm thanh và các bản liên quan',msg,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes: return
        self.player.stop(); self.player.setSource(QUrl()); self.store.trash_audio(audio_id)
        if self.audio_id==audio_id: self.audio_id=self.transcript_id=self.version_id=None
        self.navigate('library')

    def delete_version(self,version):
        if self.is_busy or self.recording: self.error('Hãy dừng tác vụ trước khi xóa.'); return
        last=len(self.store.versions(version['audio_id']))==1
        dialog=QDialog(self); dialog.setWindowTitle('Chuyển bản dịch vào Thùng rác'); layout=QVBoxLayout(dialog)
        layout.addWidget(label(f"Chuyển bản dịch v{version['number']} vào Thùng rác? Âm thanh gốc được giữ lại.",wrap=True))
        also=QCheckBox('Chuyển cả âm thanh gốc vào Thùng rác'); also.setChecked(False)
        if last: layout.addWidget(also)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec()!=QDialog.DialogCode.Accepted: return
        self.store.trash_version(version['id'],last and also.isChecked()); self.navigate('library')

    def compare_versions(self,one,two):
        if one['transcript_id']!=two['transcript_id']: self.error('Hai bản dùng transcript khác nhau; không thể ghép chính xác từng đoạn.'); return
        dialog=QDialog(self); dialog.setWindowTitle('So sánh phiên bản'); dialog.resize(1000,650); layout=QVBoxLayout(dialog)
        table=QTableWidget(0,3); table.setHorizontalHeaderLabels(['Mốc giờ',f"v{one['number']}",f"v{two['number']}"])
        first=self.store.segments(one['transcript_id'],one['id']); second=self.store.segments(two['transcript_id'],two['id']); table.setRowCount(len(first))
        for i,(a,b) in enumerate(zip(first,second)):
            for j,text in enumerate([timestamp(a['start']),a['vi'],b['vi']]): table.setItem(i,j,QTableWidgetItem(text))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); table.resizeRowsToContents(); layout.addWidget(table); dialog.exec()

    def show_trash(self):
        self.context_layout.addWidget(label('Các mục có thể khôi phục. Xóa một bản dịch không xóa âm thanh dùng chung.','muted',True))
        rows=self.store.list_audio(True)
        versions=self.store.rows('SELECT v.*,a.filename,a.deleted audio_deleted FROM versions v JOIN audio a ON a.id=v.audio_id WHERE v.deleted IS NOT NULL AND a.deleted IS NULL ORDER BY v.deleted DESC')
        for item in rows:
            panel,body=card(item['filename']); body.addWidget(label('Âm thanh và các phiên bản liên quan','muted'))
            actions=QHBoxLayout(); actions.addWidget(button('Khôi phục',lambda checked=False,a=item['id']:self.restore('audio',a)))
            actions.addWidget(button('Xóa vĩnh viễn',lambda checked=False,a=item['id']:self.purge('audio',a),danger=True)); body.addLayout(actions); self.content_layout.addWidget(panel)
        for item in versions:
            panel,body=card(f"v{item['number']} · {item['filename']}"); body.addWidget(label('Bản dịch · Giữ nguyên âm thanh gốc','muted'))
            actions=QHBoxLayout(); actions.addWidget(button('Khôi phục',lambda checked=False,a=item['id']:self.restore('version',a)))
            actions.addWidget(button('Xóa vĩnh viễn',lambda checked=False,a=item['id']:self.purge('version',a),danger=True)); body.addLayout(actions); self.content_layout.addWidget(panel)
        if not rows and not versions: self.content_layout.addWidget(label('Thùng rác đang trống.','heading'))

    def restore(self,kind,identifier):
        try:
            getattr(self.store,'restore_'+kind)(identifier); self.navigate('trash')
        except Exception as error: self.error(error)

    def purge(self,kind,identifier):
        if self.is_busy or self.recording: self.error('Hãy dừng tác vụ trước.'); return
        if kind=='audio':
            audio=self.store.one('SELECT * FROM audio WHERE id=?',(identifier,))
            versions=self.store.versions(identifier,True)
            message=f"Xóa vĩnh viễn {audio['filename']} và {len(versions)} bản dịch? Không thể hoàn tác."
        else: message='Xóa vĩnh viễn bản dịch này? Âm thanh gốc được giữ. Không thể hoàn tác.'
        if QMessageBox.warning(self,'Xác nhận xóa vĩnh viễn',message,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes: return
        try:
            getattr(self.store,'purge_'+kind)(identifier); self.navigate('trash')
        except Exception as error: self.error(error)

    def show_prompts(self):
        sets=self.store.rows('SELECT * FROM glossaries ORDER BY name')
        chosen=next((x for x in sets if x['id']==self.glossary_id),sets[0] if sets else None)
        self.glossary_id=chosen['id'] if chosen else None
        for item in sets:
            self.context_layout.addWidget(button(item['name'],lambda checked=False,g=item['id']:self.select_glossary(g)))
        self.context_layout.addWidget(button('Tạo bộ mới',self.new_glossary))
        panel,body=card('Bối cảnh & Thuật ngữ')
        self.glossary_name=QLineEdit(chosen['name'] if chosen else '')
        self.field(body,'Tên bộ',self.glossary_name)
        self.glossary_context=QPlainTextEdit(chosen['context'] if chosen else ''); self.glossary_context.setMinimumHeight(120)
        self.field(body,'Bối cảnh bài giảng',self.glossary_context)
        entries=json.loads(chosen['entries']) if chosen else []
        self.glossary_table=QTableWidget(len(entries)+1,3); self.glossary_table.setHorizontalHeaderLabels(['Tiếng Trung','Tiếng Việt ưu tiên','Ghi chú'])
        self.glossary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.glossary_table.setMinimumHeight(250)
        for i,item in enumerate(entries):
            for j,key in enumerate(['zh','vi','note']): self.glossary_table.setItem(i,j,QTableWidgetItem(item.get(key,'')))
        body.addWidget(self.glossary_table); actions=QHBoxLayout(); actions.addWidget(button('Thêm dòng',lambda:self.glossary_table.insertRow(self.glossary_table.rowCount())))
        actions.addWidget(button('Xóa dòng chọn',lambda:self.glossary_table.removeRow(self.glossary_table.currentRow())))
        actions.addWidget(button('Lưu bộ thuật ngữ',self.save_glossary,True)); body.addLayout(actions); self.content_layout.addWidget(panel)
        self.glossary_clean=self.glossary_state()

    def glossary_state(self):
        entries=[]
        for i in range(self.glossary_table.rowCount()):
            row=[self.glossary_table.item(i,j).text() if self.glossary_table.item(i,j) else '' for j in range(3)]
            if any(row): entries.append(row)
        return [self.glossary_name.text(),self.glossary_context.toPlainText(),entries]

    def confirm_glossary_changes(self):
        if self.page!='prompts' or self.glossary_clean is None or self.glossary_state()==self.glossary_clean: return True
        choice=QMessageBox.question(self,'Thuật ngữ chưa lưu','Lưu thay đổi trước khi rời bộ thuật ngữ?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if choice==QMessageBox.StandardButton.Cancel: return False
        if choice==QMessageBox.StandardButton.Save: return self.save_glossary(refresh=False)
        self.glossary_clean=self.glossary_state(); return True

    def select_glossary(self,identifier):
        if not self.confirm_glossary_changes(): return
        self.glossary_id=identifier; self.navigate('prompts')

    def new_glossary(self):
        if not self.confirm_glossary_changes(): return
        name,ok=QInputDialog.getText(self,'Tạo bộ thuật ngữ','Tên bộ')
        if ok and name.strip(): self.glossary_id=self.store.save_glossary(name,'',[]); self.navigate('prompts')

    def save_glossary(self,*,refresh=True):
        entries=[]
        for i in range(self.glossary_table.rowCount()):
            entries.append({key:(self.glossary_table.item(i,j).text() if self.glossary_table.item(i,j) else '') for j,key in enumerate(['zh','vi','note'])})
        try:
            self.glossary_id=self.store.save_glossary(self.glossary_name.text(),self.glossary_context.toPlainText(),entries,self.glossary_id)
            self.store.set_setting('glossary_id',self.glossary_id); self.store.set_setting('context',self.glossary_context.toPlainText())
            self.glossary_clean=self.glossary_state()
            if refresh: self.navigate('prompts')
            self.statusBar().showMessage('Đã lưu bộ thuật ngữ.')
            return True
        except Exception as error: self.error(error); return False

    def show_settings(self):
        self.context_layout.addWidget(label('Công cụ dịch, mô hình và giao diện','muted',True))
        panel,body=card('Kết nối Codex CLI')
        body.addWidget(label(self.codex_status.get('version','Chưa kiểm tra')+' · '+self.codex_status.get('login_label','Chưa xác định đăng nhập'),'heading',True))
        path=QLineEdit(self.store.setting('codex_path',self.codex_status.get('path','')))
        path.setReadOnly(True); self.field(body,'Đường dẫn codex.exe',path)
        actions=QHBoxLayout(); actions.addWidget(button('Chọn codex.exe',self.choose_codex)); actions.addWidget(button('Kiểm tra kết nối',self.check_codex)); actions.addWidget(button('Đăng nhập',self.login_codex,True)); body.addLayout(actions)
        body.addWidget(label('1. Cài Codex CLI.\n2. Mở Terminal và chạy: codex login\n3. Hoàn tất đăng nhập trong trình duyệt.\n4. Chạy codex login status hoặc chọn Kiểm tra kết nối.','muted',True))
        body.addWidget(button('Sao chép hướng dẫn',lambda:QApplication.clipboard().setText('codex login\ncodex login status')))
        body.addWidget(button('Tài liệu Codex chính thức',lambda:QDesktopServices.openUrl(QUrl('https://learn.chatgpt.com/docs/developer-commands?surface=cli'))))
        self.content_layout.addWidget(panel)
        quota,quota_body=card('Hạn mức sử dụng · Số liệu trực tiếp từ Codex')
        limits=self.codex_status.get('limits',{})
        limit=limits.get('rateLimits',{})
        windows=[limit.get('primary'),limit.get('secondary')]
        if not any(windows): quota_body.addWidget(label('Chưa thể đọc hạn mức trong kết nối hiện tại. Không tự ước tính.','muted',True))
        from datetime import datetime,timezone,timedelta
        for item in windows:
            if not item: continue
            minutes=item.get('windowDurationMins')
            name='5 giờ' if minutes==300 else '1 tuần' if minutes==10080 else f'{minutes} phút'
            reset=datetime.fromtimestamp(item['resetsAt'],timezone(timedelta(hours=7))).strftime('%d/%m %H:%M UTC+7') if item.get('resetsAt') else 'Chưa có dữ liệu reset'
            quota_body.addWidget(label(f"Cửa sổ {name}: đã dùng {item['usedPercent']}% · Reset: {reset}",wrap=True))
        self.content_layout.addWidget(quota)
        panel,body=card('Mô hình, mức suy luận & giao diện')
        available=QListWidget(); available.setMaximumHeight(250)
        def normalized(text): return ''.join(c for c in text.lower() if c.isalnum())
        models_by_name={normalized(x['displayName']):x for x in self.models}
        for name in APPROVED_MODELS:
            item=models_by_name.get(normalized(name)); available.addItem(name+(' · Khả dụng' if item else ' · Chưa xác minh / không khả dụng'))
        body.addWidget(available)
        body.addWidget(label('Danh sách và mức suy luận được đọc từ model/list. Không tự đổi model khi lựa chọn không được hỗ trợ.','muted',True))
        model_choice=QComboBox(); effort_choice=QComboBox()
        for item in self.models: model_choice.addItem(item['displayName'],item['model'])
        previous_model=self.store.setting('model'); selected=model_choice.findData(previous_model)
        if previous_model and selected<0:
            model_choice.addItem(previous_model+' · Không khả dụng',previous_model); selected=model_choice.count()-1; model_choice.model().item(selected).setEnabled(False)
        model_choice.setCurrentIndex(max(0,selected))
        def supported_efforts():
            effort_choice.clear(); item=next((x for x in self.models if x['model']==model_choice.currentData()),None)
            if item:
                for value in item['supportedReasoningEfforts']: effort_choice.addItem(value['reasoningEffort'],value['reasoningEffort'])
                chosen=self.store.setting('effort',item['defaultReasoningEffort']) if model_choice.currentData()==previous_model else item['defaultReasoningEffort']
                index=effort_choice.findData(chosen)
                if chosen and index<0:
                    effort_choice.addItem(chosen+' · Không khả dụng',chosen); index=effort_choice.count()-1
                    effort_choice.model().item(index).setEnabled(False)
                effort_choice.setCurrentIndex(max(0,index))
            else: effort_choice.addItem('Chưa xác minh',None)
        model_choice.currentIndexChanged.connect(supported_efforts); supported_efforts()
        self.field(body,'Mô hình mặc định',model_choice); self.field(body,'Mức suy luận mặc định',effort_choice)
        def save_default():
            try:
                validate_selection(self.models,model_choice.currentData(),effort_choice.currentData())
                self.store.set_setting('model',model_choice.currentData()); self.store.set_setting('effort',effort_choice.currentData())
                self.statusBar().showMessage('Đã lưu mô hình và mức suy luận mặc định.')
            except Exception as error: self.error(error)
        body.addWidget(button('Lưu mặc định',save_default,True))
        theme=QComboBox(); theme.addItems(['Sáng','Tối']); theme.setCurrentIndex(1 if self.colors['bg']==DARK['bg'] else 0); theme.currentIndexChanged.connect(self.change_theme)
        self.field(body,'Giao diện',theme)
        self.add_asr_settings(body)
        body.addWidget(button('Sao lưu cơ sở dữ liệu',self.backup))
        body.addWidget(button('Mở thư mục dữ liệu',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.store.root)))))
        self.content_layout.addWidget(panel)

    def backup(self):
        try: self.statusBar().showMessage('Đã sao lưu: '+str(self.store.backup()))
        except Exception as error: self.error(error)

    def change_theme(self,index):
        self.store.set_setting('theme','dark' if index else 'light'); super().change_theme(index)

    def add_asr_settings(self,body):
        body.addWidget(label('Nhận dạng giọng nói cục bộ','heading'))
        body.addWidget(label('Thư mục mô hình: '+str(self.model_manager.root),'muted',True))
        for key in ('sensevoice','paraformer','vad'):
            body.addWidget(button(CATALOG[key]['name']+(' · Đã có' if self.model_manager.ready(key) else ' · Tải mô hình'),lambda checked=False,k=key:self.install_model(k)))
        body.addWidget(button('Chọn thư mục mô hình',self.choose_model_dir))
        threads=QSpinBox(); threads.setRange(1,4); threads.setValue(self.store.setting('asr_threads',4))
        threads.valueChanged.connect(lambda value:self.store.set_setting('asr_threads',value)); self.field(body,'Luồng CPU ASR (1–4)',threads)
        if self.recovered:
            body.addWidget(label('Tác vụ bị gián đoạn','heading'))
            for row in self.recovered:
                body.addWidget(button(row['kind']+' · Phục hồi',lambda checked=False,j=row:self.recover_job(j)))

    def choose_model_dir(self):
        path=QFileDialog.getExistingDirectory(self,'Thư mục chứa sensevoice / paraformer / vad',str(self.model_manager.root))
        if path:
            self.model_manager=ModelManager(path); self.store.set_setting('model_dir',path); self.navigate('settings')

    def install_model(self,key):
        if self.model_manager.ready(key): self.statusBar().showMessage('Mô hình đã sẵn sàng.'); return
        self.cancel_event.clear()
        self.submit(lambda progress:self.model_manager.install(key,progress,self.cancel_event),lambda _:self.navigate('settings'),lambda message:self.statusBar().showMessage(str(message)))

    def transcribe(self):
        if not self.audio_id: self.choose_audio(); return
        if self.recording: self.error('Hãy kết thúc phiên ghi âm trước.'); return
        if self.transcript_id and self.store.segments(self.transcript_id):
            if QMessageBox.question(self,'Chép lời lại','Tạo bản chép lời mới? Các bản cũ được giữ nguyên.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes: return
        self.capture_options(); self.cancel_event.clear(); audio_id=self.audio_id
        def progress(item):
            if item.get('transcript_id'):
                self.transcript_id=item['transcript_id']; self.version_id=None
                if self.page=='file': self.fill_timeline()
            self.statusBar().showMessage('Đang chép lời cục bộ… '+(timestamp(item['seconds']) if 'seconds' in item else ''))
        def done(transcript):
            self.audio_id=audio_id; self.transcript_id=transcript; self.version_id=None
            if self.page=='file': self.navigate('file')
        self.submit(lambda emit:transcribe_job(self.store,self.model_manager,audio_id,emit,self.cancel_event,self.store.setting('asr_threads',4)),done,progress)

    def show_live(self):
        import sounddevice as sd
        self.mic_select=QComboBox()
        for i,device in enumerate(sd.query_devices()):
            if device['max_input_channels']>0: self.mic_select.addItem(device['name'],i)
        chosen=self.mic_select.findData(self.store.setting('mic_device')); self.mic_select.setCurrentIndex(max(0,chosen))
        self.field(self.context_layout,'Microphone',self.mic_select)
        self.options()
        controls,body=card()
        row=QHBoxLayout(); self.live_timer_label=label('Đang dừng · 00:00','heading'); row.addWidget(self.live_timer_label,1)
        self.record_button=button('Bắt đầu',self.start_recording,True); self.pause_button=button('Tạm dừng',self.pause_recording); self.stop_button=button('Dừng & lưu',self.stop_recording,danger=True)
        self.record_button.setEnabled(not self.recording); self.pause_button.setEnabled(bool(self.recording)); self.stop_button.setEnabled(bool(self.recording))
        row.addWidget(self.record_button); row.addWidget(self.pause_button); row.addWidget(self.stop_button); body.addLayout(row); self.content_layout.addWidget(controls)
        self.microphone_level=QProgressBar(); self.microphone_level.setRange(0,100); self.microphone_level.setValue(0)
        self.microphone_level.setFormat('Mức tín hiệu microphone: %p%'); body.addWidget(self.microphone_level)
        panel,body=card('Dòng thời gian song ngữ · Chỉ dịch câu đã chốt')
        self.timeline=QTableWidget(0,3); self.timeline.setHorizontalHeaderLabels(['Mốc giờ','ZH · TIẾNG TRUNG','VI · TIẾNG VIỆT'])
        self.timeline.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.timeline.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.timeline.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        self.timeline.verticalHeader().hide(); self.timeline.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.timeline.setMinimumHeight(330)
        self.follow_live=QCheckBox('Theo đoạn mới nhất'); self.follow_live.setChecked(True); body.addWidget(self.follow_live)
        self.timeline.verticalScrollBar().actionTriggered.connect(lambda _:self.follow_live.setChecked(False))
        body.addWidget(self.timeline)
        self.interim_label=label('Đang nghe · Câu chưa chốt\n'+self.live_interim,'muted',True)
        self.interim_label.setStyleSheet(f"background:{self.colors['soft']};border:1px dashed {self.colors['line']};border-radius:12px;padding:15px")
        body.addWidget(self.interim_label); self.content_layout.addWidget(panel)
        self.render_live()
        for widget in [self.mic_select,*self.option_widgets]: widget.setEnabled(not self.recording)

    def start_recording(self):
        if self.is_busy or self.recording: self.error('Một tác vụ đang chạy.'); return
        if self.mic_select.currentData() is None: self.error('Không tìm thấy microphone.'); return
        self.capture_options(); device=self.mic_select.currentData(); self.store.set_setting('mic_device',device)
        self.cancel_event.clear()
        self.live_segments=[]; self.live_interim=''
        self.statusBar().showMessage('Đang tải mô hình và mở microphone…')
        try: options=self.translation_options() if self.models and self.store.setting('model') else None
        except Exception as error: self.error(error); return
        def begin(progress):
            config=None
            if options:
                executable=find_codex(self.store.setting('codex_path')); actual=capabilities(executable,self.store.root/'work')
                validate_selection(actual['models'],options['model'],options['effort'])
                config=dict(options,executable=executable,models=actual['models'])
            session=LiveSession(self.store,self.model_manager,self.live_signals.event.emit,device,self.store.setting('asr_threads',4),config)
            if self.cancel_event.is_set(): raise InterruptedError('Đã hủy trước khi mở microphone.')
            return session.start()
        def done(session):
            self.recording=session; self.navigate('live')
            self.record_timer=QTimer(self); self.record_timer.timeout.connect(self.update_record_timer); self.record_timer.start(500)
        self.submit(begin,done)

    def update_record_timer(self):
        if self.recording:
            state='Tạm dừng' if self.recording.paused else 'Đang ghi âm' if self.recording.samples else 'Chờ dữ liệu microphone'
            value=state+' · '+timestamp(self.recording.samples/16000)
            self.activity.setText(value)
            if self.page=='live': self.live_timer_label.setText(value)

    def pause_recording(self):
        if self.recording:
            try:
                paused=self.recording.pause(); self.pause_button.setText('Tiếp tục' if paused else 'Tạm dừng')
            except Exception as error: self.error(error)

    def stop_recording(self):
        if not self.recording or self.is_busy: return
        session=self.recording; self.stop_button.setEnabled(False)
        def done(result):
            self.recording=None
            if self.record_timer: self.record_timer.stop()
            if not result.get('audio_id'):
                self.navigate('live'); self.error(result['warning']); return
            self.audio_id=result['audio_id']; self.transcript_id=result['transcript_id']; self.version_id=result.get('version_id')
            self.player.setSource(QUrl.fromLocalFile(str(self.store.audio_path(self.audio_id))))
            self.navigate('file')
            if result.get('warning'): self.error(result['warning'])
        def failed(message):
            if session.closed.is_set():
                self.recording=None
                if self.record_timer: self.record_timer.stop()
                self.recovered=self.store.rows("SELECT * FROM jobs WHERE state='interrupted'")
                self.navigate('settings')
            self.error(message)
        self.submit(lambda progress:session.stop(),done,error_handler=failed)

    def live_event(self,item):
        kind=item.get('type')
        if kind=='final': self.live_segments.append(item)
        elif kind=='translation':
            for row in self.live_segments:
                if row.get('id')==item['id']: row.update(item); break
        elif kind=='interim': self.live_interim=item.get('zh','')
        elif kind=='warning': self.statusBar().showMessage(item['message']); return
        elif kind=='level' and self.page=='live': self.microphone_level.setValue(item.get('level',0))
        if self.page=='live': self.render_live()

    def render_live(self):
        if self.page!='live' or not hasattr(self,'timeline'): return
        position=self.timeline.verticalScrollBar().value(); self.timeline.setRowCount(len(self.live_segments))
        for i,row in enumerate(self.live_segments):
            state=row.get('translation_status','untranslated')
            translated=row.get('vi') or {'queued':'Trong hàng đợi dịch','translating':'Đang dịch…','failed':'Dịch lỗi · Lưu phiên để thử lại'}.get(state,'Đã chốt câu · Chưa kết nối dịch')
            if row.get('note') and self.store.setting('show_notes',False): translated+='\nⓘ '+row['note']
            for j,text in enumerate([timestamp(row['start'])+'\n'+timestamp(row['end']),row['zh'],translated]): self.timeline.setItem(i,j,QTableWidgetItem(text))
            self.timeline.setRowHeight(i,95)
        self.interim_label.setText('Đang nghe · Câu chưa chốt (có thể thay đổi)\n'+self.live_interim)
        if self.follow_live.isChecked(): self.timeline.scrollToBottom()
        else: self.timeline.verticalScrollBar().setValue(position)
        if self.recording: self.update_record_timer()

    def recover_job(self,job):
        payload=json.loads(job['payload'])
        if job['kind']=='recording':
            def done(result):
                self.recovered=[x for x in self.recovered if x['id']!=job['id']]; self.open_audio(result['audio_id'])
            self.submit(lambda progress:materialize_recording(self.store,payload,job['id']),done)
        elif job['kind']=='transcribe':
            self.audio_id=payload['audio_id']; self.transcript_id=None; self.transcribe()
        elif job['kind']=='translate': self.resume_translation(job['target'])

    def check_codex(self):
        def work(progress): return capabilities(find_codex(self.store.setting('codex_path')),self.store.root/'work')
        def done(result):
            self.codex_status=result; self.models=result['models']
            if self.page in ('settings','file','live','dashboard') and not self.recording: self.navigate(self.page)
            self.statusBar().showMessage('Codex: '+result['login_label'])
        self.submit(work,done,busy=False,error_handler=lambda message:self.statusBar().showMessage('Codex: '+message))

    def choose_codex(self):
        path,_=QFileDialog.getOpenFileName(self,'Chọn Codex CLI','','Codex (codex.exe);;EXE (*.exe)')
        if path:
            self.store.set_setting('codex_path',path); self.check_codex()

    def login_codex(self):
        from .audio import hidden_process
        import subprocess
        self.cancel_event.clear()
        def work(progress):
            executable=find_codex(self.store.setting('codex_path'))
            process=subprocess.Popen([executable,'login'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,**hidden_process())
            try:
                import time
                deadline=time.monotonic()+300
                while process.poll() is None:
                    if self.cancel_event.wait(.25): raise InterruptedError('Đã hủy chờ đăng nhập.')
                    if time.monotonic()>deadline: raise TimeoutError('Đăng nhập chưa hoàn tất sau 5 phút.')
                if process.returncode: raise ValueError('Đăng nhập chưa hoàn tất. Dùng hướng dẫn Terminal hoặc thử lại.')
                return True
            finally:
                if process.poll() is None: process.terminate(); process.wait(timeout=5)
        self.submit(work,lambda _:self.check_codex())

    def translation_options(self):
        self.capture_options()
        model=self.store.setting('model'); effort=self.store.setting('effort')
        validate_selection(self.models,model,effort)
        glossary=self.store.one('SELECT * FROM glossaries WHERE id=?',(self.store.setting('glossary_id'),))
        return dict(model=model,effort=effort,context=self.store.setting('context',''),glossary=json.loads(glossary['entries']) if glossary else [])

    def translate(self):
        if self.recording: self.error('Phiên ghi âm đang chạy; bản dịch trực tiếp được xử lý theo câu đã chốt.'); return
        if not self.transcript_id or not self.store.segments(self.transcript_id): self.error('Chép lời tiếng Trung trước khi dịch.'); return
        try: options=self.translation_options()
        except Exception as error: self.error(error); return
        source=self.store.one('SELECT status FROM transcripts WHERE id=?',(self.transcript_id,))
        if source['status']!='complete': self.error('Bản chép lời chưa đầy đủ. Chép lời lại hoặc phục hồi tác vụ trước khi dịch.'); return
        audio_id,transcript=self.audio_id,self.transcript_id; self.cancel_event.clear()
        def work(progress):
            executable=find_codex(self.store.setting('codex_path'))
            actual=capabilities(executable,self.store.root/'work',self.cancel_event)
            validate_selection(actual['models'],options['model'],options['effort'])
            version=self.store.new_version(audio_id,transcript,**options)
            return translate_version(self.store,executable,version,actual['models'],progress,self.cancel_event)
        self.submit(work,lambda identifier:self.open_audio(audio_id,identifier),self.translation_progress)

    def translation_progress(self,item):
        self.version_id=item['version_id']
        version=self.store.one('SELECT * FROM versions WHERE id=?',(self.version_id,)); self.transcript_id=version['transcript_id']
        if self.page=='file': self.fill_timeline()
        self.statusBar().showMessage(f"Đang dịch: {item['done']}/{item['total']} đoạn")

    def resume_translation(self,identifier):
        if self.recording: self.error('Hãy kết thúc ghi âm trước.'); return
        self.cancel_event.clear()
        version=self.store.one('SELECT * FROM versions WHERE id=?',(identifier,))
        def work(progress):
            executable=find_codex(self.store.setting('codex_path')); actual=capabilities(executable,self.store.root/'work',self.cancel_event)
            return translate_version(self.store,executable,identifier,actual['models'],progress,self.cancel_event)
        self.submit(work,lambda _:self.open_audio(version['audio_id'],identifier),self.translation_progress)
    def cancel_work(self): self.cancel_event.set()

    def dragEnterEvent(self,event):
        urls=event.mimeData().urls()
        if len(urls)==1 and urls[0].isLocalFile() and not self.is_busy and not self.recording: event.acceptProposedAction()

    def dropEvent(self,event):
        urls=event.mimeData().urls()
        if len(urls)==1 and urls[0].isLocalFile():
            self.import_audio(urls[0].toLocalFile()); event.acceptProposedAction()

    def closeEvent(self,event):
        self.capture_options()
        if self.is_busy or self.recording:
            self.error('Hãy dừng tác vụ/ghi âm và lưu kết quả trước khi đóng ứng dụng.'); event.ignore(); return
        if not self.confirm_glossary_changes(): event.ignore(); return
        self.player.stop(); event.accept()
