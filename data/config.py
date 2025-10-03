import os, pygame

pygame.init()

# ================== ALAP KONFIG ==================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720
GRID_SIZE = 4
CELL_SIZE = 80
CHEESE_ROWS, CHEESE_COLS = 1, 2
CHEESE_OVERSIZE = -2
INVENTORY_START_X = 30
INVENTORY_START_Y = 100
INVENTORY_SPACING = 70

# Expert pénz rendszer
EXPERT_LEVEL_START_MONEY = {1: 200, 2: 250, 3: 300, 4: 500, 5: 500}
EXPERT_PIECE_COST = 10

# Színek / UI
COLOR_GRID_FILL = "#fff8dc"
COLOR_GRID_BORDER = "#b8860b"
COLOR_LEVEL_TEXT = "#ffcc00"
COLOR_BUTTON_BASE = "#ffcc00"
COLOR_BUTTON_HOVER = "white"
COLOR_RESET_BUTTON = "#ff6666"
COLOR_COMPLETION = (50, 200, 50)

# Kapcsolók
DEBUG_OVERLAY = False  # Ha True: cella indexek / debug info kirajzolása

# Fájl / Asset útvonalak
SAVE_DIR = "saves"
FONT_PATH = "assets/fonts/font.ttf"
BACKGROUND_IMAGE = "assets/images/cheese_BG.png"
MOUSE_IMAGE = "assets/images/mouse.png"
PLAY_BG_IMAGE = "assets/images/play_BG.png"
QUIT_BG_IMAGE = "assets/images/quit_BG.png"
MENU_MUSIC = "assets/sounds/menu_music.mp3"
COMPLETED_SOUND = "assets/sounds/completed.mp3"

os.makedirs(SAVE_DIR, exist_ok=True)

# Pygame alap
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brain Cheeser")

# Hangok / háttér
background = pygame.image.load(BACKGROUND_IMAGE)
menu_music = pygame.mixer.Sound(MENU_MUSIC)
completed_sound = pygame.mixer.Sound(COMPLETED_SOUND)

# Globális állapot
music_muted = False
