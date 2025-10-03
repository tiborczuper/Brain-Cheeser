import json, os, pygame
from config import *
from shared import *

# Globális sajtkép lista (egyszeri betöltés a modul importjakor)
CHEESE_IMAGES = load_cheese_images()

# ================== BEGINNER DATA ==================

BEGINNER_LEVEL_LOCKED_PIECES = {
    1: [
        { 'img_index': 1, 'cells': [(1,1),(1,2)], 'angle': 0 },
        { 'img_index': 3, 'cells': [(1,3),(1,4)], 'angle': 0 },
        { 'img_index': 6, 'cells': [(2,1),(3,1)], 'angle': 90 },
        { 'img_index': 5, 'cells': [(4,1),(4,2)], 'angle': 0 },
        { 'img_index': 2, 'cells': [(4,3),(4,4)], 'angle': 180 },
        { 'img_index': 4, 'cells': [(2,4),(3,4)], 'angle': 270 },
    ],
    2: [
        { 'img_index': 7, 'cells': [(2,2),(3,2)], 'angle': 90 },
        { 'img_index': 2, 'cells': [(3,3),(4,3)], 'angle': 90 },
    ],
    3: [
        { 'img_index': 5, 'cells': [(3,3),(4,3)], 'angle': 90 },
    ],
    4: [
        { 'img_index': 2, 'cells': [(1,1),(1,2)], 'angle': 0 }
    ],
    5: [
        { 'img_index': 4, 'cells': [(1,2),(1,3)], 'angle': 0 },
        { 'img_index': 5, 'cells': [(2,2),(2,3)], 'angle': 0 }
    ],
}

LEVEL_COMPLETION_TARGETS = {
    1: [
        { 'img_index': 0, 'cells': [(2,3),(3,3)], 'angle': 'any-vertical' },
        { 'img_index': 7, 'cells': [(2,2),(3,2)], 'angle': 90},
    ],
    2: [
        { 'img_index': 0, 'cells': [(1,1),(1,2)], 'angle': 'any-horizontal' },
        { 'img_index': 5, 'cells': [(1,3),(1,4)], 'angle': 0 },
        { 'img_index': 3, 'cells': [(2,1),(3,1)], 'angle': 'any-vertical' },
        { 'img_index': 1, 'cells': [(2,3),(2,4)], 'angle': 180 },
        { 'img_index': 6, 'cells': [(4,1),(4,2)], 'angle': 180 },
        { 'img_index': 4, 'cells': [(3,4),(4,4)], 'angle': 90 },
    ],
    3: [
        { 'img_index': 3, 'cells': [(1,1),(2,1)], 'angle': 'any-vertical' },
        { 'img_index': 1, 'cells': [(1,2),(1,3)], 'angle': 180 },
        { 'img_index': 2, 'cells': [(1,4),(2,4)], 'angle': 90 },
        { 'img_index': 7, 'cells': [(2,2),(2,3)], 'angle': 0 },
        { 'img_index': 4, 'cells': [(3,1),(3,2)], 'angle': 180 },
        { 'img_index': 6, 'cells': [(4,1),(4,2)], 'angle': 180 },
        { 'img_index': 0, 'cells': [(3,4),(4,4)], 'angle': 'any-vertical' },
    ],
    4: [
        { 'img_index': 0, 'cells': [(1,3),(2,3)], 'angle': 'any-vertical' },
        { 'img_index': 7, 'cells': [(1,4),(2,4)], 'angle': 270 },
        { 'img_index': 6, 'cells': [(2,1),(2,2)], 'angle': 180 },
        { 'img_index': 3, 'cells': [(3,1),(4,1)], 'angle': 'any-vertical' },
        { 'img_index': 4, 'cells': [(3,2),(4,2)], 'angle': 90 },
        { 'img_index': 5, 'cells': [(3,3),(4,3)], 'angle': 90 },
        { 'img_index': 1, 'cells': [(3,4),(4,4)], 'angle': 270 },
    ],
    5: [
        { 'img_index': 6, 'cells': [(1,1),(2,1)], 'angle': 90 },
        { 'img_index': 3, 'cells': [(1,4),(2,4)], 'angle': 'any-vertical' },
        { 'img_index': 2, 'cells': [(3,1),(3,2)], 'angle': 0 },
        { 'img_index': 7, 'cells': [(3,3),(3,4)], 'angle': 0 },
        { 'img_index': 1, 'cells': [(4,1),(4,2)], 'angle': 0 },
        { 'img_index': 0, 'cells': [(4,3),(4,4)], 'angle': 'any-horizontal' },
    ],
}

