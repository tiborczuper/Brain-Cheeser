@echo off
set PYTHONIOENCODING=utf-8
title Brain Cheeser
cd /d "%~dp0"

echo Python keresese...

python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto :found_python
)

py --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto :found_python
)

if exist "C:\Python*\python.exe" (
    for /d %%i in ("C:\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_CMD="%%i\python.exe"
            goto :found_python
        )
    )
)

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
%PYTHON_CMD% -c "import pygame; print('pygame version:', pygame.version.ver)" 2>nul
if %errorlevel% neq 0 (
    echo Pygame nem talalhato, pygame-ce telepites...
    %PYTHON_CMD% -m pip install pygame-ce
    if %errorlevel% neq 0 (
        echo HIBA: Pygame-ce telepites sikertelen!
        echo Probalkozzon manualis telepitessel: python -m pip install pygame-ce
        pause
        exit /b 1
    )
    
    echo Pygame-ce telepites befejezve, ujra ellenorzes...
    %PYTHON_CMD% -c "import pygame; print('pygame version:', pygame.version.ver)" 2>nul
    if %errorlevel% neq 0 (
        echo HIBA: Pygame meg mindig nem elerheto a telepites utan!
        echo Probalkozzon manualis telepitessel: python -m pip install pygame-ce
        pause
        exit /b 1
    )
    echo Pygame-ce sikeresen telepitve!
) else (
    echo Pygame mar telepitve van.
)

echo Jatek inditasa...
%PYTHON_CMD% main.py
if %errorlevel% neq 0 (
    echo.
    echo A jatek hibával futott le.
    echo Ellenorizze hogy minden fajl a helyen van-e.
)
pause