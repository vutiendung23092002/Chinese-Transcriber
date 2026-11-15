"""Keep FFmpeg diagnostics on Qt's native logging path, without Python callbacks."""
import os
from PySide6.QtCore import qInstallMessageHandler


def configure_multimedia_logging():
    # Qt 6.12's FFmpeg integration otherwise uses av_log_default_callback,
    # whose native stderr can retain a recycled Windows file handle under
    # output capture. Keep FFmpeg -> Qt before media init to avoid that path.
    # A Python Qt message handler is unsafe here: QMediaPlayer.play() can hold
    # the GIL while waiting for a native decoder that logs and waits for the
    # same GIL. Qt's native handler needs no Python lock (OutputDebugString
    # for windowed Windows launches, or the native Qt console sink).
    os.environ.setdefault('QT_FFMPEG_DEBUG', '1')
    qInstallMessageHandler(None)
