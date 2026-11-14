"""Add a source launcher using the official PSF runtime, alongside the EXE.

This does not change Windows policy or modify/sign the blocked executable.
"""
from importlib.metadata import distribution
from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
output=root/'dist/ChineseTranscriber'
runtime=root/'.tools/python311'
if not (runtime/'python311.zip').is_file(): raise SystemExit('Official PSF embeddable Python runtime is required for this optional launcher')
if not (output/'_internal').is_dir(): raise SystemExit('Build the PyInstaller folder first')
target=output/'python'; target.mkdir(exist_ok=True)
for path in runtime.iterdir():
    if path.is_file() and path.name!='python311._pth': shutil.copy2(path,target/path.name)
(target/'python311._pth').write_text('python311.zip\n.\n../_internal\n../src\nimport site\n',encoding='utf-8')
packages=('PySide6_Essentials','PySide6_Addons','shiboken6','numpy','cffi','pycparser','imageio-ffmpeg','attrs','referencing','rpds-py','typing_extensions','jsonschema','jsonschema_specifications','platformdirs','sounddevice','soundfile','sherpa-onnx','sherpa-onnx-core','psutil')
for name in packages:
    package=distribution(name)
    for entry in package.files or []:
        if entry.suffix!='.py' or '..' in entry.parts or any(part.endswith('.dist-info') for part in entry.parts): continue
        source=Path(package.locate_file(entry)); destination=output/'_internal'/str(entry)
        if source.is_file(): destination.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,destination)
shutil.copytree(root/'src/chinese_transcriber',output/'src/chinese_transcriber',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for folder in ('fonts','logo-concepts'):
    shutil.copytree(root/'assets'/folder,output/'assets'/folder,dirs_exist_ok=True)
(output/'launch.py').write_text('''import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent
native=root/'_internal'
handles=[]
if hasattr(os,'add_dll_directory'):
    for relative in ('','PySide6','shiboken6','numpy.libs','sherpa_onnx/lib'):
        path=native/relative
        if path.is_dir(): handles.append(os.add_dll_directory(str(path)))
ffmpeg=next((native/'bin').glob('ffmpeg*.exe'),None)
if ffmpeg: os.environ['IMAGEIO_FFMPEG_EXE']=str(ffmpeg)
os.environ.setdefault('QT_PLUGIN_PATH',str(native/'PySide6/plugins'))
from chinese_transcriber.app import main
sys.exit(main())
''',encoding='utf-8')
(output/'Run.bat').write_text('@echo off\ncd /d "%~dp0"\nstart "" "python\\pythonw.exe" "launch.py" %*\n',encoding='ascii')
print('Added official Python source launcher: dist/ChineseTranscriber/Run.bat')
