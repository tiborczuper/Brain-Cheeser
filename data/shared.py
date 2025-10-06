import pygame, json, os
from config import *

# ================== SHARED / UTIL ==================

def get_font(size:int):
    return pygame.font.Font(FONT_PATH, size)

def load_cheese_images():
    cheese_imgs = []
    num_cheese = 0
    while True:
        candidate = f"assets/images/cheese/SAJTLAP{num_cheese+1}.png"
        if os.path.exists(candidate):
            num_cheese += 1
        else:
            break
    if num_cheese == 0:
        print("[INIT WARNING] Nincs sajtlap")
    else:
        print(f"[INIT] {num_cheese} sajtlap betöltése")
    for i in range(1, num_cheese+1):
        img = pygame.image.load(f"assets/images/cheese/SAJTLAP{i}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (CHEESE_COLS*CELL_SIZE + CHEESE_OVERSIZE, CHEESE_ROWS*CELL_SIZE + CHEESE_OVERSIZE))
        cheese_imgs.append(img)
    return cheese_imgs

def init_cheese_inventory(cheese_imgs):
    cheese_rects = []
    cheese_angles = []
    cheese_used = []
    
    for i, img in enumerate(cheese_imgs):
        pos = get_cheese_inventory_position(i, cheese_imgs)
        cheese_rects.append(img.get_rect(topleft=pos))
        cheese_angles.append(0)
        cheese_used.append(False)
    return cheese_rects, cheese_angles, cheese_used

def get_cheese_inventory_position(cheese_index, cheese_imgs):
    """Kiszámolja az inventory pozíciót a sajt darab index alapján."""
    left_count = 4
    left_total_height = (left_count - 1) * INVENTORY_SPACING
    left_start_y = (SCREEN_HEIGHT - left_total_height) // 2 - 80
    
    if cheese_index < left_count:
        return (INVENTORY_START_X, left_start_y + cheese_index * INVENTORY_SPACING - CHEESE_OVERSIZE//2)
    else:
        right_count = len(cheese_imgs) - left_count
        right_total_height = (right_count - 1) * INVENTORY_SPACING
        right_start_y = (SCREEN_HEIGHT - right_total_height) // 2 - 80
        right_index = cheese_index - left_count
        right_x = SCREEN_WIDTH - cheese_imgs[cheese_index].get_width() - INVENTORY_START_X
        return (right_x, right_start_y + right_index * INVENTORY_SPACING - CHEESE_OVERSIZE//2)

def piece_cells(rect, angle, grid_origin, cell_size):
    rel_x = rect.x - grid_origin[0]
    rel_y = rect.y - grid_origin[1]
    col = rel_x // cell_size + 1
    row = rel_y // cell_size + 1
    if angle % 180 == 0:
        return {(row, col), (row, col+1)}
    return {(row, col), (row+1, col)}

def build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx=None):
    occ = set()
    for idx, pc in enumerate(placed_cheese):
        if exclude_idx is not None and idx == exclude_idx:
            continue
        occ |= piece_cells(pc['rect'], pc['angle'], grid_origin, cell_size)
    return occ

def draw_grid(screen, grid_size, cell_size, grid_origin):
    """Játéktábla kirajzolása."""
    for r in range(grid_size):
        for c in range(grid_size):
            rect = pygame.Rect(grid_origin[0] + c*cell_size, grid_origin[1] + r*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, COLOR_GRID_FILL, rect)
            pygame.draw.rect(screen, COLOR_GRID_BORDER, rect, 2)
            if DEBUG_OVERLAY:
                font = get_font(14)
                label = font.render(f"{r+1},{c+1}", True, (60,60,60))
                screen.blit(label, (rect.x+4, rect.y+4))

def draw_mice(screen, mice, grid_origin, cell_size):
    """Egerek kirajzolása a táblán."""
    mouse_img = pygame.image.load(MOUSE_IMAGE).convert_alpha()
    mouse_img = pygame.transform.smoothscale(mouse_img, (40, 40))
    for (a, b) in mice:
        (r1, c1), (r2, c2) = a, b
        x1 = grid_origin[0] + (c1-1)*cell_size + cell_size//2
        y1 = grid_origin[1] + (r1-1)*cell_size + cell_size//2
        x2 = grid_origin[0] + (c2-1)*cell_size + cell_size//2
        y2 = grid_origin[1] + (r2-1)*cell_size + cell_size//2
        center = ((x1+x2)//2, (y1+y2)//2)
        screen.blit(mouse_img, mouse_img.get_rect(center=center))
        if DEBUG_OVERLAY:
            font = get_font(16)
            txt = font.render("M", True, (200,50,50))
            screen.blit(txt, (center[0]-8, center[1]-8))

def draw_placement_preview(screen, mouse_pos, dragging_img, angle, grid_origin, cell_size, grid_size, placed_cheese, exclude_idx=None):
    """Draw a green preview of where the piece would be placed."""
    mx, my = mouse_pos
    cheese_cols, cheese_rows = CHEESE_COLS, CHEESE_ROWS
    w, h = (cheese_cols, cheese_rows) if angle % 180 == 0 else (cheese_rows, cheese_cols)
    
    # Calculate grid position based on mouse
    tmp = pygame.transform.rotate(dragging_img, angle)
    tmp_rect = tmp.get_rect(center=(mx, my))
    cx, cy = tmp_rect.center
    gx = int((cx - grid_origin[0]) / cell_size)
    gy = int((cy - grid_origin[1]) / cell_size)
    
    # Check if position is valid
    if 0 <= gx <= grid_size - w and 0 <= gy <= grid_size - h:
        sx = grid_origin[0] + gx * cell_size
        sy = grid_origin[1] + gy * cell_size
        preview_rect = pygame.Rect(sx, sy, w * cell_size, h * cell_size)
        
        # Check if placement is allowed
        test_rect = pygame.Rect(sx, sy, tmp.get_width(), tmp.get_height())
        if can_place_piece(test_rect, angle, placed_cheese, grid_origin, cell_size, grid_size, exclude_idx):
            # Draw green preview - valid placement
            pygame.draw.rect(screen, (0, 255, 0), preview_rect, 4)
            # Fill with semi-transparent green
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
            preview_surface.fill((0, 255, 0, 60))
            screen.blit(preview_surface, preview_rect.topleft)
        else:
            # Draw red preview - invalid placement
            pygame.draw.rect(screen, (255, 0, 0), preview_rect, 4)
            # Fill with semi-transparent red
            preview_surface = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
            preview_surface.fill((255, 0, 0, 60))
            screen.blit(preview_surface, preview_rect.topleft)

def img_index(img, cheese_imgs):
    for i, im in enumerate(cheese_imgs):
        if im == img:
            return i
    return -1

def matches_angle(req, ang):
    if isinstance(req, int):
        return (ang % 360) == (req % 360)
    if req == 'any-horizontal':
        return ang % 180 == 0
    if req == 'any-vertical':
        return ang % 180 == 90
    return False

def pattern_matches(pat, pc, cheese_imgs, grid_origin, cell_size):
    if 'cells' not in pat:
        return False
    idx = img_index(pc['img'], cheese_imgs)
    if idx != pat.get('img_index'):
        return False
    pc_cells = piece_cells(pc['rect'], pc['angle'], grid_origin, cell_size)
    if set(pat['cells']) != pc_cells:
        return False
    if not matches_angle(pat.get('angle', pc['angle']), pc['angle']):
        return False
    return True

def check_level_completion(placed_cheese, cheese_imgs, targets, grid_origin, cell_size):
    if not targets:
        return False
    groups = []
    for t in targets:
        if 'any_of' in t:
            groups.append(t['any_of'])
        else:
            groups.append([t])
    satisfied = [False]*len(groups)
    for gi, variants in enumerate(groups):
        if satisfied[gi]:
            continue
        for pc in placed_cheese:
            if pc.get('locked'):  # locked ne teljesítsen targetet
                continue
            for pat in variants:
                if pattern_matches(pat, pc, cheese_imgs, grid_origin, cell_size):
                    satisfied[gi] = True
                    break
            if satisfied[gi]:
                break
    return all(satisfied)

def can_place_piece(new_rect, angle, placed_cheese, grid_origin, cell_size, grid_size, exclude_idx=None):
    cells = piece_cells(new_rect, angle, grid_origin, cell_size)
    occ = build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx)
    if cells & occ:
        return False
    if not all(1 <= r <= grid_size and 1 <= c <= grid_size for (r, c) in cells):
        return False
    return True

# ================== GENERIKUS MENTÉS / BETÖLTÉS ==================

def serialize_pieces(placed_cheese, cheese_imgs):
    return [
        {
            'img_index': img_index(pc['img'], cheese_imgs),
            'x': pc['rect'].x,
            'y': pc['rect'].y,
            'angle': pc.get('angle', 0),
            'locked': pc.get('locked', pc.get('lock', False))
        } for pc in placed_cheese
    ]

def deserialize_pieces(raw_list, cheese_imgs):
    pieces = []
    for p in raw_list:
        idx = p.get('img_index', 0)
        if not (0 <= idx < len(cheese_imgs)):
            if not cheese_imgs:
                continue
            idx = 0
        img = cheese_imgs[idx]
        rect = img.get_rect(topleft=(p.get('x',0), p.get('y',0)))
        pieces.append({'img': img, 'rect': rect, 'angle': p.get('angle',0), 'locked': p.get('locked', False)})
    return pieces

def save_level_generic(path, current_level, placed_cheese, cheese_imgs):
    data = {
        'level': current_level,
        'pieces': serialize_pieces(placed_cheese, cheese_imgs)
    }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        print('[SAVE ERROR]', e)

def load_level_generic(path, cheese_imgs, default_level=1):
    if not os.path.exists(path):
        return default_level, []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        level = data.get('level', default_level)
        pieces = deserialize_pieces(data.get('pieces', []), cheese_imgs)
        return level, pieces
    except Exception as e:
        print('[LOAD ERROR]', e)
        return default_level, []

def apply_locked_specs(specs, placed_cheese, cheese_imgs, grid_origin, cell_size, warn_prefix='LOCK'):
    for spec in specs:
        idx = spec.get('img_index')
        if idx is None or not (0 <= idx < len(cheese_imgs)):
            continue
        angle = spec.get('angle', 0)
        cells = spec.get('cells')
        if not cells:
            print(f"[{warn_prefix} WARN] Spec without cells: {spec}")
            continue
        (r1,c1),(r2,c2) = cells
        top_r = min(r1,r2); left_c = min(c1,c2)
        x = grid_origin[0] + (left_c-1)*cell_size
        y = grid_origin[1] + (top_r-1)*cell_size
        # Figyelembe vesszük a forgatott kép méretét a rect létrehozásánál
        base_img = cheese_imgs[idx]
        rotated_img = pygame.transform.rotate(base_img, angle)
        rect = rotated_img.get_rect(topleft=(x,y))
        placed_cheese.append({'img': base_img, 'rect': rect, 'angle': angle, 'locked': True})
