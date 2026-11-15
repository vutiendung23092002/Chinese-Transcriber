"""Compact Codex-style model picker and capability-backed effort slider."""
from PySide6.QtCore import Qt, Signal, QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QToolButton, QSlider, QMenu

from .codex import APPROVED_MODELS
from .file_page import ElidedLabel
from .theme import DARK, icon


EFFORT_NAMES = {'none':'None', 'minimal':'Minimal', 'low':'Low', 'medium':'Medium',
                'high':'High', 'xhigh':'Extra High', 'max':'Max', 'ultra':'Ultra'}


def effort_name(value):
    return EFFORT_NAMES.get(value, str(value or 'Chưa xác minh'))


def model_name(item):
    name = item.get('displayName', item['model'])
    normalize = lambda text: ''.join(c for c in text.lower() if c.isalnum())
    return next((x for x in APPROVED_MODELS if normalize(x) == normalize(name)), name)


class EffortSlider(QSlider):
    """Native slider semantics with discrete, click-to-select painted stops."""
    effortChanged = Signal(str)

    def __init__(self, colors, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.colors = colors
        self.steps = []
        self.valid = False
        self.setObjectName('reasoning_slider')
        self.setFixedHeight(36)
        self.setMinimumWidth(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName('Mức suy luận')
        self.valueChanged.connect(self._changed)

    def set_steps(self, steps, selected):
        self.steps = list(steps)
        self.valid = selected in self.steps
        self.blockSignals(True)
        self.setRange(0, max(0, len(self.steps)-1))
        self.setValue(self.steps.index(selected) if self.valid else 0)
        self.blockSignals(False)
        self.setEnabled(bool(self.steps))
        self.setAccessibleDescription('Mức hiện tại: '+effort_name(selected)+'. Các mức: '+', '.join(effort_name(x) for x in self.steps) if self.steps else 'Chưa có mức suy luận được xác nhận')
        self.setToolTip('Mức suy luận: '+effort_name(selected))
        self.update()

    def _changed(self, index):
        if self.steps:
            self.valid = True
            self.effortChanged.emit(self.steps[index])
            self.update()

    def select_index(self, index):
        if not self.isEnabled() or not self.steps:
            return
        index = max(0, min(len(self.steps)-1, index))
        if index == self.value() and not self.valid:
            self._changed(index)
        else:
            self.setValue(index)

    def stop_x(self, index):
        return 15 + (self.width()-30)*index/max(1, len(self.steps)-1)

    def index_at(self, x):
        return round(max(0, min(1, (x-15)/max(1, self.width()-30)))*max(0, len(self.steps)-1))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self.setSliderDown(True)
            self.select_index(self.index_at(event.position().x()))
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.isSliderDown():
            self.select_index(self.index_at(event.position().x()))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isSliderDown():
            self.select_index(self.index_at(event.position().x()))
            self.setSliderDown(False)
            event.accept()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Home, Qt.Key.Key_End):
            self.select_index(0 if key == Qt.Key.Key_Home else len(self.steps)-1)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Down, Qt.Key.Key_PageDown):
            self.select_index(self.value()-1 if self.valid else 0)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_PageUp):
            self.select_index(self.value()+1 if self.valid else 0)
        else:
            return super().keyPressEvent(event)
        event.accept()

    def wheelEvent(self, event):
        # Scrolling the page must not accidentally change translation settings.
        event.ignore()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = self.colors['bg'] == DARK['bg']
        accent = QColor('#B78BEB' if dark else '#9C69D7')
        track = QRectF(2, (self.height()-24)/2, self.width()-4, 24)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#50425E' if dark else '#E4D8F3'))
        p.drawRoundedRect(track, 12, 12)
        if self.valid and self.isEnabled():
            p.setBrush(accent)
            p.drawRoundedRect(QRectF(track.x(), track.y(), self.stop_x(self.value())+12-track.x(), 24), 12, 12)
        for i in range(len(self.steps)):
            p.setBrush(QColor('#EADDF8' if self.valid and i <= self.value() else '#9683AC'))
            p.drawEllipse(QPointF(self.stop_x(i), self.height()/2), 2.2, 2.2)
        if self.valid:
            p.setPen(QPen(QColor('#7841B8' if self.isEnabled() else self.colors['muted']), 2.5))
            p.setBrush(QColor('#FFFFFF' if self.isEnabled() else self.colors['soft']))
            p.drawEllipse(QPointF(self.stop_x(self.value()), self.height()/2), 13, 13)
        if self.hasFocus():
            p.setPen(QPen(QColor(self.colors['focus']), 1, Qt.PenStyle.DotLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 16, 16)


class ModelReasoningSelector(QFrame):
    selectionChanged = Signal()

    def __init__(self, models, model, effort, colors, parent=None):
        super().__init__(parent)
        self.models = list(models)
        self.colors = colors
        self.model_id = model or (self.models[0]['model'] if self.models else None)
        item = self.current_model()
        self.effort = effort if effort is not None else (item or {}).get('defaultReasoningEffort')
        self.setObjectName('model_reasoning_selector')
        self.setFixedHeight(116)
        self.setMinimumWidth(0)
        dark = colors['bg'] == DARK['bg']
        accent = '#D4B5FA' if dark else '#6528A7'
        self.setStyleSheet(f'''
            QFrame#model_reasoning_selector {{ background:{'#393044' if dark else '#F6F1FC'}; border:1px solid {colors['line']}; border-radius:16px; }}
            QLabel {{ background:transparent; border:none; font-family:"Inter"; }}
            QLabel#reasoning_value {{ color:{accent}; font-size:16px; font-weight:700; }}
            QLabel#model_name {{ color:{colors['muted']}; font-size:15px; font-weight:400; }}
            QPushButton#model_picker, QToolButton#reasoning_reset {{ background:transparent; border:0; padding:0; min-height:0; min-width:0; border-radius:6px; }}
            QPushButton#model_picker:hover, QToolButton#reasoning_reset:hover {{ background:{colors['lavender']}; }}
            QPushButton#model_picker:focus, QToolButton#reasoning_reset:focus {{ border:1px solid {colors['focus']}; }}
        ''')
        body = QVBoxLayout(self)
        body.setContentsMargins(10, 10, 10, 10)
        body.setSpacing(2)
        top = QHBoxLayout(); top.setSpacing(3)
        bolt = QLabel(); bolt.setFixedSize(24, 24); bolt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bolt.setPixmap(icon('bolt', colors['muted'], 18).pixmap(18, 18))
        self.effort_label = QLabel(); self.effort_label.setObjectName('reasoning_value')
        self.effort_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.effort_label.setMinimumWidth(0)
        self.reset_button = QToolButton(); self.reset_button.setObjectName('reasoning_reset')
        self.reset_button.setFixedSize(24, 24); self.reset_button.setIcon(icon('refresh', colors['muted'], 17))
        self.reset_button.setAccessibleName('Đặt mức suy luận về mặc định của model')
        self.reset_button.clicked.connect(self.reset_effort)
        top.addWidget(bolt); top.addWidget(self.effort_label, 1); top.addWidget(self.reset_button)
        body.addLayout(top)
        self.model_button = QPushButton(); self.model_button.setObjectName('model_picker')
        self.model_button.setFixedHeight(24); self.model_button.setCursor(Qt.CursorShape.PointingHandCursor)
        model_row = QHBoxLayout(self.model_button); model_row.setContentsMargins(4, 0, 4, 0); model_row.setSpacing(3)
        model_row.addStretch()
        self.model_label = ElidedLabel(''); self.model_label.setObjectName('model_name')
        self.model_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        model_row.addWidget(self.model_label)
        chevron = QLabel(); chevron.setFixedSize(12, 16); chevron.setPixmap(icon('chevron', colors['muted'], 12).pixmap(12, 12))
        chevron.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        model_row.addWidget(chevron); model_row.addStretch()
        body.addWidget(self.model_button)
        self.model_menu = QMenu(self)
        self.model_menu.setStyleSheet(f'''QMenu {{ background:{colors['panel']}; color:{colors['text']}; border:1px solid {colors['line']}; border-radius:12px; padding:6px; font-family:"Inter"; font-size:15px; }}
            QMenu::item {{ padding:9px 24px 9px 12px; border-radius:6px; }}
            QMenu::item:selected {{ background:{colors['lavender']}; }}
            QMenu::item:disabled {{ color:{colors['muted']}; }}''')
        self.model_button.clicked.connect(self.show_model_menu)
        body.addSpacing(8)
        self.effort_slider = EffortSlider(colors)
        self.effort_slider.effortChanged.connect(self.select_effort)
        body.addWidget(self.effort_slider)
        self.refresh()

    def current_model(self):
        return next((item for item in self.models if item['model'] == self.model_id), None)

    def supported_efforts(self):
        return list(dict.fromkeys(x['reasoningEffort'] for x in (self.current_model() or {}).get('supportedReasoningEfforts', [])))

    def refresh(self):
        item = self.current_model()
        supported = self.supported_efforts()
        name = model_name(item) if item else self.model_id or 'Chọn model'
        self.model_label.setText(name); self.model_label.setToolTip(name)
        self.fit_model_name()
        self.model_button.setAccessibleName('Chọn model: '+name)
        if item and self.effort in supported:
            title = effort_name(self.effort)
            detail = 'Mức suy luận: '+title
        elif not self.models:
            title, detail = 'Chưa xác minh', 'Kiểm tra kết nối Codex để đọc model và mức suy luận.'
        elif not item:
            title, detail = 'Không khả dụng', f'Model {name} không còn khả dụng. Chọn lại model; lựa chọn cũ được giữ.'
        else:
            title, detail = 'Không hỗ trợ', f'Mức {effort_name(self.effort)} không được model này hỗ trợ. Chọn một nấc để tiếp tục.'
        self.effort_label.setText(title); self.effort_label.setToolTip(detail)
        self.model_button.setToolTip(name if item else detail)
        self.effort_slider.set_steps(supported, self.effort)
        default = (item or {}).get('defaultReasoningEffort')
        self.reset_button.setEnabled(default in supported and default != self.effort)
        self.reset_button.setToolTip('Mức mặc định của model: '+effort_name(default))
        self.setAccessibleName('Mô hình & suy luận: '+name+' · '+detail)

    def fit_model_name(self):
        self.model_label.setFixedWidth(min(self.model_label.fontMetrics().horizontalAdvance(self.model_label.text())+2, max(0, self.width()-50)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_model_name()

    def select_model(self, identifier):
        item = next((x for x in self.models if x['model'] == identifier), None)
        if not item or identifier == self.model_id:
            return
        self.model_id = identifier
        self.effort = item.get('defaultReasoningEffort')
        self.refresh(); self.selectionChanged.emit()

    def select_effort(self, value):
        if value not in self.supported_efforts() or value == self.effort:
            return
        self.effort = value
        self.refresh(); self.selectionChanged.emit()

    def reset_effort(self):
        self.select_effort((self.current_model() or {}).get('defaultReasoningEffort'))

    def show_model_menu(self):
        self.model_menu.clear()
        for item in self.models:
            action = self.model_menu.addAction(model_name(item))
            action.setData(item['model']); action.setCheckable(True); action.setChecked(item['model'] == self.model_id)
            action.triggered.connect(lambda checked=False, identifier=item['model']: self.select_model(identifier))
        names = {''.join(c for c in x['displayName'].lower() if c.isalnum()) for x in self.models}
        unavailable = [name for name in APPROVED_MODELS if ''.join(c for c in name.lower() if c.isalnum()) not in names]
        if self.model_id and not self.current_model():
            unavailable.insert(0, self.model_id)
        if unavailable:
            if self.models: self.model_menu.addSeparator()
            for name in dict.fromkeys(unavailable):
                action = self.model_menu.addAction(name+' · Không khả dụng' if self.models else name+' · Chưa xác minh')
                action.setEnabled(False)
        self.model_menu.setMinimumWidth(max(260, self.width()))
        self.model_menu.popup(self.model_button.mapToGlobal(QPoint(0, self.model_button.height()+4)))
