@echo off
echo ========================================
echo Shila-Vision - EXE Builder
echo ========================================
echo.

REM Aktiviere venv
call venv\Scripts\activate.bat

REM Installiere PyInstaller falls nicht vorhanden
echo Installiere PyInstaller...
pip install pyinstaller

echo.
echo Prüfe ob alte .exe noch geöffnet ist...
taskkill /F /IM "Shila-Vision.exe" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starte Build-Prozess...
echo.

REM Führe PyInstaller aus
pyinstaller --name=Shila-Vision ^
    --onefile ^
    --windowed ^
    --add-data="Modeltagger;Modeltagger" ^
    --hidden-import=onnxruntime ^
    --hidden-import=scipy ^
    --hidden-import=PIL ^
    --hidden-import=numpy ^
    --hidden-import=PySide6 ^
    --hidden-import=tagger.local_model_loader ^
    --hidden-import=tagger.wd14_tagger ^
    --collect-all=onnxruntime ^
    --collect-all=scipy ^
    --exclude-module=wdtagger ^
    --noconfirm ^
    --clean ^
    main.py

echo.
echo ========================================
echo Build abgeschlossen!
echo Die .exe-Datei findest du im 'dist' Ordner.
echo ========================================
pause

