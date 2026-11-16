from __future__ import annotations
import json
import os
from pathlib import Path
import threading
from PySide6.QtCore import Qt, QThreadPool, QTimer, QUrl, QSize, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,
    QPlainTextEdit,QLineEdit,QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem,
    QHeaderView,QAbstractItemView,QListWidget,QListWidgetItem,QDialog,QDialogButtonBox,
    QCheckBox,QInputDialog,QSlider,QProgressBar,QApplication,QSplitter,QPushButton,QSpacerItem,QSizePolicy)
from .window import MainWindow
from .widgets import PAGES,label,button,tonal_button,box,card,clear,ComboBox
from .file_page import FilePage, FilenameComboBox, NotesSwitch, transcription_context_styles, audio_thumbnail
from .live_page import LivePage
from .library_page import LibraryPage, library_context_styles
from .glossary_page import GlossaryPage, glossary_context_styles
from .dashboard_page import DashboardPage, DashboardActions
from .theme import LIGHT,DARK,stylesheet,icon
from .storage import Store
from .audio import audio_info,timestamp,export_txt,waveform_peaks
from .workers import Task
from .models import ModelManager
from .asr import transcribe_job
from .recording import LiveSession, materialize_recording
from .microphone import input_devices,selected_input,device_identity
from .pipeline import transcribe_translate_job
from .codex import capabilities,find_codex,validate_selection,translate_version
from .model_selector import ModelReasoningSelector
from .settings_page import SettingsPage
from .multimedia import configure_multimedia_logging

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
        self.waveforms={}; self.waveform_pending=set(); self.waveform_cancel=threading.Event()
        import sys
        bundled=Path(sys.executable).parent/'models' if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]/'models'
        self.model_manager=ModelManager(self.store.setting('model_dir',str(bundled if bundled.is_dir() else self.store.root/'models')))
        self.live_signals=LiveSignals(); self.live_signals.event.connect(self.live_event)
        self.live_segments=[]; self.live_interim=''; self.live_level=0; self.live_follow=True
        self.live_stopping=False; self.record_timer=None
        self.pool=QThreadPool(); self.pool.setMaxThreadCount(3)
        super().__init__()
        self.colors=dict(DARK if self.store.setting('theme','light')=='dark' else LIGHT)
        self.setStyleSheet(stylesheet(self.colors)); self.rail.apply_colors(self.colors)
        configure_multimedia_logging()
        self.player=QMediaPlayer(self); self.audio_output=QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self.playback_position)
        self.player.playbackStateChanged.connect(self.refresh_player)
        self.player.durationChanged.connect(self.refresh_player)
        self.player.errorOccurred.connect(lambda *args:self.statusBar().showMessage(self.player.errorString()))
        self.file_pipeline_progress=None
        self.file_pipeline_timer=QTimer(self); self.file_pipeline_timer.setSingleShot(True)
        self.file_pipeline_timer.setInterval(100); self.file_pipeline_timer.timeout.connect(self.render_file_pipeline_progress)
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
            self.is_busy=True; self.cancel_button.setEnabled(True); self.cancel_button.show(); self.activity.setText('Đang xử lý…')
            self.refresh_file_state()
            self.refresh_live_state()
            self.refresh_library_state()
        task.signals.error.connect(error_handler or self.error)
        if done: task.signals.result.connect(done)
        if progress: task.signals.progress.connect(progress)
        def finish():
            self.tasks.discard(task)
            if busy: self.is_busy=False
            if busy:
                self.cancel_button.hide()
                if not self.recording: self.activity.setText('')
                self.refresh_file_state()
                self.refresh_live_state()
                self.refresh_library_state()
        task.signals.finished.connect(finish)
        self.pool.start(task)

    def navigate(self,page):
        if not self._ready: return super().navigate(page)
        if not self.confirm_glossary_changes():
            self.rail.set_page(self.page); return
        self.capture_options()
        self.page=page; self.rail.set_page(page)
        clear(self.context_layout); clear(self.content_layout)
        self.context.setStyleSheet(transcription_context_styles(self.colors) if page in ('file','live') else '')
        if page=='library': self.context.setStyleSheet(library_context_styles(self.colors))
        if page=='prompts': self.context.setStyleSheet(glossary_context_styles(self.colors))
        self.update_context_panel()
        self.context_layout.setContentsMargins(12,20,12,12)
        settings=page=='settings'
        self.workspace_layout.setSpacing(0)
        self.workspace_layout.setContentsMargins(26,24,26,18 if page in ('live','library','prompts') else 20)
        titles={'dashboard':'Bạn muốn học gì?','file':'Dịch từ âm thanh','live':'Phiên học trực tiếp',
            'library':'Tài liệu của bạn','prompts':'Ngữ cảnh học tập','settings':'Tùy chỉnh','trash':'Thùng rác'}
        context_title=label(titles[page],'heading')
        if page=='dashboard': context_title.setStyleSheet('font-size:20px;font-weight:700')
        if page in ('file','live'): context_title.setObjectName(page+'_context_title')
        if page=='library': context_title.setObjectName('library_context_title')
        if page=='prompts': context_title.setObjectName('prompts_context_title')
        if settings: context_title.setStyleSheet('font-size:22px;font-weight:600')
        self.context_layout.addWidget(context_title)
        context_subtitle=label('Cá nhân hóa không gian học tập.' if settings else 'Không gian học tập Trung – Việt','muted',True)
        if page=='dashboard': context_subtitle.setStyleSheet(f"font-size:13px;color:{self.colors['muted']}")
        if page in ('file','live'): context_subtitle.setObjectName(page+'_context_subtitle')
        if settings: context_subtitle.setStyleSheet('font-size:13px')
        self.context_layout.addWidget(context_subtitle)
        self.context_layout.setSpacing(8)
        self.option_widgets=None
        getattr(self,'show_'+page)()
        self.context_layout.addStretch()
        if settings: self.context_layout.addWidget(self.settings_page.connection_footer())
        else:
            footer=button('●  Codex đã kết nối' if self.codex_status.get('authenticated') else 'Codex CLI · '+self.codex_status.get('login_label','Kết nối'),lambda:self.navigate('settings'))
            if page in ('file','live','library','prompts'): footer.setObjectName(page+'_connection')
            elif self.codex_status.get('authenticated'):
                footer.setStyleSheet(f"background:{self.colors['soft']};color:{self.colors['success']};border:0;text-align:left;padding:10px 12px")
            self.context_layout.addWidget(footer)
            if page not in ('file','live','library','prompts','dashboard'): self.content_layout.addStretch()
        if page=='file': self.apply_file_density()
        elif page=='live': self.apply_live_density()
        elif page=='library': self.apply_library_density()
        elif page=='prompts': self.apply_glossary_density()
        elif page=='dashboard': self.apply_dashboard_density()
        self.scroll.verticalScrollBar().setValue(0)

    def apply_dashboard_density(self):
        compact=self.height()<820
        self.context_layout.setContentsMargins(12,12 if compact else 20,12,10 if compact else 12)
        self.context_layout.setSpacing(4 if compact else 8)
        self.dashboard_header_gap.changeSize(0,0 if compact else 18,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.context_layout.invalidate()
        self.dashboard_actions.set_compact(compact)

    def apply_options_density(self):
        compact=self.height()<820
        self.context.ensurePolished()
        self.context_layout.setSpacing(4 if compact else 10)
        self.context_layout.setContentsMargins(12,12 if compact else 20,12,10 if compact else 12)
        if self.option_widgets:
            context,glossary,selector=self.option_widgets
            context.ensurePolished()
            context.setFixedHeight(58 if compact else 76)
            glossary.ensurePolished(); glossary.setFixedHeight(38 if compact else 40)
        return compact

    def apply_live_density(self):
        compact=self.apply_options_density()
        self.mic_select.ensurePolished(); self.mic_select.setFixedHeight(38 if compact else 40)
        self.live_page.set_compact(compact)

    def apply_file_density(self):
        compact=self.apply_options_density()
        for control in (self.file_import_button,self.file_source):
            control.ensurePolished(); control.setFixedHeight(42 if compact else 48)
        self.transcribe_button.ensurePolished(); self.transcribe_button.setFixedHeight(40 if compact else 46)
        self.file_page.set_compact(compact)

    def apply_library_density(self):
        compact=self.height()<820
        self.context_layout.setContentsMargins(12,12 if compact else 20,12,10 if compact else 12)
        self.context_layout.setSpacing(8 if compact else 10)
        self.library_page.set_compact(compact)

    def apply_glossary_density(self):
        compact=self.height()<820
        self.context_layout.setContentsMargins(12,12 if compact else 20,12,10 if compact else 12)
        self.context_layout.setSpacing(8 if compact else 10)
        if self.glossary_sets:
            self.glossary_sets.setFixedHeight(min(self.glossary_sets.count()*48+4,max(96,self.height()-300)))
        self.glossary_page.set_compact(compact)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self._ready and self.page=='file' and hasattr(self,'file_page'): self.apply_file_density()
        if self._ready and self.page=='live' and hasattr(self,'live_page'): self.apply_live_density()
        if self._ready and self.page=='library' and hasattr(self,'library_page'): self.apply_library_density()
        if self._ready and self.page=='prompts' and hasattr(self,'glossary_page'): self.apply_glossary_density()
        if self._ready and self.page=='dashboard' and hasattr(self,'dashboard_actions'):
            self.apply_dashboard_density()

    def capture_options(self):
        widgets=getattr(self,'option_widgets',None)
        if widgets:
            context,glossary,selector=widgets
            try:
                self.store.set_setting('context',context.toPlainText())
                self.store.set_setting('glossary_id',glossary.currentData())
                self.store.set_setting('model',selector.model_id)
                self.store.set_setting('effort',selector.effort)
                if self.page=='live' and self.mic_select.currentData() is not None:
                    self.store.set_setting('mic_device_identity',device_identity(self.mic_select.currentData()))
            except RuntimeError:
                pass

    def context_action(self,text,page):
        self.context_layout.addWidget(button(text,lambda:self.navigate(page)))

    def show_dashboard(self):
        self.dashboard_header_gap=QSpacerItem(0,18,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)
        self.context_layout.addItem(self.dashboard_header_gap)
        self.dashboard_actions=DashboardActions(self)
        self.context_layout.addWidget(self.dashboard_actions)
        self.dashboard_page=DashboardPage(self)
        self.content_layout.addWidget(self.dashboard_page,1)

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

    def open_audio(self,audio_id,version_id=None,*,transcript_only=False):
        self.audio_id=audio_id; self.version_id=version_id
        if version_id:
            row=self.store.one('SELECT * FROM versions WHERE id=?',(version_id,)); self.transcript_id=row['transcript_id']
        else:
            versions=self.store.versions(audio_id)
            if versions and not transcript_only:
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
        context.setPlaceholderText('Môn học, chủ đề, yêu cầu dịch…')
        glossary=ComboBox(); glossary.addItem('Không áp dụng',None)
        for row in self.store.rows('SELECT * FROM glossaries ORDER BY name'):
            glossary.addItem(row['name'],row['id'])
        index=glossary.findData(self.store.setting('glossary_id')); glossary.setCurrentIndex(max(0,index))
        self.model_selector=ModelReasoningSelector(self.models,self.store.setting('model'),self.store.setting('effort'),self.colors)
        self.field(self.context_layout,'Bối cảnh bài giảng',context)
        self.field(self.context_layout,'Bộ thuật ngữ',glossary)
        self.field(self.context_layout,'Mô hình & suy luận',self.model_selector)
        self.option_widgets=(context,glossary,self.model_selector)

    def show_file(self):
        upload=button('Chọn file âm thanh',self.choose_audio)
        upload.setIcon(icon('upload','#5F2BA6' if self.colors['bg']!=DARK['bg'] else self.colors['primary'],22))
        upload.setIconSize(QSize(22,22))
        upload.setObjectName('file_import')
        self.file_import_button=upload
        upload.setToolTip('Chọn file âm thanh hoặc kéo thả file vào cửa sổ.')
        self.context_layout.addWidget(upload)
        source=FilenameComboBox(); source.setObjectName('file_source'); source.addItem('Chọn từ thư viện',None)
        self.file_source=source
        for row in self.store.list_audio():
            source.addItem(audio_thumbnail(self.colors),row['filename'],row['id'])
            source.setItemData(source.count()-1,row['filename'],Qt.ItemDataRole.ToolTipRole)
        source.setCurrentIndex(max(0,source.findData(self.audio_id)))
        source.setIconSize(QSize(28,28))
        source.activated.connect(lambda _:self.open_audio(source.currentData()) if source.currentData() else None)
        self.context_layout.addWidget(source)
        self.options()
        self.file_translation_toggle=NotesSwitch(self.colors)
        self.file_translation_toggle.setObjectName('file_translation_mode')
        self.file_translation_toggle.setText('Dịch cả bài một lượt')
        self.file_translation_toggle.setAccessibleName('Chép lời xong, dịch cả bài một lượt')
        self.file_translation_toggle.setChecked(self.store.setting('file_translation_mode','parallel')=='whole')
        self.file_translation_toggle.setToolTip('Bật: chép lời hoàn tất rồi gửi toàn bộ bản chép lời trong một lượt dịch. Tắt: dịch song song các đoạn đã chốt.')
        self.file_translation_hint=label('','muted',True)
        self.file_translation_hint.setStyleSheet(f"font-size:12px;color:{self.colors['muted']}")
        self.file_translation_toggle.toggled.connect(self.file_translation_mode_changed)
        self.context_layout.addWidget(self.file_translation_toggle)
        self.context_layout.addWidget(self.file_translation_hint)
        self.file_translation_mode_changed(self.file_translation_toggle.isChecked())
        self.transcribe_button=button('Chép lời tiếng Trung',self.transcribe,True)
        self.transcribe_button.setIcon(icon('audio',self.colors['on_primary'],22)); self.transcribe_button.setIconSize(QSize(22,22))
        self.context_layout.addWidget(self.transcribe_button)
        audio=self.store.one('SELECT * FROM audio WHERE id=?',(self.audio_id,)) if self.audio_id else None
        self.file_page=FilePage(self,audio)
        self.timeline=self.file_page.timeline; self.notes_toggle=self.file_page.notes_toggle
        self.seek_slider=self.file_page.seek_slider; self.play_label=self.file_page.play_label
        self.timeline.cellDoubleClicked.connect(self.edit_segment)
        self.timeline.cellClicked.connect(self.seek_segment)
        self.content_layout.addWidget(self.file_page,1)
        self.fill_timeline()
        self.refresh_player()
        if audio: self.load_waveform(audio)

    def file_translation_mode_changed(self,whole):
        self.store.set_setting('file_translation_mode','whole' if whole else 'parallel')
        self.file_translation_hint.setText('Chép lời xong mới bắt đầu dịch.' if whole else 'Dịch song song các đoạn đã chốt.')

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
        self.refresh_file_state()

    def refresh_file_state(self):
        if self.page!='file' or not hasattr(self,'file_page'): return
        transcript=self.store.one('SELECT status,engine FROM transcripts WHERE id=?',(self.transcript_id,)) if self.transcript_id else None
        version=self.store.one('SELECT status FROM versions WHERE id=?',(self.version_id,)) if self.version_id else None
        rows=getattr(self,'timeline_rows',[])
        ready=bool(transcript and transcript['status']=='complete' and rows)
        idle=not self.is_busy and not self.recording
        self.transcribe_button.setEnabled(idle)
        self.file_translation_toggle.setEnabled(idle)
        self.transcribe_button.setText('Dịch bản chép lời' if self.models and ready and not self.version_id else 'Chép lời và dịch' if self.models else 'Chép lời tiếng Trung')
        self.transcribe_button.setToolTip(self.file_translation_toggle.toolTip() if self.models else 'Chép lời cục bộ. Kết nối Codex để dịch bản chép lời đã lưu.')
        self.file_page.export_zh.setEnabled(bool(rows))
        self.file_page.export_vi.setEnabled(bool(version and version['status']=='complete' and ready and all(row['translation_status']=='complete' for row in rows)))
        steps=self.file_page.steps
        steps.completed=3 if version and version['status']=='complete' else 2 if ready else 1 if self.audio_id else 0
        steps.setToolTip('Chép lời: '+state_name(transcript['status'])+' · '+transcript['engine']+' · Mốc giờ theo ranh giới lời nói' if transcript else 'Chọn âm thanh → Chép lời → Dịch tiếng Việt')
        steps.update()
        table=self.file_page.timeline
        table.empty.setVisible(not rows)
        if not rows:
            if self.is_busy:
                title,description='Đang xử lý…','Nội dung sẽ xuất hiện theo từng đoạn đã chốt.'
            elif transcript and transcript['status'] in ('failed','interrupted'):
                title,description='Chép lời chưa hoàn tất','Âm thanh được giữ lại. Chép lời lại hoặc tiếp tục từ Thư viện.'
            elif self.audio_id:
                title,description='Sẵn sàng chép lời','Bắt đầu chép lời để xem nội dung Trung – Việt tại đây.'
            else:
                title,description='Chọn âm thanh để bắt đầu','Chọn file hoặc kéo thả âm thanh vào cửa sổ.'
            table.empty_title.setText(title)
            table.empty_description.setText(description)

    def load_waveform(self,audio):
        identifier=audio['id']
        if identifier in self.waveforms:
            self.file_page.seek_slider.peaks=self.waveforms[identifier]
            self.file_page.seek_slider.update(); return
        if identifier in self.waveform_pending: return
        self.waveform_pending.add(identifier)
        path=self.store.audio_path(identifier)
        def done(peaks):
            self.waveform_pending.discard(identifier); self.waveforms[identifier]=peaks
            if self.page=='file' and self.audio_id==identifier:
                self.file_page.seek_slider.peaks=peaks; self.file_page.seek_slider.update()
        def failed(message):
            self.waveform_pending.discard(identifier)
            if not self.waveform_cancel.is_set(): self.statusBar().showMessage('Không tải được dạng sóng. Vẫn có thể phát và tua âm thanh.')
        self.submit(lambda _:waveform_peaks(path,audio['duration'],cancel=self.waveform_cancel),done,busy=False,error_handler=failed)

    def refresh_player(self,*args):
        if self.page!='file' or not hasattr(self,'file_page'): return
        playing=self.player.playbackState()==QMediaPlayer.PlaybackState.PlayingState
        control=self.file_page.play_button
        control.set_playing(playing)
        control.setAccessibleName('Tạm dừng' if playing else 'Phát âm thanh')
        control.setToolTip(control.accessibleName())
        muted=self.audio_output.isMuted()
        control=self.file_page.volume_button
        control.setIcon(icon('volume-off' if muted else 'volume',self.colors['text'],24)); control.setIconSize(QSize(24,24))
        control.setAccessibleName('Bật âm thanh' if muted else 'Tắt âm thanh')
        control.setToolTip(control.accessibleName())
        if self.player.duration()>0:
            self.seek_slider.setMaximum(self.player.duration())
            self.file_page.duration_label.setText(timestamp(self.player.duration()/1000))

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
        for title,glyph,callback in (
            ('Tất cả âm thanh','library',lambda:self.library_page.show_all()),
            ('Nhập âm thanh mới','upload',self.choose_audio),
            ('Thùng rác','trash',lambda:self.navigate('trash')),
        ):
            control=button(title,callback); control.setProperty('library_nav',True)
            control.setProperty('library_selected',glyph=='library')
            control.setIcon(icon(glyph,self.colors['text'],20)); control.setIconSize(QSize(20,20))
            self.context_layout.addWidget(control)
            if glyph=='upload': self.library_import_action=control
        self.context_layout.addWidget(label('Mỗi nguồn chỉ lưu một lần. Các phiên bản cùng dùng âm thanh gốc.','muted',True))
        self.library_page=LibraryPage(self); self.content_layout.addWidget(self.library_page,1)
        self.refresh_library_state()

    def refresh_library_state(self):
        if self.page!='library' or not hasattr(self,'library_page'): return
        self.library_page.refresh_busy()
        self.library_import_action.setEnabled(not self.is_busy and not self.recording)

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
        create=button('Tạo bộ mới',self.new_glossary); create.setObjectName('glossary_new')
        create.setIcon(icon('plus',self.colors['text'],18)); create.setIconSize(QSize(18,18))
        self.context_layout.addWidget(create)
        self.glossary_sets=None
        if sets:
            self.glossary_sets=QListWidget(); self.glossary_sets.setObjectName('glossary_sets')
            self.glossary_sets.setSpacing(4); self.glossary_sets.setIconSize(QSize(18,18))
            self.glossary_sets.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.glossary_sets.setTextElideMode(Qt.TextElideMode.ElideMiddle)
            for item in sets:
                entry=QListWidgetItem(icon('book',self.colors['text'],18),item['name'])
                entry.setData(Qt.ItemDataRole.UserRole,item['id']); entry.setToolTip(item['name']); entry.setSizeHint(QSize(0,40))
                self.glossary_sets.addItem(entry)
                if item['id']==self.glossary_id: self.glossary_sets.setCurrentItem(entry)
            self.glossary_sets.currentItemChanged.connect(lambda current,previous:self.select_glossary(current.data(Qt.ItemDataRole.UserRole)) if current else None)
            self.context_layout.addWidget(self.glossary_sets)
        else:
            self.context_layout.addWidget(label('Các bộ đã lưu sẽ xuất hiện tại đây.','muted',True))
        entries=json.loads(chosen['entries']) if chosen else []
        self.glossary_page=GlossaryPage(self,chosen,entries)
        self.glossary_name=self.glossary_page.name; self.glossary_context=self.glossary_page.context; self.glossary_table=self.glossary_page.table
        self.content_layout.addWidget(self.glossary_page,1)
        self.glossary_clean=self.glossary_page.current_state(); self.glossary_page.refresh_state()

    def glossary_state(self):
        self.glossary_page.commit_editor()
        return self.glossary_page.current_state()

    def confirm_glossary_changes(self):
        if self.page!='prompts' or self.glossary_clean is None or self.glossary_state()==self.glossary_clean: return True
        choice=QMessageBox.question(self,'Thuật ngữ chưa lưu','Lưu thay đổi trước khi rời bộ thuật ngữ?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if choice==QMessageBox.StandardButton.Cancel: return False
        if choice==QMessageBox.StandardButton.Save: return self.save_glossary(refresh=False)
        self.glossary_clean=self.glossary_state(); return True

    def select_glossary(self,identifier):
        if not self.confirm_glossary_changes():
            if self.glossary_sets:
                self.glossary_sets.blockSignals(True)
                for i in range(self.glossary_sets.count()):
                    item=self.glossary_sets.item(i)
                    if item.data(Qt.ItemDataRole.UserRole)==self.glossary_id: self.glossary_sets.setCurrentItem(item); break
                self.glossary_sets.blockSignals(False)
            return
        self.glossary_id=identifier; self.navigate('prompts')

    def new_glossary(self):
        if not self.confirm_glossary_changes(): return
        name,ok=QInputDialog.getText(self,'Tạo bộ thuật ngữ','Tên bộ')
        if ok and name.strip(): self.glossary_id=self.store.save_glossary(name,'',[]); self.navigate('prompts')

    def save_glossary(self,*,refresh=True):
        self.glossary_page.commit_editor()
        entries=[]
        for i in range(self.glossary_table.rowCount()):
            entries.append({key:(self.glossary_table.item(i,j).text() if self.glossary_table.item(i,j) else '') for j,key in enumerate(['zh','vi','note'])})
        try:
            self.glossary_id=self.store.save_glossary(self.glossary_name.text(),self.glossary_context.toPlainText(),entries,self.glossary_id)
            self.store.set_setting('glossary_id',self.glossary_id); self.store.set_setting('context',self.glossary_context.toPlainText())
            self.glossary_clean=self.glossary_state()
            if refresh: self.navigate('prompts')
            else: self.glossary_page.refresh_state()
            self.statusBar().showMessage('Đã lưu bộ thuật ngữ.')
            return True
        except Exception as error: self.error(error); return False

    def show_settings(self):
        self.settings_page=SettingsPage(self); self.settings_page.add_navigation(self.context_layout)
        self.content_layout.addWidget(self.settings_page,1)

    def backup(self):
        try: self.statusBar().showMessage('Đã sao lưu: '+str(self.store.backup()))
        except Exception as error: self.error(error)

    def change_theme(self,index):
        position=self.scroll.verticalScrollBar().value() if self.page=='settings' else None
        self.store.set_setting('theme','dark' if index else 'light'); super().change_theme(index)
        if position is not None: QTimer.singleShot(0,lambda:self.scroll.verticalScrollBar().setValue(position) if self.page=='settings' else None)

    def choose_model_dir(self):
        path=QFileDialog.getExistingDirectory(self,'Thư mục chứa sensevoice / paraformer / vad',str(self.model_manager.root))
        if path:
            self.model_manager=ModelManager(path); self.store.set_setting('model_dir',path); self.navigate('settings')

    def install_model(self,key):
        if self.model_manager.ready(key): self.statusBar().showMessage('Mô hình đã sẵn sàng.'); return
        self.cancel_event.clear()
        self.submit(lambda progress:self.model_manager.install(key,progress,self.cancel_event),lambda _:self.navigate('settings'),lambda message:self.statusBar().showMessage(str(message)))

    def transcribe(self):
        if self.is_busy: self.error('Một tác vụ đang chạy. Hãy chờ hoặc dừng tác vụ trước.'); return
        if not self.audio_id: self.choose_audio(); return
        if self.recording: self.error('Hãy kết thúc phiên ghi âm trước.'); return
        source=self.store.one('SELECT status FROM transcripts WHERE id=?',(self.transcript_id,)) if self.transcript_id else None
        if self.models and not self.version_id and source and source['status']=='complete' and self.store.segments(self.transcript_id):
            self.translate(); return
        if self.transcript_id and self.store.segments(self.transcript_id):
            if QMessageBox.question(self,'Chép lời lại','Tạo bản chép lời mới? Các bản cũ được giữ nguyên.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes: return
        self.capture_options(); self.cancel_event.clear(); audio_id=self.audio_id
        if self.models:
            try: options=self.translation_options()
            except Exception as error: self.error(error); return
            known_models=list(self.models)
            translation_mode=self.store.setting('file_translation_mode','parallel')
            self.submit(lambda emit:transcribe_translate_job(self.store,self.model_manager,audio_id,options,
                emit,self.cancel_event,self.store.setting('asr_threads',4),known_models=known_models,translation_mode=translation_mode),
                self.file_pipeline_done,self.file_pipeline_event)
            return
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
        self.mic_select=ComboBox()
        devices=input_devices(); identity=self.store.setting('mic_device_identity')
        chosen=selected_input(identity,devices)
        self.mic_select.addItem('Chọn microphone…',None)
        selected=0
        for device in devices:
            name=device['name']+(' · '+device['hostapi'] if device['hostapi'] else '')
            self.mic_select.addItem(name,device)
            self.mic_select.setItemData(self.mic_select.count()-1,name,Qt.ItemDataRole.ToolTipRole)
            if device==chosen: selected=self.mic_select.count()-1
        self.mic_select.setCurrentIndex(selected)
        self.mic_select.setToolTip('Chọn đúng mic đang thu giọng nói. Tên và trình điều khiển được nhớ thay cho số thứ tự thiết bị.')
        if identity is not None and chosen is None:
            self.mic_select.setToolTip('Microphone đã lưu chưa kết nối hoặc không xác định được duy nhất. Hãy chọn lại mic; ứng dụng sẽ không tự đổi sang thiết bị khác.')
        self.field(self.context_layout,'Microphone',self.mic_select)
        self.options()
        self.live_page=LivePage(self); self.content_layout.addWidget(self.live_page,1)
        self.timeline=self.live_page.timeline; self.follow_live=self.live_page.follow
        self.record_button=self.live_page.record_button; self.pause_button=self.live_page.pause_button
        self.stop_button=self.live_page.stop_button; self.microphone_level=self.live_page.meter
        self.render_live()

    def refresh_live_state(self):
        if self.page!='live' or not hasattr(self,'live_page'): return
        recording=bool(self.recording); paused=recording and self.recording.paused
        seconds=self.recording.samples/16000 if recording else 0
        state=('Đang lưu…' if self.live_stopping else 'Tạm dừng' if paused else 'Đang ghi âm' if self.recording.samples else 'Chờ microphone') if recording else 'Đang xử lý…' if self.is_busy else 'Đang dừng'
        self.live_page.set_state(state,seconds,self.live_level,recording,paused,self.is_busy or self.live_stopping)
        for widget in [self.mic_select,*self.option_widgets]: widget.setEnabled(not recording and not self.is_busy)

    def start_recording(self):
        if self.is_busy or self.recording: self.error('Một tác vụ đang chạy.'); return
        if self.mic_select.currentData() is None: self.error('Hãy chọn microphone đang dùng để thu giọng nói.'); return
        self.capture_options(); device=self.mic_select.currentData()
        self.cancel_event.clear()
        self.live_segments=[]; self.live_interim=''; self.live_level=0; self.live_follow=True
        self.follow_live.setChecked(True); self.render_live()
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
            self.refresh_live_state()

    def pause_recording(self):
        if self.recording:
            try:
                self.recording.pause(); self.live_level=0; self.update_record_timer()
            except Exception as error: self.error(error)

    def stop_recording(self):
        if not self.recording or self.is_busy: return
        session=self.recording; self.live_stopping=True
        def done(result):
            self.recording=None; self.live_stopping=False; self.live_level=0; self.live_interim=''
            if self.record_timer: self.record_timer.stop()
            if not result.get('audio_id'):
                self.navigate('live'); self.error(result['warning']); return
            self.audio_id=result['audio_id']; self.transcript_id=result['transcript_id']; self.version_id=result.get('version_id')
            self.player.setSource(QUrl.fromLocalFile(str(self.store.audio_path(self.audio_id))))
            self.navigate('file')
            if result.get('warning'): self.error(result['warning'])
        def failed(message):
            self.live_stopping=False
            if session.closed.is_set():
                self.recording=None; self.live_level=0
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
        elif kind=='interim':
            self.live_interim=item.get('zh','')
            if self.page=='live': self.live_page.set_interim(self.live_interim)
            return
        elif kind=='warning': self.statusBar().showMessage(item['message']); return
        elif kind=='level':
            self.live_level=max(0,min(100,int(item.get('level',0))))
            if self.page=='live' and 'rms_dbfs' in item:
                self.microphone_level.setToolTip(f"Mức tín hiệu gốc: {item['rms_dbfs']:.1f} dBFS. Thang hiển thị theo âm lượng; âm thanh lưu không bị tăng giảm.")
            self.refresh_live_state(); return
        if self.page=='live': self.render_live()

    def render_live(self):
        if self.page!='live' or not hasattr(self,'live_page'): return
        self.live_page.set_segments(self.live_segments,self.store.setting('show_notes',False))
        self.live_page.set_interim(self.live_interim); self.refresh_live_state()
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
        elif job['kind']=='transcribe_translate': self.resume_translation(job['target'])

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
        if self.is_busy: self.error('Một tác vụ đang chạy. Hãy chờ hoặc dừng tác vụ trước.'); return
        if self.recording: self.error('Phiên ghi âm đang chạy; bản dịch trực tiếp được xử lý theo câu đã chốt.'); return
        if not self.transcript_id or not self.store.segments(self.transcript_id): self.error('Chép lời tiếng Trung trước khi dịch.'); return
        try: options=self.translation_options()
        except Exception as error: self.error(error); return
        source=self.store.one('SELECT status FROM transcripts WHERE id=?',(self.transcript_id,))
        if source['status']!='complete': self.error('Bản chép lời chưa đầy đủ. Chép lời lại hoặc phục hồi tác vụ trước khi dịch.'); return
        audio_id,transcript=self.audio_id,self.transcript_id; self.cancel_event.clear()
        known_models=list(self.models); translation_mode=self.store.setting('file_translation_mode','parallel')
        self.submit(lambda emit:transcribe_translate_job(self.store,self.model_manager,audio_id,options,
            emit,self.cancel_event,self.store.setting('asr_threads',4),transcript_id=transcript,
            known_models=known_models,translation_mode=translation_mode),self.file_pipeline_done,self.file_pipeline_event)

    def translation_progress(self,item):
        self.version_id=item['version_id']
        version=self.store.one('SELECT * FROM versions WHERE id=?',(self.version_id,)); self.transcript_id=version['transcript_id']
        if self.page=='file': self.fill_timeline()
        self.statusBar().showMessage(f"Đang dịch: {item['done']}/{item['total']} đoạn")

    def file_pipeline_event(self,item):
        self.file_pipeline_progress=item
        if item['type']=='started' and self.audio_id==item['audio_id']:
            self.transcript_id=item['transcript_id']; self.version_id=item['version_id']
        if not self.file_pipeline_timer.isActive(): self.file_pipeline_timer.start()

    def render_file_pipeline_progress(self):
        item=self.file_pipeline_progress
        if not item: return
        if self.page=='file' and self.audio_id==item['audio_id'] and self.version_id==item['version_id']:
            selector=self.file_page.versions
            if selector.findData(item['version_id'])<0:
                version=self.store.one('SELECT number,model FROM versions WHERE id=?',(item['version_id'],))
                selector.addItem(f"v{version['number']} · {version['model']}",item['version_id'])
            selector.setCurrentIndex(selector.findData(item['version_id']))
            self.fill_timeline()
        phase=f"Đang chép lời {timestamp(item['seconds'])}" if not item['asr_done'] else f"Đã chốt {item['recognized']} đoạn"
        translated=f"Đã dịch {item['translated']}/{item['recognized']} · Chờ {item['pending']} đoạn"
        if item.get('translation_mode')=='whole':
            translated='Chờ chép lời hoàn tất để dịch cả bài' if not item['asr_done'] else 'Đang dịch cả bài một lượt' if item['pending'] else f"Đã dịch {item['translated']}/{item['recognized']} đoạn"
        if item['translation_error']: translated=f"Dịch tạm dừng · {item['pending']} đoạn đã lưu để thử lại"
        self.statusBar().showMessage(phase+' · '+translated)

    def file_pipeline_done(self,result):
        self.file_pipeline_timer.stop(); self.file_pipeline_progress=None
        self.recovered=[job for job in self.recovered if not (job['kind']=='transcribe_translate' and job['target']==result['version_id'])]
        self.open_audio(result['audio_id'],result['version_id'])
        if result['cancelled']:
            self.statusBar().showMessage('Đã dừng. Các đoạn đã lưu được giữ; tiếp tục từ Thư viện khi cần.')
        elif result['warnings']:
            self.error('Các đoạn đã xử lý được giữ trong thư viện. Phần chưa hoàn tất: '+' · '.join(result['warnings'].values()))
        else:
            self.statusBar().showMessage('Đã chép lời và dịch xong.')

    def resume_translation(self,identifier):
        if self.is_busy: self.error('Một tác vụ đang chạy. Hãy chờ hoặc dừng tác vụ trước.'); return
        if self.recording: self.error('Hãy kết thúc ghi âm trước.'); return
        self.cancel_event.clear()
        version=self.store.one('SELECT * FROM versions WHERE id=?',(identifier,))
        paired=self.store.one("SELECT id FROM jobs WHERE kind='transcribe_translate' AND target=? LIMIT 1",(identifier,))
        if paired:
            known_models=list(self.models)
            self.submit(lambda emit:transcribe_translate_job(self.store,self.model_manager,version['audio_id'],None,
                emit,self.cancel_event,self.store.setting('asr_threads',4),version_id=identifier,known_models=known_models),
                self.file_pipeline_done,self.file_pipeline_event)
            return
        def work(progress):
            executable=find_codex(self.store.setting('codex_path')); actual=capabilities(executable,self.store.root/'work',self.cancel_event)
            return translate_version(self.store,executable,identifier,actual['models'],progress,self.cancel_event)
        self.submit(work,lambda _:self.open_audio(version['audio_id'],identifier),self.translation_progress)
    def cancel_work(self):
        self.cancel_event.set(); self.cancel_button.setEnabled(False); self.activity.setText('Đang dừng…')

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
        self.waveform_cancel.set()
        self.player.stop(); event.accept()
