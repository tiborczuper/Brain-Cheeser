import json, os, pygame
from config import *
from shared import *

# Globális sajtkép lista (egyszeri betöltés a modul importjakor)
CHEESE_IMAGES = load_cheese_images()

# ================== EXPERT DATA ==================

EXPERT_LEVEL_LOCKED_PIECES = {
    1: [
        { 'img_index': 1, 'cells': [(1,2),(1,3)], 'angle': 180 },
        { 'img_index': 7, 'cells': [(1,4),(2,4)], 'angle': -90 },
    ],
    2: [
        { 'img_index': 4, 'cells': [(1,1),(1,2)], 'angle': 180 },
        { 'img_index': 2, 'cells': [(4,1),(4,2)], 'angle': 0 },
    ],
    3: [
        { 'img_index': 2, 'cells': [(2,2),(3,2)], 'angle': -90 },
    ],
    4: [

    ],
    5: [

    ],
}

LEVEL_COMPLETION_TARGETS = {
    1: [
        { 'img_index': 2, 'cells': [(1,1),(2,1)], 'angle': 90 },
        { 'img_index': 4, 'cells': [(2,2),(2,3)], 'angle': 0 },
        { 'img_index': 3, 'cells': [(3,1),(4,1)], 'angle': 'any-vertical' },
        { 'img_index': 5, 'cells': [(3,2),(3,3)], 'angle': 0 },
        { 'img_index': 0, 'cells': [(4,2),(4,3)], 'angle': 'any-horizontal' },
        { 'img_index': 6, 'cells': [(3,4),(4,4)], 'angle': -90 },
    ],
    2: [
        { 'img_index': 1, 'cells': [(2,1),(3,1)], 'angle': 90 },
        { 'img_index': 7, 'cells': [(2,2),(3,2)], 'angle': -90 },
        { 'img_index': 5, 'cells': [(1,3),(1,4)], 'angle': 0 },
        { 'img_index': 0, 'cells': [(2,3),(2,4)], 'angle': 'any-horizontal' },
        { 'img_index': 3, 'cells': [(3,3),(4,3)], 'angle': 'any-vertical' },
        { 'img_index': 6, 'cells': [(3,4),(4,4)], 'angle': -90 },
    ],
    3: [
        { 'img_index': 5, 'cells': [(1,1),(1,2)], 'angle': 0 },
        { 'img_index': 1, 'cells': [(2,1),(3,1)], 'angle': -90 },
        { 'img_index': 3, 'cells': [(4,1),(4,2)], 'angle': 'any-horizontal' },
        { 'img_index': 0, 'cells': [(1,3),(2,3)], 'angle': 'any-vertical' },
        { 'img_index': 7, 'cells': [(1,4),(2,4)], 'angle': -90 },
        { 'img_index': 4, 'cells': [(3,3),(4,3)], 'angle': -90 },
        { 'img_index': 6, 'cells': [(3,4),(4,4)], 'angle': -90 },

    ],
    4: [
        { 'img_index': 5, 'cells': [(1,1),(1,2)], 'angle': 0 },
        { 'img_index': 2, 'cells': [(1,3),(1,4)], 'angle': 180 },
        { 'img_index': 0, 'cells': [(2,1),(2,2)], 'angle': 'any-horizontal' },
        { 'img_index': 3, 'cells': [(3,1),(4,1)], 'angle': 'any-vertical' },
        { 'img_index': 6, 'cells': [(3,2),(4,2)], 'angle': -90 },
        { 'img_index': 7, 'cells': [(2,3),(3,3)], 'angle': 90 },
        { 'img_index': 1, 'cells': [(2,4),(3,4)], 'angle': -90 },
        { 'img_index': 4, 'cells': [(4,3),(4,4)], 'angle': 0 },
    ],
    5: [
        { 'img_index': 7, 'cells': [(1,1),(1,2)], 'angle': 0 },
        { 'img_index': 6, 'cells': [(1,3),(1,4)], 'angle': 0 },
        { 'img_index': 5, 'cells': [(2,1),(2,2)], 'angle': 0 },
        { 'img_index': 3, 'cells': [(2,3),(2,4)], 'angle': 'any-horizontal' },
        { 'img_index': 1, 'cells': [(3,1),(4,1)], 'angle': -90 },
        { 'img_index': 4, 'cells': [(3,2),(3,3)], 'angle': 0 },
        { 'img_index': 0, 'cells': [(4,2),(4,3)], 'angle': 'any-horizontal' },
        { 'img_index': 2, 'cells': [(3,4),(4,4)], 'angle': -90 },
    ],
}

EXPERT_LEVEL_COMPLETION_TARGETS = LEVEL_COMPLETION_TARGETS

