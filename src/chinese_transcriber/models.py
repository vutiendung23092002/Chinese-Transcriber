"""Verified, optional CPU models. Only int8 weights are downloaded."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tarfile
import urllib.request
from .audio import atomic_text

CATALOG={
 'sensevoice':dict(name='SenseVoiceSmall INT8',folder='sensevoice',
   url='https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2',
   sha256='7d1efa2138a65b0b488df37f8b89e3d91a60676e416f515b952358d83dfd347e',
   files=['model.int8.onnx','tokens.txt']),
 'paraformer':dict(name='Streaming Paraformer INT8',folder='paraformer',
   repo='csukuangfj/sherpa-onnx-streaming-paraformer-bilingual-zh-en',
   files=['encoder.int8.onnx','decoder.int8.onnx','tokens.txt']),
 'vad':dict(name='Silero VAD',folder='vad',
   url='https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx',files=['silero_vad.onnx']),
}

def request(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ChineseTranscriber/1.0'}),timeout=60)

def download(url,path,expected=None,progress=lambda x:None,cancel=None):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.part')
    digest=hashlib.sha256(); count=0
    try:
        with request(url) as response,temporary.open('wb') as handle:
            total=int(response.headers.get('Content-Length',0))
            while chunk:=response.read(1024*1024):
                if cancel and cancel.is_set(): raise InterruptedError('Đã dừng tải mô hình.')
                digest.update(chunk); handle.write(chunk); count+=len(chunk)
                progress(f'{path.name}: {count/1048576:.0f} MB'+(f' / {total/1048576:.0f} MB' if total else ''))
            handle.flush(); os.fsync(handle.fileno())
        if expected and digest.hexdigest()!=expected: raise ValueError('SHA-256 mô hình không khớp. File tải về không được sử dụng.')
        os.replace(temporary,path)
        return digest.hexdigest()
    finally:
        temporary.unlink(missing_ok=True)

class ModelManager:
    def __init__(self,root):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)

    def path(self,key): return self.root/CATALOG[key]['folder']

    def ready(self,key):
        return all((self.path(key)/filename).is_file() for filename in CATALOG[key]['files'])

    def install(self,key,progress=lambda x:None,cancel=None):
        config=CATALOG[key]; destination=self.path(key); destination.mkdir(parents=True,exist_ok=True)
        manifest={}
        if key=='sensevoice':
            archive=self.root/'sensevoice-int8.tar.bz2'
            download(config['url'],archive,config['sha256'],progress,cancel)
            try:
                with tarfile.open(archive,'r:bz2') as incoming:
                    for member in incoming.getmembers():
                        name=Path(member.name).name
                        if name not in config['files'] and not (member.name.endswith('test_wavs/zh.wav')): continue
                        if not member.isfile(): continue
                        output=destination/('test-zh.wav' if name=='zh.wav' else name)
                        handle=incoming.extractfile(member)
                        data=handle.read(); handle.close()
                        temporary=output.with_suffix(output.suffix+'.part'); temporary.write_bytes(data); os.replace(temporary,output)
                        manifest[output.name]=hashlib.sha256(data).hexdigest()
            finally: archive.unlink(missing_ok=True)
        elif key=='paraformer':
            with request('https://huggingface.co/api/models/'+config['repo']+'?blobs=true') as response:
                metadata=json.load(response)
            entries={x['rfilename']:x for x in metadata['siblings']}
            for filename in config['files']:
                expected=entries[filename].get('lfs',{}).get('sha256')
                manifest[filename]=download('https://huggingface.co/'+config['repo']+'/resolve/main/'+filename,destination/filename,expected,progress,cancel)
            download('https://huggingface.co/'+config['repo']+'/resolve/main/test_wavs/0.wav',destination/'test-zh.wav',progress=progress,cancel=cancel)
        else:
            # GitHub release asset metadata provides the checksum where published.
            with request('https://api.github.com/repos/k2-fsa/sherpa-onnx/releases/tags/asr-models') as response:
                release=json.load(response)
            item=next(x for x in release['assets'] if x['name']=='silero_vad.onnx')
            expected=(item.get('digest') or '').removeprefix('sha256:') or None
            manifest['silero_vad.onnx']=download(config['url'],destination/'silero_vad.onnx',expected,progress,cancel)
        atomic_text(destination/'manifest.json',json.dumps({'source':config,'checksums':manifest},ensure_ascii=False,indent=2))
        if not self.ready(key): raise ValueError('Mô hình chưa đủ file cần thiết.')
        return destination

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--root',default='models'); parser.add_argument('models',nargs='*',default=['sensevoice','paraformer','vad']); args=parser.parse_args()
    manager=ModelManager(args.root)
    for key in args.models:
        if not manager.ready(key):
            last=[-1]
            def report(text):
                import time
                if time.monotonic()-last[0]>5: print(text,flush=True); last[0]=time.monotonic()
            manager.install(key,report)
        print(key,manager.path(key),'ready',flush=True)
