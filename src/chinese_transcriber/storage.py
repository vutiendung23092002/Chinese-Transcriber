"""Transactional metadata, content-addressed audio and recoverable deletion."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import threading
import uuid
from platformdirs import user_data_dir

def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')

def uid():
    return uuid.uuid4().hex

class Store:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.environ.get('CHINESE_TRANSCRIBER_DATA') or user_data_dir('ChineseTranscriber',appauthor=False)).resolve()
        for name in ('audio','recordings','cache','backups','models','work'):
            (self.root/name).mkdir(parents=True,exist_ok=True)
        self.db_path = self.root/'library.sqlite3'
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS audio(
              id TEXT PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, filename TEXT NOT NULL,
              title TEXT NOT NULL, path TEXT NOT NULL UNIQUE, duration REAL NOT NULL DEFAULT 0,
              size INTEGER NOT NULL, source TEXT NOT NULL CHECK(source IN ('upload','live')),
              created TEXT NOT NULL, deleted TEXT);
            CREATE TABLE IF NOT EXISTS transcripts(
              id TEXT PRIMARY KEY, audio_id TEXT NOT NULL REFERENCES audio(id) ON DELETE CASCADE,
              engine TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, deleted TEXT);
            CREATE TABLE IF NOT EXISTS segments(
              id TEXT PRIMARY KEY, transcript_id TEXT NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
              ordinal INTEGER NOT NULL, start REAL NOT NULL CHECK(start>=0), end REAL NOT NULL,
              zh TEXT NOT NULL, timing TEXT NOT NULL DEFAULT 'speech-boundary',
              CHECK(end>=start), UNIQUE(transcript_id,ordinal));
            CREATE TABLE IF NOT EXISTS versions(
              id TEXT PRIMARY KEY, audio_id TEXT NOT NULL REFERENCES audio(id) ON DELETE CASCADE,
              transcript_id TEXT NOT NULL REFERENCES transcripts(id), number INTEGER NOT NULL,
              model TEXT NOT NULL, effort TEXT NOT NULL, context TEXT NOT NULL, glossary TEXT NOT NULL,
              status TEXT NOT NULL, created TEXT NOT NULL, deleted TEXT, UNIQUE(audio_id,number));
            CREATE TABLE IF NOT EXISTS translations(
              version_id TEXT NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
              segment_id TEXT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
              vi TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', status TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0, error TEXT NOT NULL DEFAULT '',
              PRIMARY KEY(version_id,segment_id));
            CREATE TABLE IF NOT EXISTS jobs(
              id TEXT PRIMARY KEY, kind TEXT NOT NULL, target TEXT NOT NULL, state TEXT NOT NULL,
              payload TEXT NOT NULL, error TEXT NOT NULL DEFAULT '', updated TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS glossaries(
              id TEXT PRIMARY KEY, name TEXT NOT NULL, context TEXT NOT NULL, entries TEXT NOT NULL,
              updated TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_versions_audio ON versions(audio_id);
            CREATE INDEX IF NOT EXISTS idx_transcripts_audio ON transcripts(audio_id);
            PRAGMA user_version=1;
            ''')

    def connect(self):
        db=sqlite3.connect(self.db_path,timeout=30)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        return db

    @contextmanager
    def transaction(self):
        with self.lock:
            db=self.connect()
            try:
                db.execute('BEGIN IMMEDIATE')
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                db.close()

    def rows(self, sql, args=()):
        with self.connect() as db:
            return [dict(row) for row in db.execute(sql,args)]

    def one(self, sql, args=()):
        items=self.rows(sql,args)
        return items[0] if items else None

    def setting(self,key,default=None):
        row=self.one('SELECT value FROM settings WHERE key=?',(key,))
        return json.loads(row['value']) if row else default

    def set_setting(self,key,value):
        with self.transaction() as db:
            db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value,ensure_ascii=False)))

    def import_audio(self, source: str | Path, duration=0.0, kind='upload', title=None):
        source=Path(source).resolve()
        if not source.is_file():
            raise ValueError('Không tìm thấy file âm thanh.')
        temp=self.root/'audio'/('.import-'+uid())
        digest=hashlib.sha256(); size=0
        try:
            with source.open('rb') as incoming,temp.open('xb') as outgoing:
                while chunk:=incoming.read(1024*1024):
                    digest.update(chunk); outgoing.write(chunk); size+=len(chunk)
                outgoing.flush(); os.fsync(outgoing.fileno())
            if not size:
                raise ValueError('File âm thanh rỗng.')
            sha=digest.hexdigest()
            with self.transaction() as db:
                existing=db.execute('SELECT * FROM audio WHERE sha256=?',(sha,)).fetchone()
                if existing:
                    return dict(existing),False
                suffix=source.suffix.lower()
                if len(suffix)>10 or not suffix[1:].isalnum(): suffix='.audio'
                relative=Path('audio')/(sha+suffix)
                dest=self.root/relative
                os.replace(temp,dest)
                record=dict(id=uid(),sha256=sha,filename=source.name,title=title or source.stem,
                    path=relative.as_posix(),duration=max(0,float(duration)),size=size,source=kind,created=now(),deleted=None)
                db.execute('INSERT INTO audio VALUES(:id,:sha256,:filename,:title,:path,:duration,:size,:source,:created,:deleted)',record)
            return record,True
        finally:
            temp.unlink(missing_ok=True)

    def audio_path(self,audio_id):
        row=self.one('SELECT * FROM audio WHERE id=?',(audio_id,))
        if not row: raise ValueError('Âm thanh không còn trong thư viện.')
        path=(self.root/row['path']).resolve()
        if not path.is_relative_to(self.root/'audio'):
            raise ValueError('Đường dẫn nguồn không hợp lệ.')
        return path

    def list_audio(self,deleted=False):
        condition='IS NOT NULL' if deleted else 'IS NULL'
        return self.rows(f'''SELECT a.*, (SELECT COUNT(*) FROM versions v WHERE v.audio_id=a.id AND v.deleted IS NULL) AS version_count,
          (SELECT COUNT(*) FROM transcripts t WHERE t.audio_id=a.id AND t.deleted IS NULL) AS transcript_count
          FROM audio a WHERE a.deleted {condition} ORDER BY a.created DESC''')

    def new_transcript(self,audio_id,engine,status='running'):
        with self.transaction() as db:
            row=db.execute('SELECT deleted FROM audio WHERE id=?',(audio_id,)).fetchone()
            if not row or row['deleted']: raise ValueError('Hãy khôi phục âm thanh trước.')
            identifier=uid()
            db.execute('INSERT INTO transcripts VALUES(?,?,?,?,?,NULL)',(identifier,audio_id,engine,status,now()))
        return identifier

    def append_segment(self,transcript_id,start,end,text,timing='speech-boundary',version_id=None):
        text=text.strip()
        if not text: return None
        with self.transaction() as db:
            previous=db.execute('SELECT ordinal,end FROM segments WHERE transcript_id=? ORDER BY ordinal DESC LIMIT 1',(transcript_id,)).fetchone()
            if previous and start<previous['end']-0.05: raise ValueError('Mốc thời gian bị chồng lấn.')
            ordinal=previous['ordinal']+1 if previous else 0
            identifier=uid()
            db.execute('INSERT INTO segments VALUES(?,?,?,?,?,?,?)',(identifier,transcript_id,ordinal,float(start),float(end),text,timing))
            if version_id:
                version=db.execute('SELECT transcript_id,deleted FROM versions WHERE id=?',(version_id,)).fetchone()
                if not version or version['deleted'] or version['transcript_id']!=transcript_id:
                    raise ValueError('Hàng đợi dịch không thuộc bản chép lời này.')
                db.execute("INSERT INTO translations(version_id,segment_id,status) VALUES(?,?,'queued')",(version_id,identifier))
        return identifier

    def queue_missing_translations(self,version_id):
        with self.transaction() as db:
            db.execute("""INSERT OR IGNORE INTO translations(version_id,segment_id,status)
                SELECT v.id,s.id,'queued' FROM versions v JOIN segments s ON s.transcript_id=v.transcript_id
                WHERE v.id=? AND v.deleted IS NULL""",(version_id,))

    def set_transcript_status(self,identifier,status):
        with self.transaction() as db:
            db.execute('UPDATE transcripts SET status=? WHERE id=?',(status,identifier))

    def latest_transcript(self,audio_id,complete_only=True):
        condition="AND status='complete'" if complete_only else ''
        return self.one(f'SELECT * FROM transcripts WHERE audio_id=? AND deleted IS NULL {condition} ORDER BY created DESC,rowid DESC LIMIT 1',(audio_id,))

    def segments(self,transcript_id,version_id=None):
        return self.rows('''SELECT s.*, COALESCE(t.vi,'') vi, COALESCE(t.note,'') note,
           COALESCE(t.status,'untranslated') translation_status, COALESCE(t.error,'') error
           FROM segments s LEFT JOIN translations t ON t.segment_id=s.id AND t.version_id=?
           WHERE s.transcript_id=? ORDER BY s.ordinal''',(version_id,transcript_id))

    def new_version(self,audio_id,transcript_id,model,effort,context,glossary):
        with self.transaction() as db:
            source=db.execute('SELECT deleted FROM audio WHERE id=?',(audio_id,)).fetchone()
            transcript=db.execute('SELECT * FROM transcripts WHERE id=? AND audio_id=?',(transcript_id,audio_id)).fetchone()
            if not source or source['deleted'] or not transcript or transcript['deleted']:
                raise ValueError('Nguồn hoặc bản chép lời không khả dụng.')
            number=db.execute('SELECT COALESCE(MAX(number),0)+1 FROM versions WHERE audio_id=?',(audio_id,)).fetchone()[0]
            identifier=uid()
            db.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?,NULL)',(identifier,audio_id,transcript_id,number,model,effort,context,json.dumps(glossary,ensure_ascii=False),'queued',now()))
            db.execute("INSERT INTO translations(version_id,segment_id,status) SELECT ?,id,'queued' FROM segments WHERE transcript_id=?",(identifier,transcript_id))
        return identifier

    def versions(self,audio_id,deleted=False):
        return self.rows('SELECT * FROM versions WHERE audio_id=? AND deleted '+('IS NOT NULL' if deleted else 'IS NULL')+' ORDER BY number DESC',(audio_id,))

    def translation_result(self,version_id,segment_id,text,note='',status='complete',error=''):
        with self.transaction() as db:
            count=db.execute('''UPDATE translations SET vi=?,note=?,status=?,error=?,attempts=attempts+1
              WHERE version_id=? AND segment_id=?''',(text,note,status,error,version_id,segment_id)).rowcount
            if count!=1: raise ValueError('ID đoạn dịch không thuộc phiên bản này.')

    def translation_results(self,version_id,results):
        """Commit a validated Codex response together; never save half a turn."""
        with self.transaction() as db:
            for item in results:
                count=db.execute("""UPDATE translations SET vi=?,note=?,status='complete',error='',attempts=attempts+1
                  WHERE version_id=? AND segment_id=?""",(item['vi'],item['note'],version_id,item['id'])).rowcount
                if count!=1: raise ValueError('ID đoạn dịch không thuộc phiên bản này.')

    def set_version_status(self,identifier,status):
        with self.transaction() as db:
            db.execute('UPDATE versions SET status=? WHERE id=?',(status,identifier))

    def deletion_stamp(self,db,audio_id):
        # A deletion group must be distinct even within one Windows clock tick.
        stamp=now()
        while db.execute('SELECT 1 FROM versions WHERE audio_id=? AND deleted=?',(audio_id,stamp)).fetchone():
            stamp=(datetime.fromisoformat(stamp)+timedelta(microseconds=1)).isoformat(timespec='microseconds')
        return stamp

    def trash_version(self,version_id,also_audio=False):
        with self.transaction() as db:
            row=db.execute('SELECT * FROM versions WHERE id=? AND deleted IS NULL',(version_id,)).fetchone()
            if not row: raise ValueError('Không tìm thấy bản dịch đang hoạt động.')
            stamp=self.deletion_stamp(db,row['audio_id'])
            remaining=db.execute('SELECT COUNT(*) FROM versions WHERE audio_id=? AND deleted IS NULL AND id<>?',(row['audio_id'],version_id)).fetchone()[0]
            if also_audio and remaining: raise ValueError('Âm thanh vẫn được bản dịch khác sử dụng.')
            db.execute('UPDATE versions SET deleted=? WHERE id=?',(stamp,version_id))
            if also_audio:
                db.execute('UPDATE audio SET deleted=? WHERE id=?',(stamp,row['audio_id']))

    def trash_audio(self,audio_id):
        with self.transaction() as db:
            stamp=self.deletion_stamp(db,audio_id)
            db.execute('UPDATE audio SET deleted=? WHERE id=? AND deleted IS NULL',(stamp,audio_id))
            # Preserve previously trashed versions' own timestamps/group membership.
            db.execute('UPDATE versions SET deleted=? WHERE audio_id=? AND deleted IS NULL',(stamp,audio_id))

    def restore_version(self,version_id):
        with self.transaction() as db:
            row=db.execute('SELECT audio_id FROM versions WHERE id=?',(version_id,)).fetchone()
            if not row: raise ValueError('Bản dịch đã bị xóa vĩnh viễn.')
            db.execute('UPDATE audio SET deleted=NULL WHERE id=?',(row['audio_id'],))
            db.execute('UPDATE versions SET deleted=NULL WHERE id=?',(version_id,))

    def restore_audio(self,audio_id):
        with self.transaction() as db:
            row=db.execute('SELECT deleted FROM audio WHERE id=?',(audio_id,)).fetchone()
            if not row: raise ValueError('Âm thanh đã bị xóa vĩnh viễn.')
            stamp=row['deleted']
            db.execute('UPDATE audio SET deleted=NULL WHERE id=?',(audio_id,))
            if stamp: db.execute('UPDATE versions SET deleted=NULL WHERE audio_id=? AND deleted=?',(audio_id,stamp))

    def purge_version(self,version_id):
        with self.transaction() as db:
            row=db.execute('SELECT deleted FROM versions WHERE id=?',(version_id,)).fetchone()
            if not row or not row['deleted']: raise ValueError('Chỉ xóa vĩnh viễn mục trong thùng rác.')
            db.execute('DELETE FROM versions WHERE id=?',(version_id,))

    def purge_audio(self,audio_id):
        with self.transaction() as db:
            row=db.execute('SELECT * FROM audio WHERE id=?',(audio_id,)).fetchone()
            if not row or not row['deleted']: raise ValueError('Chỉ xóa vĩnh viễn nguồn trong thùng rác.')
            if db.execute('SELECT COUNT(*) FROM versions WHERE audio_id=? AND deleted IS NULL',(audio_id,)).fetchone()[0]:
                raise ValueError('Còn bản dịch đang dùng âm thanh này.')
            # Metadata removal commits first. A crash leaves an orphan, never a dangling live record.
            path=self.audio_path(audio_id)
            db.execute('DELETE FROM versions WHERE audio_id=?',(audio_id,))
            db.execute('DELETE FROM audio WHERE id=?',(audio_id,))
        path.unlink(missing_ok=True)

    def save_glossary(self,name,context,entries,identifier=None):
        cleaned=[]; seen=set()
        for item in entries:
            zh=str(item.get('zh','')).strip(); vi=str(item.get('vi','')).strip()
            if not zh and not vi: continue
            if not zh or not vi or zh in seen: raise ValueError('Thuật ngữ cần đủ Trung/Việt và không trùng tiếng Trung.')
            seen.add(zh); cleaned.append(dict(zh=zh,vi=vi,note=str(item.get('note','')).strip()))
        identifier=identifier or uid()
        with self.transaction() as db:
            db.execute('INSERT INTO glossaries VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,context=excluded.context,entries=excluded.entries,updated=excluded.updated',
                (identifier,name.strip() or 'Bộ thuật ngữ',context,json.dumps(cleaned,ensure_ascii=False),now()))
        return identifier

    def job(self,kind,target,payload,identifier=None,state='running',error=''):
        identifier=identifier or uid()
        with self.transaction() as db:
            db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state,payload=excluded.payload,error=excluded.error,updated=excluded.updated',
                (identifier,kind,target,state,json.dumps(payload,ensure_ascii=False),error,now()))
        return identifier

    def recover_jobs(self):
        with self.transaction() as db:
            db.execute("UPDATE jobs SET state='interrupted',updated=? WHERE state='running'",(now(),))
            db.execute("UPDATE transcripts SET status='interrupted' WHERE status='running'")
            db.execute("UPDATE versions SET status='interrupted' WHERE status='running'")
            db.execute("UPDATE translations SET status='queued' WHERE status='translating'")
        return self.rows("SELECT * FROM jobs WHERE state='interrupted'")

    def backup(self):
        destination=self.root/'backups'/('library-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uid()[:6]+'.sqlite3')
        with self.connect() as incoming,sqlite3.connect(destination) as outgoing:
            incoming.backup(outgoing)
        return destination
