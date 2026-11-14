# PyInstaller portable folder: native Qt modules only; weights stay outside the EXE.
from pathlib import Path
import imageio_ffmpeg
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, copy_metadata

root=Path(SPECPATH).parent
native=collect_dynamic_libs('sherpa_onnx')
native.append((imageio_ffmpeg.get_ffmpeg_exe(),'bin'))
data=[(str(root/'assets/fonts'),'assets/fonts'),(str(root/'assets/logo-concepts'),'assets/logo-concepts'),(str(root/'assets/icons'),'assets/icons')]
for package in ('PySide6','PySide6_Essentials','PySide6_Addons','shiboken6','numpy','cffi','pycparser','imageio-ffmpeg','attrs','referencing','rpds-py','typing_extensions','jsonschema','jsonschema_specifications','platformdirs','sounddevice','soundfile','sherpa_onnx','sherpa-onnx-core','psutil'):
    try: data+=copy_metadata(package)
    except Exception: pass
data+=collect_data_files('jsonschema_specifications')
data+=collect_data_files('_sounddevice_data',include_py_files=False)
data+=collect_data_files('licensing',include_py_files=False)
a=Analysis([str(root/'run.py')],pathex=[str(root/'src')],binaries=native,datas=data,
    hiddenimports=['sherpa_onnx.lib._sherpa_onnx','sounddevice','_cffi_backend','numpy','soundfile'],
    excludes=['PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','PySide6.QtWebEngineQuick','PySide6.QtPdf','PySide6.QtQuick','PySide6.QtQml','PySide6.Qt3DCore','scipy','matplotlib','pytest','IPython','tkinter'],noarchive=False)
# The imageio hook copies the same 100 MB executable; the runtime uses bin/.
a.binaries=[entry for entry in a.binaries if not entry[0].replace('\\','/').startswith('imageio_ffmpeg/binaries/ffmpeg')]
a.datas=[entry for entry in a.datas if not entry[0].replace('\\','/').startswith('imageio_ffmpeg/binaries/ffmpeg')]
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='ChineseTranscriber',debug=False,bootloader_ignore_signals=False,
    strip=False,upx=False,console=False,disable_windowed_traceback=False,icon=str(root/'assets/app.ico'))
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='ChineseTranscriber')