#############################################
# EGÉR ELHELYEZÉS – EDGE INDEX ALAPÚ RENDSZER
#############################################

EDGE_INDEX_MAP = {
    1: ((1,1),(1,2)), 2: ((1,2),(1,3)), 3: ((1,3),(1,4)),
    4: ((1,1),(2,1)), 5: ((1,2),(2,2)), 6: ((1,3),(2,3)), 7: ((1,4),(2,4)),
    8: ((2,1),(2,2)), 9: ((2,2),(2,3)), 10: ((2,3),(2,4)),
    11: ((2,1),(3,1)), 12: ((2,2),(3,2)), 13: ((2,3),(3,3)), 14: ((2,4),(3,4)),
    15: ((3,1),(3,2)), 16: ((3,2),(3,3)), 17: ((3,3),(3,4)),
    18: ((3,1),(4,1)), 19: ((3,2),(4,2)), 20: ((3,3),(4,3)), 21: ((3,4),(4,4)),
    22: ((4,1),(4,2)), 23: ((4,2),(4,3)), 24: ((4,3),(4,4)),
}

LEVEL_MOUSE_EDGE_INDICES = {
    1: [3,12,14,18,19],
    2: [6,8,14,18,19,20],
    3: [3,4,9,14,16,22],
    4: [4,6,17,18],
    5: [2,4,10,19],
}

def _edge_index_to_cells(idx:int):
        return EDGE_INDEX_MAP[idx]

EXPERT_LEVEL_MICE = {}
for lvl, edges in LEVEL_MOUSE_EDGE_INDICES.items():
    pairs = []
    for e in edges:
        try:
            a,b = _edge_index_to_cells(e)
            pairs.append((a,b))
        except Exception as err:
            print('[MOUSE EDGE ERROR]', err)
    EXPERT_LEVEL_MICE[lvl] = pairs

# ================== EXPERT HELPERS ==================

def get_expert_locked_pieces(level):
    return EXPERT_LEVEL_LOCKED_PIECES.get(level, [])

def get_expert_completion_targets(level):
    return EXPERT_LEVEL_COMPLETION_TARGETS.get(level, [])

def get_expert_level_mice(level):
    return EXPERT_LEVEL_MICE.get(level, [])

def apply_expert_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size):
    apply_locked_specs(get_expert_locked_pieces(level), placed_cheese, cheese_imgs, grid_origin, cell_size, warn_prefix='EXPERT')

# Save / Load (kept separate for clarity, though structurally similar to beginner)

EXPERT_SAVE_FILE = os.path.join(SAVE_DIR, 'expert_progress.json')

def save_expert_level(current_level, placed_cheese, money=None, level_completed=False, game_over=False):
    # Save level with money and status information
    # Load existing data first to preserve other levels
    all_data = {}
    if os.path.exists(EXPERT_SAVE_FILE):
        try:
            with open(EXPERT_SAVE_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except:
            all_data = {}
    
    # Update data for current level
    level_data = {
        'pieces': serialize_pieces(placed_cheese, CHEESE_IMAGES),
        'level_completed': level_completed,
        'game_over': game_over
    }
    if money is not None:
        level_data['money'] = money
    
    all_data[str(current_level)] = level_data
    
    try:
        with open(EXPERT_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f)
    except Exception as e:
        print('[EXPERT SAVE ERROR]', e)


def load_expert_level(level):
    # Load level with money and status information for specific level
    if not os.path.exists(EXPERT_SAVE_FILE):
        return level, [], None, False, False
    
    try:
        with open(EXPERT_SAVE_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # Check if this is old format (single level) or new format (multiple levels)
        if 'level' in all_data:
            # Old format - convert to new format
            old_level = all_data.get('level', 1)
            if old_level == level:
                pieces = deserialize_pieces(all_data.get('pieces', []), CHEESE_IMAGES)
                money = all_data.get('money', None)
                level_completed = all_data.get('level_completed', False)
                game_over = all_data.get('game_over', False)
                return level, pieces, money, level_completed, game_over
            else:
                return level, [], None, False, False
        else:
            # New format - load specific level
            level_data = all_data.get(str(level), {})
            pieces = deserialize_pieces(level_data.get('pieces', []), CHEESE_IMAGES)
            money = level_data.get('money', None)
            level_completed = level_data.get('level_completed', False)
            game_over = level_data.get('game_over', False)
            return level, pieces, money, level_completed, game_over
    except Exception as e:
        print('[EXPERT LOAD ERROR]', e)
        return level, [], None, False, False


def reset_expert_level(level, cheese_imgs, grid_origin, cell_size):
    placed = []
    apply_expert_locked_pieces(level, placed, cheese_imgs, grid_origin, cell_size)
    return placed
