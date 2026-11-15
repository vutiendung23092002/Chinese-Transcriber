from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess
import numpy as np
import soundfile as sf

def hidden_process():
    return {'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}

def ffmpeg():
    import sys
    if getattr(sys,'frozen',False):
        bundled=list((Path(sys._MEIPASS)/'bin').glob('ffmpeg*.exe'))
        if bundled: return str(bundled[0])
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def audio_info(path):
    try:
        info=sf.info(str(path))
        if not info.frames or not info.samplerate: raise ValueError('Âm thanh rỗng.')
        return info.duration
    except (sf.LibsndfileError,RuntimeError):
        proc=subprocess.run([ffmpeg(),'-hide_banner','-i',str(path)],capture_output=True,**hidden_process())
        text=proc.stderr.decode('utf-8',errors='replace')
        duration=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',text)
        if not duration or 'Audio:' not in text: raise ValueError('File không chứa âm thanh có thể đọc được.')
        return int(duration[1])*3600+int(duration[2])*60+float(duration[3])

def decoded_chunks(path,chunk_samples=1600,cancel=None):
    proc=subprocess.Popen([ffmpeg(),'-nostdin','-v','error','-i',str(path),'-vn','-ac','1','-ar','16000','-f','f32le','pipe:1'],
        stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,**hidden_process())
    try:
        while True:
            if cancel and cancel.is_set(): raise InterruptedError('Đã dừng chép lời; các đoạn trước vẫn được lưu.')
            data=proc.stdout.read(chunk_samples*4)
            if not data: break
            yield np.frombuffer(data,dtype='<f4').copy()
        if proc.wait()!=0: raise ValueError('FFmpeg không giải mã được toàn bộ âm thanh.')
    finally:
        if proc.poll() is None: proc.kill()
        proc.wait(); proc.stdout.close()

def timestamp(seconds):
    seconds=max(0,int(seconds)); hours,seconds=divmod(seconds,3600); minutes,seconds=divmod(seconds,60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}' if hours else f'{minutes:02d}:{seconds:02d}'


def waveform_peaks(path,duration,bins=240,cancel=None):
    """Bounded-memory amplitude envelope for the seek control, decoded off the UI thread."""
    block=max(512,int(max(1,duration)*16000/bins))
    return [float(np.max(np.abs(chunk))) for chunk in decoded_chunks(path,block,cancel)]

def atomic_text(path,text):
    path=Path(path); temp=path.with_name(path.name+'.'+__import__('uuid').uuid4().hex+'.tmp')
    try:
        with temp.open('x',encoding='utf-8',newline='\n') as handle:
            handle.write(text); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)

def export_txt(store,transcript_id,version_id,path,language='zh',timestamps=True):
    rows=store.segments(transcript_id,version_id)
    if not rows: raise ValueError('Chưa có nội dung để xuất.')
    if language=='vi' and any(row['translation_status']!='complete' for row in rows):
        raise ValueError('Bản dịch chưa đầy đủ. Hãy tiếp tục hoặc thử lại các đoạn lỗi trước khi xuất Việt TXT.')
    lines=[]
    for row in rows:
        text=row['zh'] if language=='zh' else row['vi']
        prefix=f"[{timestamp(row['start'])} – {timestamp(row['end'])}] " if timestamps else ''
        lines.append(prefix+text)
    atomic_text(path,'\n\n'.join(lines)+'\n')

