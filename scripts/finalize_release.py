"""Archive the prepared portable folder and verify its content manifest."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'scripts/prepare_distribution.py')],check=True,cwd=root)
folder=root/'dist/ChineseTranscriber'
for line in (folder/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
    expected,relative=line.split('  ',1)
    if hashlib.file_digest((folder/relative).open('rb'),'sha256').hexdigest()!=expected: raise ValueError('Checksum mismatch: '+relative)
archive=root/'dist/ChineseTranscriber-1.0.0-win-x64.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as output:
    for path in sorted(folder.rglob('*')):
        if path.is_file(): output.write(path,path.relative_to(folder.parent))
with zipfile.ZipFile(archive) as source:
    if source.testzip(): raise ValueError('ZIP CRC check failed')
digest=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
print(json.dumps(dict(archive=str(archive),zip_mb=round(archive.stat().st_size/2**20,1),sha256=digest,manifest_verified=True)))
