"""Install, verify and uninstall this MSI in an isolated workspace directory."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import uuid
import warnings
import winreg
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def package_product_code(package):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        import msilib
    db = msilib.OpenDatabase(str(package), msilib.MSIDBOPEN_READONLY)
    view = db.OpenView("SELECT `Value` FROM `Property` WHERE `Property`='ProductCode'")
    view.Execute(None)
    result = view.Fetch().GetString(1)
    view.Close()
    return result


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--msi', type=Path, default=ROOT / 'dist/ChineseTranscriber-1.0.0-preview.1-win-x64.msi')
    args = parser.parse_args()
    package = args.msi.resolve()
    build = json.loads(package.with_suffix('.build-info.json').read_text(encoding='utf-8'))
    if digest(package) != build['sha256']:
        raise ValueError('Installer hash does not match build report')
    msi = ctypes.WinDLL('msi')
    msi.MsiQueryProductStateW.argtypes = [wintypes.LPCWSTR]
    msi.MsiQueryProductStateW.restype = ctypes.c_int
    product = build['product_code']
    if package_product_code(package) != product:
        raise ValueError('Installer product code does not match build report')
    if msi.MsiQueryProductStateW(product) != -1:
        raise RuntimeError('Product already exists; refusing to alter an existing installation')
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\ChineseTranscriber') as key:
            winreg.QueryValueEx(key, 'InstallDir')
    except FileNotFoundError:
        pass
    else:
        raise RuntimeError('An installer location is already registered; preserving it')
    work = ROOT / '.test-data/installer' / str(uuid.uuid4())
    work.mkdir(parents=True)
    installed = work / 'installed/ChineseTranscriber'
    menu = work / 'start-menu/ChineseTranscriber'
    report = dict(product_code=product, msi_sha256=build['sha256'], work_dir=str(work),
                  install_exit=None, uninstall_exit=None, ok=False)
    # Resolve the normal destination without installing into the real profile.
    msi.MsiSetInternalUI.argtypes = [wintypes.UINT, ctypes.c_void_p]
    msi.MsiSetInternalUI.restype = wintypes.UINT
    msi.MsiOpenPackageExW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.UINT)]
    msi.MsiDoActionW.argtypes = [wintypes.UINT, wintypes.LPCWSTR]
    msi.MsiGetTargetPathW.argtypes = [wintypes.UINT, wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    msi.MsiCloseHandle.argtypes = [wintypes.UINT]
    previous_ui = msi.MsiSetInternalUI(2, None)
    session = wintypes.UINT()
    try:
        assert msi.MsiOpenPackageExW(str(package), 0, ctypes.byref(session)) == 0
        for action in ('AppSearch', 'CostInitialize', 'FileCost', 'CostFinalize'):
            assert msi.MsiDoActionW(session.value, action) == 0, action
        buffer = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buffer))
        assert msi.MsiGetTargetPathW(session.value, 'INSTALLDIR', buffer, ctypes.byref(size)) == 0
        expected = Path(os.environ['LOCALAPPDATA']) / 'Programs/ChineseTranscriber'
        assert Path(buffer.value).resolve() == expected.resolve()
        report['default_install_dir_verified'] = True
    finally:
        if session.value:
            msi.MsiCloseHandle(session.value)
        msi.MsiSetInternalUI(previous_ui, None)
    msiexec = str(Path(os.environ['WINDIR']) / 'System32/msiexec.exe')
    installed_by_test = False

    def run_msi(arguments, log):
        # msiexec needs PROPERTY="path with spaces", not "PROPERTY=path with spaces".
        # Pass this directly to CreateProcess, without a command shell.
        encoded = []
        for argument in [msiexec, *arguments, '/qn', '/norestart', '/L*v', str(log)]:
            if '=' in argument and not argument.startswith('/'):
                name, value = argument.split('=', 1)
                if not name.isidentifier() or not name.isupper() or '"' in value:
                    raise ValueError('Invalid installer property')
                encoded.append(name + '="' + value + '"')
            else:
                encoded.append(subprocess.list2cmdline([argument]))
        completed = subprocess.run(' '.join(encoded), executable=msiexec,
                                   capture_output=True, timeout=300,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        return completed.returncode

    try:
        exit_code = run_msi(['/i', str(package), f'INSTALLDIR={installed}', f'APPSTARTMENU={menu}'], work / 'install.log')
        report['install_exit'] = exit_code
        installed_by_test = msi.MsiQueryProductStateW(product) in (1, 2, 5)
        if exit_code not in (0, 3010):
            report['status'] = 'blocked_by_policy' if exit_code == 1625 else 'installation_failed'
            return 2
        if not installed.is_relative_to(work) or not menu.is_relative_to(work):
            raise ValueError('Test installation escaped its workspace')
        for line in (installed / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            expected, relative = line.split('  ', 1)
            path = (installed / relative).resolve()
            if not path.is_relative_to(installed.resolve()) or digest(path) != expected:
                raise ValueError('Installed file mismatch: ' + relative)
        with zipfile.ZipFile(ROOT / 'dist/ChineseTranscriber-1.0.0-win-x64.zip') as archive:
            files = [name for name in archive.namelist() if not name.endswith('/')]
            assert all((installed / Path(name).relative_to('ChineseTranscriber')).is_file() for name in files)
        report['installed_files_verified'] = len(files)
        shortcut = menu / 'Chinese Transcriber.lnk'
        assert shortcut.is_file(), shortcut
        script = "$link=(New-Object -ComObject WScript.Shell).CreateShortcut($env:INSTALLER_TEST_SHORTCUT); [pscustomobject]@{target=$link.TargetPath;arguments=$link.Arguments;working_directory=$link.WorkingDirectory} | ConvertTo-Json -Compress"
        details = json.loads(subprocess.check_output(
            ['powershell', '-NoProfile', '-Command', script], text=True, encoding='utf-8',
            env=dict(os.environ, INSTALLER_TEST_SHORTCUT=str(shortcut)), timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW))
        assert Path(details['target']).resolve() == (installed / 'python/pythonw.exe').resolve()
        assert details['arguments'] == '"' + str(installed / 'launch.py') + '"'
        assert Path(details['working_directory']).resolve() == installed.resolve()
        report['start_menu_shortcut_verified'] = True
        library = work / 'test-library'
        launched = subprocess.run([details['target'], str(installed / 'launch.py'), '--smoke-test', '--data-dir', str(library)],
                                  cwd=details['working_directory'],
                                  env=dict(os.environ, QT_QPA_PLATFORM='offscreen', CHINESE_TRANSCRIBER_NO_PROBE='1'),
                                  capture_output=True, timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
        report['installed_launcher_exit'] = launched.returncode
        assert launched.returncode == 0, launched.stderr.decode(errors='replace')[-1000:]
        databases = list(library.glob('*.sqlite3'))
        assert databases
        with sqlite3.connect(databases[0]) as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        report['installed_library_integrity'] = 'ok'
        try:
            frozen = subprocess.run([str(installed / 'ChineseTranscriber.exe'), '--smoke-test', '--data-dir', str(work / 'frozen-library')],
                                    cwd=installed, env=dict(os.environ, QT_QPA_PLATFORM='offscreen', CHINESE_TRANSCRIBER_NO_PROBE='1'),
                                    capture_output=True, timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
            report['installed_exe_exit'] = frozen.returncode
            report['installed_exe_status'] = 'passed' if frozen.returncode == 0 else 'launch_failed'
        except OSError as error:
            report['installed_exe_status'] = 'blocked_by_windows_application_control' if getattr(error, 'winerror', None) == 4551 else 'launch_failed'
            report['installed_exe_winerror'] = getattr(error, 'winerror', None)
        keep = installed / 'keep-user-file.txt'
        keep.write_text('User-owned file must survive uninstall.\n', encoding='utf-8')
        report['status'] = 'installed_application_verified'
    finally:
        if installed_by_test:
            # Uninstall only the product installed by this run, never an existing product.
            assert installed.resolve().is_relative_to(work.resolve())
            report['uninstall_exit'] = run_msi(['/x', product], work / 'uninstall.log')
            report['product_unregistered'] = msi.MsiQueryProductStateW(product) == -1
            report['shortcut_removed'] = not (menu / 'Chinese Transcriber.lnk').exists()
            report['owned_executable_removed'] = not (installed / 'ChineseTranscriber.exe').exists()
            report['user_file_preserved'] = (installed / 'keep-user-file.txt').is_file()
            report['test_library_preserved'] = (work / 'test-library').is_dir()
            report['ok'] = bool(report.get('start_menu_shortcut_verified') and report.get('installed_launcher_exit') == 0
                                and report['uninstall_exit'] in (0, 3010) and report['product_unregistered']
                                and report['shortcut_removed'] and report['owned_executable_removed']
                                and report['user_file_preserved'] and report['test_library_preserved'])
            if report['ok']:
                report['status'] = 'passed'
        (work / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        summary = ROOT / '.test-data/installer/validation.json'
        summary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report))
    return 0 if report['ok'] else 2


if __name__ == '__main__':
    sys.exit(main())
