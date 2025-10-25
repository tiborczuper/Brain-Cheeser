#!/bin/bash
export PYTHONIOENCODING=utf-8

cd "$(dirname "$0")"

echo "Python keresése..."

PYTHON_CMD=""

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "Python3 megtalálva: $(which python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
    echo "Python megtalálva: $(which python)"
else
    echo "HIBA: Python nem található!"
    echo "Kérem telepítse a Python-t:"
    echo "- Mac: brew install python3 vagy python.org-ról"
    echo "- Linux: sudo apt install python3 python3-pip"
    read -p "Nyomjon Enter-t a kilépéshez..."
    exit 1
fi

echo "Python verzió: $($PYTHON_CMD --version)"

# Pip ellenőrzése és frissítése
echo "Pip ellenőrzése..."
$PYTHON_CMD -m pip --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Pip nem található, telepítés..."
    if command -v apt >/dev/null 2>&1; then
        sudo apt update && sudo apt install -y python3-pip
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3-pip
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S python-pip
    fi
fi

echo "Pip frissítése..."
$PYTHON_CMD -m pip install --upgrade pip --user

echo "Pygame ellenőrzése és telepítése..."
$PYTHON_CMD -c "import pygame; print('pygame version:', pygame.version.ver)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Pygame nem található, telepítés..."
    
    # Próbálkozás pygame-ce-vel
    echo "Pygame-ce telepítés user módban..."
    $PYTHON_CMD -m pip install pygame-ce --user
    
    if [ $? -ne 0 ]; then
        echo "Pygame-ce telepítés sikertelen, próbálkozás pygame-vel..."
        $PYTHON_CMD -m pip install pygame --user
        
        if [ $? -ne 0 ]; then
            echo "Pip telepítés sikertelen, rendszer csomagkezelő próbálása..."
            if command -v apt >/dev/null 2>&1; then
                sudo apt update && sudo apt install -y python3-pygame
            elif command -v yum >/dev/null 2>&1; then
                sudo yum install -y python3-pygame
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -S python-pygame
            else
                echo "HIBA: Nem sikerült a pygame telepítése!"
                echo "Próbálja meg manuálisan: $PYTHON_CMD -m pip install pygame --user"
                read -p "Nyomjon Enter-t a kilépéshez..."
                exit 1
            fi
        fi
    fi
    
    echo "Pygame telepítés befejezve!"
else
    echo "Pygame már telepítve van."
fi

echo "Játék indítása..."
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "A program hibával futott le."
    echo "Ellenőrizze hogy minden fájl a helyén van-e."
    read -p "Nyomjon Enter-t a kilépéshez..."
fi