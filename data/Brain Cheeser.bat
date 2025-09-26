@echo off
set PYTHONIOENCODING=utf-8
title Brain Cheeser
cd /d "%~dp0"

echo Python keresese...

REM Probaljuk meg a python parancsot
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM Probaljuk meg a py parancsot (Python Launcher)
py --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto :found_python
)

REM Probaljuk meg kozvetlenul a telepitesi helyekrol
if exist "C:\Python*\python.exe" (
    for /d %%i in ("C:\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_CMD="%%i\python.exe"
            goto :found_python
        )
    )
)

REM Ha meg mindig nem talaltuk, probaljuk az AppData-ban
if exist "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_CMD="%%i\python.exe"
            goto :found_python
        )
    )
)

echo HIBA: Python nem talalhato!
echo Kerem telepitse a Python-t a python.org oldalrol
echo es valassza ki a "Add Python to PATH" opciót a telepites soran.
pause
exit /b 1

:found_python
echo Python megtalalva: %PYTHON_CMD%

echo Pygame ellenorzese es telepitese...
%PYTHON_CMD% -c "import pygame" 2>nul || %PYTHON_CMD% -m pip install pygame

echo Jatek inditasa...
%PYTHON_CMD% main.py
pause