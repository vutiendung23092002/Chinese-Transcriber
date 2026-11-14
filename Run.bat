@echo off
cd /d "%~dp0"
if exist ".tools\python311\pythonw.exe" (
  start "" ".tools\python311\pythonw.exe" -m chinese_transcriber.app %*
  exit /b
)
if exist "dist\ChineseTranscriber\ChineseTranscriber.exe" (
  start "" "dist\ChineseTranscriber\ChineseTranscriber.exe" %*
  exit /b
)
echo Khong tim thay runtime. Xem README.md de cai dat tu source.
pause
