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

echo "Pygame ellenőrzése és telepítése..."
$PYTHON_CMD -c "import pygame" 2>/dev/null || {
    echo "Pygame telepítése..."
    $PYTHON_CMD -m pip install pygame --user || {
        echo "Pygame telepítése sudo-val..."
        sudo $PYTHON_CMD -m pip install pygame
    }
}

echo "Játék indítása..."
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "A program hibával futott le."
    echo "Ellenőrizze hogy minden fájl a helyén van-e."
    read -p "Nyomjon Enter-t a kilépéshez..."
fi