@echo off
REM ============================================================
REM  Arma Reforger Mod Cleaner - EXE olusturucu
REM  Depo klasorunun icinde cift tikla. Gereken dosyalar:
REM    - reforger_mod_cleaner.py
REM    - assets\background.png
REM    - assets\icon.ico
REM    - requirements.txt
REM  (Bilgisayarda Python 3.9+ kurulu olmali: https://python.org)
REM ============================================================
setlocal
cd /d "%~dp0"

for %%F in (reforger_mod_cleaner.py assets\background.png assets\icon.ico requirements.txt) do (
    if not exist "%%F" (
        echo HATA: "%%F" bu klasorde yok. build.bat ile ayni klasorde olmali.
        pause
        exit /b 1
    )
)

set PY=py -3
%PY% --version >nul 2>&1 || set PY=python
%PY% --version >nul 2>&1 || (
    echo HATA: Python bulunamadi. https://python.org adresinden kur ve "Add to PATH" isaretle.
    pause
    exit /b 1
)

echo.
echo === Gerekli paketler kuruluyor ===
%PY% -m pip install --upgrade pip >nul
%PY% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo HATA: pip calismadi. Internet baglantisini kontrol et.
    pause
    exit /b 1
)

echo.
echo === EXE olusturuluyor ===
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "ReforgerModCleaner" ^
  --icon "assets\icon.ico" ^
  --add-data "assets\background.png;assets" ^
  --add-data "assets\icon.ico;assets" ^
  reforger_mod_cleaner.py

echo.
if exist "dist\ReforgerModCleaner.exe" (
    echo === BITTI! ===
    echo EXE konumu:  dist\ReforgerModCleaner.exe
) else (
    echo === Olusmadi. Yukaridaki hata mesajlarina bak. ===
)
pause
