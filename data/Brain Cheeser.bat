::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFC9dTg2+GGS5E7gZ5vzo0/yU4k4SUOcDWp3a07rDA+gW71bhZ6op125bpMofHx5MbS6iYw4zrH1+v2eKOYmVsACB
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFC9dTg2+GGS5E7gZ5vzo0/yU4k4SUOcDWp3a07rDA+gW71bhZ6op125bpMofHx5MbS6iYw4zrH1+lHaEPsnckAfkT1uM9AsHEms6gnvV7A==
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
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
%PYTHON_CMD% -c "import pygame" 2>nul || %PYTHON_CMD% -m pip install pygame

echo Jatek inditasa...
%PYTHON_CMD% main.py
pause