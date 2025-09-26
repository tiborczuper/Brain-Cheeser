@echo off
set PYTHONIOENCODING=utf-8
title Brain Cheeser
cd /d "%~dp0"

echo Pygame ellenorzese es telepitese...
python -c "import pygame" 2>nul || python -m pip install pygame

echo Jatek inditasa...
python main.py
pause