BEGINNER_LEVEL_COMPLETION_TARGETS = LEVEL_COMPLETION_TARGETS

#############################################
# EGÉR ELHELYEZÉS – EDGE INDEX ALAPÚ RENDSZER
#############################################
LEVEL_MOUSE_EDGE_INDICES = {
    1: [3,5,16,18],
    2: [5,6,11,16,23],
    3: [3,10,12,23,24],
    4: [3,14,18,23],
    5: [5,11,12],
}

EDGE_INDEX_MAP = {
    1: ((1,1),(1,2)), 2: ((1,2),(1,3)), 3: ((1,3),(1,4)),
    4: ((1,1),(2,1)), 5: ((1,2),(2,2)), 6: ((1,3),(2,3)), 7: ((1,4),(2,4)),
    8: ((2,1),(2,2)), 9: ((2,2),(2,3)), 10: ((2,3),(2,4)),
    11: ((2,1),(3,1)), 12: ((2,2),(3,2)), 13: ((2,3),(3,3)), 14: ((2,4),(3,4)),
    15: ((3,1),(3,2)), 16: ((3,2),(3,3)), 17: ((3,3),(3,4)),
    18: ((3,1),(4,1)), 19: ((3,2),(4,2)), 20: ((3,3),(4,3)), 21: ((3,4),(4,4)),
    22: ((4,1),(4,2)), 23: ((4,2),(4,3)), 24: ((4,3),(4,4)),
}

def _edge_index_to_cells(idx:int):
        return EDGE_INDEX_MAP[idx]

BEGINNER_LEVEL_MICE = {}
for lvl, edges in LEVEL_MOUSE_EDGE_INDICES.items():
    pairs = []
    for e in edges:
        try:
            a,b = _edge_index_to_cells(e)
            pairs.append((a,b))
        except Exception as err:
            print('[MOUSE EDGE ERROR]', err)
    BEGINNER_LEVEL_MICE[lvl] = pairs

# ================== BEGINNER HELPERS ==================

def get_beginner_locked_pieces(level):
    return BEGINNER_LEVEL_LOCKED_PIECES.get(level, [])

def get_beginner_completion_targets(level):
    return BEGINNER_LEVEL_COMPLETION_TARGETS.get(level, [])

def get_beginner_level_mice(level):
    return BEGINNER_LEVEL_MICE.get(level, [])

def apply_beginner_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size):
    apply_locked_specs(get_beginner_locked_pieces(level), placed_cheese, cheese_imgs, grid_origin, cell_size, warn_prefix='BEGINNER')

# Save / Load (kept separate for clarity, though structurally similar to expert)

BEGINNER_SAVE_FILE = os.path.join(SAVE_DIR, 'beginner_progress.json')

def save_beginner_level(current_level, placed_cheese):
    save_level_generic(BEGINNER_SAVE_FILE, current_level, placed_cheese, CHEESE_IMAGES)


def load_beginner_level():
    return load_level_generic(BEGINNER_SAVE_FILE, CHEESE_IMAGES, default_level=1)


def reset_beginner_level(level, cheese_imgs, grid_origin, cell_size):
    placed = []
    apply_beginner_locked_pieces(level, placed, cheese_imgs, grid_origin, cell_size)
    return placed
