import json, os, pygame
from config import *
from shared import *
from common import create_mice_from_edges

# Globális sajtkép lista
CHEESE_IMAGES = None

def get_cheese_images():
    global CHEESE_IMAGES
    if CHEESE_IMAGES is None:
        CHEESE_IMAGES = load_cheese_images()
    return CHEESE_IMAGES

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

# ================== BEGINNER EGEREK ==================

LEVEL_MOUSE_EDGE_INDICES = {
    1: [3,5,16,18],
    2: [5,6,11,16,23],
    3: [3,10,12,23,24],
    4: [3,14,18,23],
    5: [5,11,12],
}

BEGINNER_LEVEL_MICE = {}
for lvl, edges in LEVEL_MOUSE_EDGE_INDICES.items():
    BEGINNER_LEVEL_MICE[lvl] = create_mice_from_edges(edges)

# ================== BEGINNER FUNCTIONS ==================

def get_beginner_locked_pieces(level):
    return BEGINNER_LEVEL_LOCKED_PIECES.get(level, [])

def get_beginner_completion_targets(level):
    return BEGINNER_LEVEL_COMPLETION_TARGETS.get(level, [])

def get_beginner_level_mice(level):
    return BEGINNER_LEVEL_MICE.get(level, [])

def apply_beginner_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size):
    apply_locked_specs(get_beginner_locked_pieces(level), placed_cheese, cheese_imgs, grid_origin, cell_size, warn_prefix='BEGINNER')

# ================== SAVE / LOAD ==================

BEGINNER_SAVE_FILE = os.path.join(SAVE_DIR, 'beginner_progress.json')

def save_beginner_level(current_level, placed_cheese):
    # Save level with multi-level support like expert mode
    # Load existing data first to preserve other levels
    all_data = {}
    if os.path.exists(BEGINNER_SAVE_FILE):
        try:
            with open(BEGINNER_SAVE_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except:
            all_data = {}
    
    # Update data for current level
    level_data = {
        'pieces': serialize_pieces(placed_cheese, get_cheese_images())
    }
    
    all_data[str(current_level)] = level_data
    
    try:
        with open(BEGINNER_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f)
    except Exception as e:
        print('[BEGINNER SAVE ERROR]', e)

def load_beginner_level(level=None):
    # Load specific level or return highest completed level + pieces if level=None
    if not os.path.exists(BEGINNER_SAVE_FILE):
        return (1, []) if level is None else []
    
    try:
        with open(BEGINNER_SAVE_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # Check if this is old format (single level) or new format (multiple levels)
        if 'level' in all_data:
            # Old format - convert to new format and return
            old_level = all_data.get('level', 1)
            pieces = deserialize_pieces(all_data.get('pieces', []), get_cheese_images())
            if level is None:
                return old_level, pieces
            elif level == old_level:
                return pieces
            else:
                return []
        else:
            # New format
            if level is None:
                # Find the highest level with progress
                max_level = 1
                latest_pieces = []
                for level_str, level_data in all_data.items():
                    try:
                        level_num = int(level_str)
                        if level_num > max_level:
                            max_level = level_num
                            latest_pieces = deserialize_pieces(level_data.get('pieces', []), get_cheese_images())
                    except ValueError:
                        continue
                return max_level, latest_pieces
            else:
                # Load specific level
                level_data = all_data.get(str(level), {})
                return deserialize_pieces(level_data.get('pieces', []), get_cheese_images())
    except Exception as e:
        print('[BEGINNER LOAD ERROR]', e)
        return (1, []) if level is None else []
