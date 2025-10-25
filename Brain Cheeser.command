#!/bin/bash

# Brain Cheeser - Cross-platform launcher (Mac & Linux)
export PYTHONIOENCODING=utf-8

cd "$(dirname "$0")"

echo "Brain Cheeser Game Starter"
echo "=========================="

echo "Python keresése..."

PYTHON_CMD=""
PYTHON_FOUND=false

# Python keresése többféle névvel
for cmd in python3 python python3.11 python3.10 python3.9; do
    if command -v $cmd >/dev/null 2>&1; then
        PYTHON_CMD=$cmd
        PYTHON_FOUND=true
        echo "✓ Python megtalálva: $(which $cmd)"
        echo "  Verzió: $($cmd --version)"
        break
    fi
done

# Ha nincs Python, telepítési útmutatás
if [ "$PYTHON_FOUND" = false ]; then
    echo "HIBA: Python nem található!"
    echo "Kérem telepítse a Python-t:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "- Mac: brew install python3 vagy letöltés python.org-ról"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "- Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "- CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "- Arch: sudo pacman -S python python-pip"
    fi
    read -p "Nyomjon Enter-t a kilépéshez..."
    exit 1
fi

# Pip ellenőrzése
echo "Pip ellenőrzése..."
$PYTHON_CMD -m pip --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Pip telepítése..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt >/dev/null 2>&1; then
            sudo apt install -y python3-pip
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y python3-pip
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S python-pip
        fi
    fi
fi

# Linux rendszer függőségek
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux rendszer függőségek ellenőrzése..."
    if command -v apt >/dev/null 2>&1; then
        sudo apt install -y python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev >/dev/null 2>&1
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3-devel SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel freetype-devel >/dev/null 2>&1
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --needed python sdl2 sdl2_image sdl2_mixer sdl2_ttf freetype2 >/dev/null 2>&1
    fi
fi

echo "Pygame ellenőrzése és telepítése..."
$PYTHON_CMD -c "import pygame" 2>/dev/null || {
    echo "Pygame telepítése..."
    
    # Többféle telepítési módszer próbálása
    PYGAME_INSTALLED=false
    
    # 1. User módban pygame-ce
    echo "  Pygame-ce telepítés..."
    $PYTHON_CMD -m pip install pygame-ce --user >/dev/null 2>&1
    $PYTHON_CMD -c "import pygame" >/dev/null 2>&1 && PYGAME_INSTALLED=true
    
    # 2. User módban pygame
    if [ "$PYGAME_INSTALLED" = false ]; then
        echo "  Pygame telepítés..."
        $PYTHON_CMD -m pip install pygame --user >/dev/null 2>&1
        $PYTHON_CMD -c "import pygame" >/dev/null 2>&1 && PYGAME_INSTALLED=true
    fi
    
    # 3. Sudo-val (ha user mód sikertelen)
    if [ "$PYGAME_INSTALLED" = false ]; then
        echo "  Pygame telepítése sudo-val..."
        sudo $PYTHON_CMD -m pip install pygame >/dev/null 2>&1
        $PYTHON_CMD -c "import pygame" >/dev/null 2>&1 && PYGAME_INSTALLED=true
    fi
    
    # 4. Rendszer csomagkezelő (Linux)
    if [ "$PYGAME_INSTALLED" = false ] && [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Rendszer csomagkezelő..."
        if command -v apt >/dev/null 2>&1; then
            sudo apt install -y python3-pygame >/dev/null 2>&1
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y python3-pygame >/dev/null 2>&1
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S python-pygame >/dev/null 2>&1
        fi
        $PYTHON_CMD -c "import pygame" >/dev/null 2>&1 && PYGAME_INSTALLED=true
    fi
    
    if [ "$PYGAME_INSTALLED" = false ]; then
        echo "HIBA: Pygame telepítése sikertelen!"
        read -p "Nyomjon Enter-t a kilépéshez..."
        exit 1
    fi
}

echo "✓ Pygame rendben"

echo "Játék indítása..."
cd data
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "A program hibával futott le."
    echo "Ellenőrizze hogy minden fájl a helyén van-e."
    read -p "Nyomjon Enter-t a kilépéshez..."
fi