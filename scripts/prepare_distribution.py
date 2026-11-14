import argparse
import hashlib
from pathlib import Path
import shutil
import sys

parser=argparse.ArgumentParser(); parser.add_argument('--skip-models',action='store_true'); args=parser.parse_args()
root=Path(__file__).resolve().parents[1]; output=root/'dist/ChineseTranscriber'
if not (output/'ChineseTranscriber.exe').is_file(): raise SystemExit('Build EXE first')
if not args.skip_models:
    for folder in ('sensevoice','paraformer','vad'):
        source=root/'models'/folder
        if source.is_dir():
            destination=output/'models'/folder; destination.mkdir(parents=True,exist_ok=True)
            for path in source.iterdir():
                if path.is_file() and path.name!='test-zh.wav': shutil.copy2(path,destination/path.name)
for source in ('README.md','docs/USER_GUIDE.md','docs/TROUBLESHOOTING.md','docs/THIRD_PARTY.md','docs/VALIDATION.md','docs/CODEX_SETUP.md','docs/PACKAGING.md'):
    path=root/source
    if path.exists():
        target=output/source; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
licenses=output/'licenses'; licenses.mkdir(exist_ok=True)
python_license=Path(sys.base_prefix)/'LICENSE.txt'
if python_license.exists(): shutil.copy2(python_license,licenses/'Python-LICENSE.txt')
for path in (root/'assets/licenses').glob('*'):
    if path.is_file(): shutil.copy2(path,licenses/path.name)
checks=[]
for file in sorted(output.rglob('*')):
    if file.is_file() and file.name!='SHA256SUMS.txt':
        digest=hashlib.sha256()
        with file.open('rb') as handle:
            while block:=handle.read(1024*1024): digest.update(block)
        checks.append(digest.hexdigest()+'  '+file.relative_to(output).as_posix())
(output/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n',encoding='utf-8')
print(f'Portable folder ready: {output}')
