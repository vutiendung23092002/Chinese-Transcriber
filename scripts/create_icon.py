import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import struct
from PySide6.QtCore import QByteArray,QBuffer,QIODevice
from PySide6.QtGui import QGuiApplication,QImage,QPainter
from PySide6.QtSvg import QSvgRenderer

root=Path(__file__).resolve().parents[1]
app=QGuiApplication([]); renderer=QSvgRenderer(str(root/'assets/logo-concepts/03-v2-voice-rhythm.svg'))
images=[]
for size in (16,24,32,48,64,128,256):
    image=QImage(size,size,QImage.Format.Format_ARGB32); image.fill(0)
    painter=QPainter(image); painter.setRenderHint(QPainter.RenderHint.Antialiasing); renderer.render(painter); painter.end()
    buffer=QBuffer(); buffer.open(QIODevice.OpenModeFlag.WriteOnly); image.save(buffer,'PNG'); images.append((size,bytes(buffer.data())))
header=struct.pack('<HHH',0,1,len(images)); offset=6+16*len(images); entries=[]
for size,data in images:
    entries.append(struct.pack('<BBBBHHII',size if size<256 else 0,size if size<256 else 0,0,0,1,32,len(data),offset)); offset+=len(data)
(root/'assets/app.ico').write_bytes(header+b''.join(entries)+b''.join(data for _,data in images))
print('Created approved application icon.')
