"""Exercise the actual frozen executable, including packaged FFmpeg and Qt codecs."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from chinese_transcriber.audio import ffmpeg,hidden_process

base=Path(__file__).resolve().parents[1]
source_mode='--source' in sys.argv
portable_python='--portable-python' in sys.argv
root=base/('.test-data/portable-python' if portable_python else '.test-data/source-release' if source_mode else '.test-data/release'); root.mkdir(parents=True,exist_ok=True)
exe=base/'dist/ChineseTranscriber/ChineseTranscriber.exe'
launcher=[str(exe.parent/'python/python.exe'),str(exe.parent/'launch.py')] if portable_python else [sys.executable,'-m','chinese_transcriber.app'] if source_mode else [str(exe)]
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',CHINESE_TRANSCRIBER_NO_PROBE='1')
try:
    smoke=subprocess.run(launcher+['--smoke-test','--data-dir',str(root/'smoke')],cwd=root,env=env,capture_output=True,timeout=45,**hidden_process())
except OSError as error:
    report=dict(ok=False,source_mode=source_mode,status='blocked_by_windows_application_control' if getattr(error,'winerror',None)==4551 else 'launch_error',winerror=getattr(error,'winerror',None),message=str(error))
    report['exe_sha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
    (root/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report)); sys.exit(2)
if smoke.returncode: raise RuntimeError(f'Smoke test exit {smoke.returncode}')
source=base/'models/sensevoice/test-zh.wav'; reports=[]
for extension in ('wav','mp3','m4a'):
    audio=source
    if extension!='wav':
        audio=root/('mandarin.'+extension)
        subprocess.run([ffmpeg(),'-nostdin','-v','error','-y','-i',str(source),str(audio)],check=True,capture_output=True,**hidden_process())
    library=root/extension
    command=launcher+['--self-test-audio',str(audio),'--data-dir',str(library)]
    if extension=='wav': command.append('--self-test-codex')
    result=subprocess.run(command,cwd=root,env=env,capture_output=True,timeout=180,**hidden_process())
    path=library/'selftest-report.json'
    if not path.exists(): raise RuntimeError(f'{extension}: no report, exit {result.returncode}')
    report=json.loads(path.read_text(encoding='utf-8')); report['format']=extension; reports.append(report)
    if result.returncode or not report['ok']: raise RuntimeError(str(report))
files=list(exe.parent.rglob('*'))
browser=[str(path.relative_to(exe.parent)) for path in files if 'webengine' in path.name.lower()]
if browser: raise AssertionError('Browser dependency in native release: '+str(browser))
report=dict(ok=True,source_mode=source_mode,portable_python=portable_python,smoke_exit=smoke.returncode,native_no_webengine=True,formats=reports)
report['exe_sha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
(root/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
