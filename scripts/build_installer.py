"""Build a per-user Windows MSI from the verified portable ZIP.

Build dependency: Windows Python 3.11/3.12 (stdlib msilib, removed in 3.13).
The installed application does not depend on msilib or a system Python.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid
import warnings
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/vutiendung23092002/Chinese-Transcriber'
UPGRADE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, REPOSITORY + '/windows-msi/per-user/x64')
INSTALLER_NAME = 'ChineseTranscriber-1.0.0-preview.1-win-x64.msi'


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def identifier(prefix, text):
    return prefix + hashlib.sha256(text.encode('utf-8')).hexdigest()[:28]


def guid(text):
    return '{' + str(uuid.uuid5(UPGRADE_NAMESPACE, text)).upper() + '}'


def short_filename(name, used):
    """Keep deterministic, collision-free 8.3 names alongside the original names."""
    index = 0
    suffix = Path(name).suffix[1:4].upper()
    while True:
        short = 'F' + hashlib.sha256((name + str(index)).encode('utf-8')).hexdigest()[:7].upper()
        if suffix:
            short += '.' + suffix
        if short not in used:
            used.add(short)
            return short + '|' + name
        index += 1


def add_location_search(db, msilib):
    """Remember custom install/shortcut locations for repair and uninstall."""
    msilib.add_data(db, 'RegLocator', [
        ('AppLocationSearch', 1, r'Software\ChineseTranscriber', 'InstallDir', 18),
        ('MenuLocationSearch', 1, r'Software\ChineseTranscriber', 'StartMenuDir', 18),
    ])
    msilib.add_data(db, 'AppSearch', [
        ('INSTALLDIR', 'AppLocationSearch'), ('APPSTARTMENU', 'MenuLocationSearch'),
    ])


def build_msi(payload: Path, output: Path, archive_digest: str):
    if sys.platform != 'win32' or sys.version_info >= (3, 13):
        raise RuntimeError('Build the MSI using Windows Python 3.11 or 3.12.')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        import msilib
        from msilib import schema, sequence, text

    info = json.loads((payload / 'BUILD-INFO.json').read_text(encoding='utf-8'))
    if sha256(payload / 'ChineseTranscriber.exe') != info['exe_sha256']:
        raise ValueError('Portable EXE does not match BUILD-INFO.json')
    files = sorted(path for path in payload.rglob('*') if path.is_file())
    if any('__pycache__' in path.parts or path.suffix in ('.sqlite3', '.pyc') for path in files):
        raise ValueError('Unexpected cache or private database in installer payload')
    product_code = guid('product:1.0.0-preview.1:' + info['exe_sha256'])
    upgrade_code = '{' + str(UPGRADE_NAMESPACE).upper() + '}'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.building.msi')
    if temporary.exists():
        raise FileExistsError(temporary)
    db = msilib.init_database(str(temporary), schema, 'Chinese Transcriber 1.0.0 Preview 1',
                             product_code, '1.0.0', 'Chinese Transcriber')
    summary = db.GetSummaryInformation(20)
    summary.SetProperty(msilib.PID_TEMPLATE, 'x64;1033')
    summary.SetProperty(msilib.PID_WORDCOUNT, 10)  # Compressed, per-user, no elevation.
    summary.SetProperty(msilib.PID_PAGECOUNT, 400)
    summary.SetProperty(msilib.PID_COMMENTS, 'Preview release. Live recording is incomplete.')
    summary.Persist()
    msilib.add_tables(db, sequence)
    msilib.add_data(db, 'ActionText', text.ActionText)
    msilib.add_data(db, 'UIText', text.UIText)
    msilib.add_data(db, 'Property', [
        ('UpgradeCode', upgrade_code), ('INSTALLLEVEL', '1'),
        ('LIMITUI', '1'), ('ARPNOMODIFY', '1'), ('REBOOT', 'ReallySuppress'),
        ('ARPURLINFOABOUT', REPOSITORY), ('ARPHELPLINK', REPOSITORY + '/issues'),
        ('ARPCOMMENTS', 'Preview release. Live recording is incomplete.'),
        ('ARPPRODUCTICON', 'AppIcon.ico'), ('REINSTALLMODE', 'amus'),
        ('SecureCustomProperties', 'OLDERPRODUCTS;NEWERPRODUCTFOUND'),
        ('PayloadSHA256', archive_digest), ('AppSourceCommit', info['source_commit']),
    ])
    # Run discovery before launch conditions; remove older installs transactionally.
    for table in ('InstallExecuteSequence', 'InstallUISequence'):
        view = db.OpenView(f"UPDATE `{table}` SET `Sequence`=25 WHERE `Action`='FindRelatedProducts'")
        view.Execute(None); view.Close()
    view = db.OpenView("UPDATE `InstallExecuteSequence` SET `Sequence`=1510 WHERE `Action`='RemoveExistingProducts'")
    view.Execute(None); view.Close()
    msilib.add_data(db, 'Upgrade', [
        (upgrade_code, None, '1.0.0', None, 513, None, 'OLDERPRODUCTS'),
        (upgrade_code, '1.0.0', None, None, 2, None, 'NEWERPRODUCTFOUND'),
    ])
    msilib.add_data(db, 'LaunchCondition', [
        ('VersionNT64', 'This package requires 64-bit Windows.'),
        ('NOT ALLUSERS', 'This package installs for the current user only.'),
        ('NOT NEWERPRODUCTFOUND', 'A newer Chinese Transcriber MSI is already installed.'),
    ])
    add_location_search(db, msilib)
    msilib.add_data(db, 'Directory', [
        ('TARGETDIR', None, 'SourceDir'), ('LocalAppDataFolder', 'TARGETDIR', '.'),
        ('UserPrograms', 'LocalAppDataFolder', 'Programs'),
        ('INSTALLDIR', 'UserPrograms', 'CHINET~1|ChineseTranscriber'),
        ('ProgramMenuFolder', 'TARGETDIR', '.'),
        ('APPSTARTMENU', 'ProgramMenuFolder', 'CHINET~1|Chinese Transcriber'),
    ])
    directories = {Path('.'): 'INSTALLDIR'}
    directory_short_names = {}
    for directory in sorted((p for p in payload.rglob('*') if p.is_dir()), key=lambda p: (len(p.parts), str(p))):
        relative = directory.relative_to(payload)
        parent = directories[relative.parent]
        logical = identifier('D', relative.as_posix())
        default = short_filename(directory.name, directory_short_names.setdefault(parent, set()))
        msilib.add_data(db, 'Directory', [(logical, parent, default)])
        directories[relative] = logical
    msilib.add_data(db, 'Feature', [
        ('MainFeature', None, 'Chinese Transcriber', 'Application, fonts and speech models', 1, 1, 'INSTALLDIR', 0)
    ])
    cab = msilib.CAB('payload.cab')
    short_names = {}
    for number, path in enumerate(files, 1):
        relative = path.relative_to(payload)
        file_id = identifier('F', relative.as_posix())
        component = identifier('C', relative.as_posix())
        registry_id = identifier('R', relative.as_posix())
        directory_id = directories[relative.parent]
        # HKCU registry key paths make every component explicitly per-user.
        msilib.add_data(db, 'Component', [(component, guid('component:' + relative.as_posix()), directory_id, 260, None, registry_id)])
        msilib.add_data(db, 'FeatureComponents', [('MainFeature', component)])
        msilib.add_data(db, 'Registry', [(registry_id, 1, r'Software\ChineseTranscriber\InstallerComponents', file_id, '#1', component)])
        filename = short_filename(path.name, short_names.setdefault(directory_id, set()))
        msilib.add_data(db, 'File', [(file_id, component, filename, path.stat().st_size, None, None, 512, number)])
        cab.append(str(path), path.name, file_id)
    shortcut_component = 'StartMenuComponent'
    msilib.add_data(db, 'Component', [(shortcut_component, guid('component:start-menu'), 'INSTALLDIR', 260, None, 'InstallLocation')])
    msilib.add_data(db, 'FeatureComponents', [('MainFeature', shortcut_component)])
    msilib.add_data(db, 'Registry', [('InstallLocation', 1, r'Software\ChineseTranscriber', 'InstallDir', '[INSTALLDIR]', shortcut_component)])
    msilib.add_data(db, 'Registry', [('StartMenuLocation', 1, r'Software\ChineseTranscriber', 'StartMenuDir', '[APPSTARTMENU]', shortcut_component)])
    msilib.add_data(db, 'Icon', [('AppIcon.ico', msilib.Binary(str(ROOT / 'assets/app.ico')))])
    msilib.add_data(db, 'Shortcut', [
        ('StartMenuShortcut', 'APPSTARTMENU', 'CHINET~1|Chinese Transcriber', shortcut_component,
         '[INSTALLDIR]python\\pythonw.exe', '"[INSTALLDIR]launch.py"', 'Chinese Transcriber', None, 'AppIcon.ico', 0, 1, 'INSTALLDIR'),
    ])
    # Windows Installer removes only owned files and empty directories; user data is preserved.
    msilib.add_data(db, 'CreateFolder', [(directory, shortcut_component) for directory in [*directories.values(), 'APPSTARTMENU']])
    db.Commit()
    print(json.dumps({'status': 'compressing_msi_payload', 'files': len(files), 'product_code': product_code}), flush=True)
    cab.commit(db)
    db.Commit()
    summary = None
    view = None
    db = None
    os.replace(temporary, output)
    digest = sha256(output)
    output.with_suffix(output.suffix + '.sha256').write_text(digest + '  ' + output.name + '\n', encoding='utf-8')
    report = dict(msi=str(output), bytes=output.stat().st_size, sha256=digest,
                  product_code=product_code, upgrade_code=upgrade_code, files=len(files),
                  payload_sha256=archive_digest, app_source_commit=info['source_commit'],
                  app_exe_sha256=info['exe_sha256'], per_user=True,
                  shortcut_target='python/pythonw.exe launch.py', live_recording_status='incomplete')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'dist/ChineseTranscriber-1.0.0-win-x64.zip')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / INSTALLER_NAME)
    args = parser.parse_args()
    archive = args.archive.resolve()
    digest = sha256(archive)
    checksum = archive.with_suffix(archive.suffix + '.sha256')
    if not checksum.is_file() or checksum.read_text(encoding='utf-8').split()[0] != digest:
        raise ValueError('Portable ZIP checksum is missing or does not match.')
    work = ROOT / 'build/msi' / str(uuid.uuid4())
    work.mkdir(parents=True)
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            target = (work / item.filename).resolve()
            if not target.is_relative_to(work.resolve()):
                raise ValueError('Unsafe archive member: ' + item.filename)
        bundle.extractall(work)
    payload = work / 'ChineseTranscriber'
    for line in (payload / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, relative = line.split('  ', 1)
        path = (payload / relative).resolve()
        if not path.is_relative_to(payload.resolve()) or sha256(path) != expected:
            raise ValueError('Payload checksum mismatch: ' + relative)
    report = build_msi(payload, args.output.resolve(), digest)
    report_path = args.output.with_suffix('.build-info.json')
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
