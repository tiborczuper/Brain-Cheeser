import pygame, sys, json, os
from assets.button import Button

pygame.init()

# ================== KONSTANSOK ==================
# Képernyő beállítások
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720

# Játék beállítások
GRID_SIZE = 4
CELL_SIZE = 80
CHEESE_ROWS, CHEESE_COLS = 1, 2
CHEESE_OVERSIZE = -2

# Fájl útvonalak
SAVE_DIR = "saves"
FONT_PATH = "assets/fonts/font.ttf"
BACKGROUND_IMAGE = "assets/images/cheese_BG.jpeg"
MOUSE_IMAGE = "assets/images/mouse.png"
PLAY_BG_IMAGE = "assets/images/play_BG.png"
QUIT_BG_IMAGE = "assets/images/quit_BG.png"
MENU_MUSIC = "assets/sounds/menu_music.mp3"
COMPLETED_SOUND = "assets/sounds/completed.mp3"

# Színek
COLOR_GRID_FILL = "#fff8dc"
COLOR_GRID_BORDER = "#b8860b"
COLOR_LEVEL_TEXT = "#ffcc00"
COLOR_BUTTON_BASE = "#ffcc00"
COLOR_BUTTON_HOVER = "white"
COLOR_RESET_BUTTON = "#ff6666"
COLOR_COMPLETION = (50, 200, 50)

# Inventory pozíciók
INVENTORY_START_X = 30
INVENTORY_START_Y = 100
INVENTORY_SPACING = 70

# ================== GLOBÁLIS OBJEKTUMOK ==================
os.makedirs(SAVE_DIR, exist_ok=True)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brain Cheeser")

background = pygame.image.load(BACKGROUND_IMAGE)
menu_music = pygame.mixer.Sound(MENU_MUSIC)
completed_sound = pygame.mixer.Sound(COMPLETED_SOUND)

# ================== UTILITY FÜGGVÉNYEK ==================

def get_font(size:int):
    """Betűtípus betöltése a megadott méretben."""
    return pygame.font.Font(FONT_PATH, size)

def load_cheese_images():
    """Dinamikusan betölti az összes elérhető sajtlap képet."""
    cheese_imgs = []
    num_cheese = 0
    while True:
        candidate = f"assets/images/cheese/SAJTLAP{num_cheese+1}.png"
        if os.path.exists(candidate):
            num_cheese += 1
        else:
            break
    
    if num_cheese == 0:
        print("[INIT WARNING] Nem találhatóak SAJTLAP képek (assets/images/cheese/SAJTLAP*.png)")
    else:
        print(f"[INIT] {num_cheese} sajtlap betöltése")
    
    for i in range(1, num_cheese+1):
        img = pygame.image.load(f"assets/images/cheese/SAJTLAP{i}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (CHEESE_COLS*CELL_SIZE + CHEESE_OVERSIZE, CHEESE_ROWS*CELL_SIZE + CHEESE_OVERSIZE))
        cheese_imgs.append(img)
    
    return cheese_imgs

def init_cheese_inventory(cheese_imgs):
    """Inicializálja a sajtlap inventory-t."""
    cheese_rects = []
    cheese_angles = []
    cheese_used = []
    
    for i, img in enumerate(cheese_imgs):
        pos = (INVENTORY_START_X, INVENTORY_START_Y + i*INVENTORY_SPACING - CHEESE_OVERSIZE//2)
        cheese_rects.append(img.get_rect(topleft=pos))
        cheese_angles.append(0)
        cheese_used.append(False)
    
    return cheese_rects, cheese_angles, cheese_used

def piece_cells(rect, angle, grid_origin, cell_size):
    """Visszaadja a sajtlap által elfoglalt rács cellákat (row,col), 1-alapú index."""
    rel_x = rect.x - grid_origin[0]
    rel_y = rect.y - grid_origin[1]
    col = rel_x // cell_size + 1
    row = rel_y // cell_size + 1
    if angle % 180 == 0:
        return {(row, col), (row, col+1)}
    return {(row, col), (row+1, col)}

def build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx=None):
    """Összeállítja az elfoglalt cellák halmazát."""
    occ = set()
    for idx, pc in enumerate(placed_cheese):
        if exclude_idx is not None and idx == exclude_idx:
            continue
        occ |= piece_cells(pc['rect'], pc['angle'], grid_origin, cell_size)
    return occ

def draw_grid(screen, grid_size, cell_size, grid_origin):
    """Kirajzolja a játék rácsot."""
    for r in range(grid_size):
        for c in range(grid_size):
            rect = pygame.Rect(grid_origin[0] + c*cell_size, grid_origin[1] + r*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, COLOR_GRID_FILL, rect)
            pygame.draw.rect(screen, COLOR_GRID_BORDER, rect, 2)

def draw_mice(screen, mice, grid_origin, cell_size):
    """Kirajzolja az egereket a pályán."""
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

def reset_saves():
    """Törli a mentett beginner szint fájlokat a saves könyvtárból."""
    if not os.path.isdir(SAVE_DIR):
        return 0
    removed = 0
    for name in os.listdir(SAVE_DIR):
        if name.startswith("beginner_level_") and name.endswith(".json"):
            path = os.path.join(SAVE_DIR, name)
            try:
                os.remove(path)
                removed += 1
            except Exception as e:
                print(f"[RESET ERROR] {path}: {e}")
    print(f"[RESET] {removed} mentés törölve")
    return removed

# ================== SZINT KONFIGURÁCIÓK ==================

def get_locked_pieces_for_level(level:int):
    """Visszaadja a szinthez tartozó rögzített darabokat."""
    return LEVEL_LOCKED_PIECES.get(level, [])

def get_completion_targets_for_level(level:int):
    """Visszaadja a szint teljesítési feltételeit."""
    return LEVEL_COMPLETION_TARGETS.get(level, [])

def get_beginner_level_mice(level:int):
    """Szintenként eltérő egér (él) elhelyezések.
    Minden elem egy él: ((r1,c1),(r2,c2)) ahol 1..4 a cella index a 4x4 rácson.
    """
    edges = base_beginner_edges()
    lvl1_indices = [3,5,16,18]
    level1 = [edges[i-1] for i in lvl1_indices if 1 <= i <= len(edges)]

    lvl2_indices = [5,6,11,16,23]
    level2 = [edges[i-1] for i in lvl2_indices if 1 <= i <= len(edges)]

    lvl3_indices = [3,10,12,23,24]
    level3 = [edges[i-1] for i in lvl3_indices if 1 <= i <= len(edges)]

    lvl4_indices = [3,14,18,23]
    level4 = [edges[i-1] for i in lvl4_indices if 1 <= i <= len(edges)]

    lvl5_indices = [5,11,12]
    level5 = [edges[i-1] for i in lvl5_indices if 1 <= i <= len(edges)]

    mapping = {1: level1, 2: level2, 3: level3, 4: level4, 5: level5}
    return mapping.get(level, level1)

def base_beginner_edges():
    """Felhasználó által megadott 24 él sorrend (1..24) a 4x4 cellás rácson."""
    return [
        ((1,1),(1,2)), ((1,2),(1,3)), ((1,3),(1,4)),
        ((1,1),(2,1)), ((1,2),(2,2)), ((1,3),(2,3)), ((1,4),(2,4)),
        ((2,1),(2,2)), ((2,2),(2,3)), ((2,3),(2,4)),
        ((2,1),(3,1)), ((2,2),(3,2)), ((2,3),(3,3)), ((2,4),(3,4)),
        ((3,1),(3,2)), ((3,2),(3,3)), ((3,3),(3,4)),
        ((3,1),(4,1)), ((3,2),(4,2)), ((3,3),(4,3)), ((3,4),(4,4)),
        ((4,1),(4,2)), ((4,2),(4,3)), ((4,3),(4,4))
    ]

def edge_index_mapping():
    """Visszaad egy dict-et: index (1-alapú) -> él tuple."""
    edges = base_beginner_edges()
    return {i+1: e for i, e in enumerate(edges)}

# ---------------- SZINT ADATOK -----------------
LEVEL_LOCKED_PIECES = {
    1: [
        { 'img_index': 1, 'row': 1, 'col': 1, 'angle': 0 },
        { 'img_index': 3, 'row': 1, 'col': 3, 'angle': 0 },
        { 'img_index': 6, 'row': 2, 'col': 1, 'angle': 90 },
        { 'img_index': 5, 'row': 4, 'col': 1, 'angle': 0 },
        { 'img_index': 2, 'row': 4, 'col': 3, 'angle': 180 },
        { 'img_index': 4, 'row': 2, 'col': 4, 'angle': 270 },
    ],
    2: [
        { 'img_index': 7, 'row': 2, 'col': 2, 'angle': 90 },
        { 'img_index': 2, 'row': 3, 'col': 3, 'angle': 90 },
    ],
    3: [
        { 'img_index': 5, 'row': 3, 'col': 3, 'angle': 90 },
    ],
    4: [
        { 'img_index': 2, 'row': 1, 'col': 1, 'angle': 0 }
    ],
    5: [
        { 'img_index': 4, 'row': 1, 'col': 2, 'angle': 0 },
        { 'img_index': 5, 'row': 2, 'col': 2, 'angle': 0 }
    ],
}

LEVEL_COMPLETION_TARGETS = {
    1: [
        { 'img_index': 0, 'cells': [(2,3),(3,3)], 'angle': 'any-vertical' },
        { 'img_index': 7, 'cells': [(2,2),(3,2)], 'angle': 90},
    ],
    2: [{ 'img_index': 0, 'cells': [(1,1),(1,2)], 'angle': 'any-horizontal' },
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

def get_font(size:int):
    return pygame.font.Font(FONT_PATH, size)

def get_locked_pieces_for_level(level:int):
    return LEVEL_LOCKED_PIECES.get(level, [])

def get_completion_targets_for_level(level:int):
    return LEVEL_COMPLETION_TARGETS.get(level, [])

# ================== GAMEPLAY FÜGGVÉNYEK ==================

def apply_locked_pieces(level:int, placed_cheese:list, cheese_imgs:list, grid_origin, cell_size):
    """Alkalmazza a szinthez tartozó rögzített darabokat."""
    specs = get_locked_pieces_for_level(level)
    if not cheese_imgs:
        return
    for spec in specs:
        idx = spec['img_index']
        if not (0 <= idx < len(cheese_imgs)):
            continue
        base_img = cheese_imgs[idx]
        row = spec['row']; col = spec['col']
        angle = spec['angle']
        top_left = (grid_origin[0] + (col-1)*cell_size, grid_origin[1] + (row-1)*cell_size)
        disp_img = base_img
        disp_img = pygame.transform.rotate(disp_img, angle)
        rect = disp_img.get_rect(topleft=top_left)
        exists = False
        for pc in placed_cheese:
            if pc.get('lock') and pc['rect'].topleft == rect.topleft:
                pc['img'] = base_img
                pc['angle'] = angle
                exists = True
                break
        if not exists:
            placed_cheese.append({'img': base_img, 'rect': rect, 'angle': angle, 'lock': True})

def reset_level(level:int, placed_cheese:list, cheese_imgs:list, cheese_used:list, cheese_angles:list, grid_origin, cell_size):
    """Visszaállítja az adott szint alapállapotát: csak a locked pieces maradnak meg."""
    # Eltávolítjuk az összes nem-locked darabot a placed_cheese-ből
    placed_cheese[:] = [pc for pc in placed_cheese if pc.get('lock', False)]
    
    # Visszaállítjuk a cheese_used és cheese_angles állapotát
    for i in range(len(cheese_used)):
        cheese_used[i] = False
        cheese_angles[i] = 0
    
    # Újra alkalmazzuk a locked pieces-eket és frissítjük a cheese_used-ot
    apply_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)
    
    # A locked pieces-ek miatt frissítjük a cheese_used állapotot
    if placed_cheese:
        for pc in placed_cheese:
            if pc.get('lock', False):
                idx = -1
                for i, im in enumerate(cheese_imgs):
                    if im == pc['img']:
                        idx = i
                        break
                if idx >= 0 and idx < len(cheese_used):
                    cheese_used[idx] = True

def check_level_completion(placed_cheese, cheese_imgs, targets, grid_origin, cell_size):
    """Ellenőrzi, hogy a szint teljesítve van-e."""
    if not targets:
        return False
    
    def img_index(img):
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

    def pattern_matches(pat, pc):
        idx = img_index(pc['img'])
        pc_cells = piece_cells(pc['rect'], pc['angle'], grid_origin, cell_size)
        
        if idx != pat['img_index']:
            return False
        if set(pat['cells']) != pc_cells:
            return False
        if not matches_angle(pat['angle'], pc['angle']):
            return False
        return True

    # Preprocess targets: each element can be a single dict or {'any_of': [dict,...]}
    groups = []  # list of list of pattern dicts
    for t in targets:
        if 'any_of' in t:
            groups.append(t['any_of'])
        else:
            groups.append([t])

    # Track satisfied flags per group
    satisfied = [False]*len(groups)

    for gi, variants in enumerate(groups):
        if satisfied[gi]:
            continue
        # Try to find any matching placed piece for any variant
        for pc in placed_cheese:
            for pat in variants:
                if pattern_matches(pat, pc):
                    satisfied[gi] = True
                    break
            if satisfied[gi]:
                break
    
    return all(satisfied)

def can_place_piece(new_rect, angle, placed_cheese, grid_origin, cell_size, grid_size, exclude_idx=None):
    """Ellenőrzi, hogy egy darab elhelyezhető-e az adott pozícióban."""
    cells = piece_cells(new_rect, angle, grid_origin, cell_size)
    occ = build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx)
    
    # Ellenőrizzük a határokat és az ütközéseket
    if cells & occ:
        return False
    if not all(1 <= r <= grid_size and 1 <= c <= grid_size for (r, c) in cells):
        return False
    return True

def init_game_state(level):
    """Inicializálja egy szint játékállapotát."""
    # Játék paraméterek
    grid_size = GRID_SIZE
    cell_size = CELL_SIZE
    cheese_rows, cheese_cols = CHEESE_ROWS, CHEESE_COLS
    grid_origin = (350, SCREEN_HEIGHT//2 - (grid_size*cell_size)//2)
    mice = get_beginner_level_mice(level)

    # Sajtlap készlet betöltése
    cheese_imgs = load_cheese_images()
    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)

    # Húzás állapot
    dragging_idx = None
    dragging_placed_idx = None
    offset = (0, 0)

    # Elhelyezett sajtlapok
    placed_cheese = load_beginner_level(level, cheese_imgs)
    apply_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)

    # A betöltött és lockolt darabok ne jelenjenek meg bal oldalt
    if placed_cheese:
        for pc in placed_cheese:
            idx = -1
            for i, im in enumerate(cheese_imgs):
                if im == pc['img']:
                    idx = i
                    break
            if idx >= 0 and idx < len(cheese_used):
                cheese_used[idx] = True

    # Célállapotok a szinthez
    targets = get_completion_targets_for_level(level)

    # Győzelmi állapot változók
    level_completed = False
    played_completion_sound = False

    return {
        'grid_size': grid_size,
        'cell_size': cell_size,
        'cheese_rows': cheese_rows,
        'cheese_cols': cheese_cols,
        'grid_origin': grid_origin,
        'mice': mice,
        'cheese_imgs': cheese_imgs,
        'cheese_rects': cheese_rects,
        'cheese_angles': cheese_angles,
        'cheese_used': cheese_used,
        'dragging_idx': dragging_idx,
        'dragging_placed_idx': dragging_placed_idx,
        'offset': offset,
        'placed_cheese': placed_cheese,
        'targets': targets,
        'level_completed': level_completed,
        'played_completion_sound': played_completion_sound
    }

def beginner_mode_with_level(level:int):
    """Beginner mód egy konkrét szinttel."""
    # Játék paraméterek
    grid_size = GRID_SIZE
    cell_size = CELL_SIZE
    cheese_rows, cheese_cols = CHEESE_ROWS, CHEESE_COLS
    grid_origin = (350, SCREEN_HEIGHT//2 - (grid_size*cell_size)//2)
    mice = get_beginner_level_mice(level)

    # Sajtlap készlet betöltése
    cheese_imgs = load_cheese_images()
    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)

    # Húzás állapot
    dragging_idx = None
    dragging_placed_idx = None
    offset = (0, 0)

    # Elhelyezett sajtlapok
    placed_cheese = load_beginner_level(level, cheese_imgs)
    apply_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)

    # A betöltött és lockolt darabok ne jelenjenek meg bal oldalt
    if placed_cheese:
        for pc in placed_cheese:
            idx = -1
            for i, im in enumerate(cheese_imgs):
                if im == pc['img']:
                    idx = i
                    break
            if idx >= 0 and idx < len(cheese_used):
                cheese_used[idx] = True

    # Célállapotok a szinthez
    targets = get_completion_targets_for_level(level)

    # Győzelmi állapot változók
    level_completed = False
    played_completion_sound = False

    while True:  # FŐ JÁTÉKCIKLUS
        mouse_pos = pygame.mouse.get_pos()
        screen.fill("black")
        
        # Rács kirajzolása
        draw_grid(screen, grid_size, cell_size, grid_origin)
        
        # Level szöveg
        lvl_text = get_font(40).render(f"LEVEL {level}  |  MICE: {len(mice)}", True, COLOR_LEVEL_TEXT)
        screen.blit(lvl_text, lvl_text.get_rect(center=(SCREEN_WIDTH/2, 40)))
        
        # Szint teljesítés ellenőrzése
        if not level_completed:
            if check_level_completion(placed_cheese, cheese_imgs, targets, grid_origin, cell_size):
                level_completed = True
                if not played_completion_sound:
                    completed_sound.play()
                    played_completion_sound = True
        
        # Egerek kirajzolása
        draw_mice(screen, mice, grid_origin, cell_size)
        
        # Elhelyezett sajtlapok kirajzolása
        for idx, pc in enumerate(placed_cheese):
            base = pc['img']
            draw = pygame.transform.rotate(base, pc['angle'])
            rect = draw.get_rect(topleft=pc['rect'].topleft)
            if dragging_placed_idx == idx:
                mx, my = mouse_pos
                rect.topleft = (mx - offset[0], my - offset[1])
            screen.blit(draw, rect)
            pc['rect'] = rect.copy()
        
        # Inventory sajtlapok kirajzolása
        for i, img in enumerate(cheese_imgs):
            if cheese_used[i]:
                continue  # már a táblán van
            draw = pygame.transform.rotate(img, cheese_angles[i])
            rect = draw.get_rect(topleft=cheese_rects[i].topleft)
            if dragging_idx == i:
                mx, my = mouse_pos
                rect.topleft = (mx - offset[0], my - offset[1])
            screen.blit(draw, rect)
            cheese_rects[i] = rect.copy()
        
        # UI gombok
        back_btn = Button(image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60), 
                         text_input="BACK", font=get_font(50), 
                         base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        reset_btn = Button(image=None, pos=(SCREEN_WIDTH-120, SCREEN_HEIGHT-60), 
                          text_input="RESET", font=get_font(40), 
                          base_color=COLOR_RESET_BUTTON, hovering_color=COLOR_BUTTON_HOVER)
        
        back_btn.changeColor(mouse_pos)
        back_btn.update(screen)
        reset_btn.changeColor(mouse_pos)
        reset_btn.update(screen)
        
        # Teljesítés üzenet
        if level_completed:
            comp = get_font(70).render("COMPLETED!", True, COLOR_COMPLETION)
            screen.blit(comp, comp.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2)))
        
        # Event kezelés
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Gombok kezelése
                if level_completed:
                    if back_btn.checkForInput(mouse_pos):
                        save_beginner_level(level, placed_cheese, cheese_imgs)
                        beginner_levels_menu()
                    if reset_btn.checkForInput(mouse_pos):
                        reset_level(level, placed_cheese, cheese_imgs, cheese_used, cheese_angles, grid_origin, cell_size)
                        level_completed = False
                        played_completion_sound = False
                    continue
                
                if back_btn.checkForInput(mouse_pos):
                    save_beginner_level(level, placed_cheese, cheese_imgs)
                    beginner_levels_menu()
                
                if reset_btn.checkForInput(mouse_pos):
                    reset_level(level, placed_cheese, cheese_imgs, cheese_used, cheese_angles, grid_origin, cell_size)
                    level_completed = False
                    played_completion_sound = False
                
                # Húzás kezdése
                if event.button == 1 and dragging_idx is None and dragging_placed_idx is None:
                    # Elhelyezett darabok ellenőrzése (felső réteg először)
                    for idx in reversed(range(len(placed_cheese))):
                        pc = placed_cheese[idx]
                        if pc['rect'].collidepoint(event.pos):
                            if not pc.get('lock'):
                                dragging_placed_idx = idx
                                offset = (event.pos[0] - pc['rect'].x, event.pos[1] - pc['rect'].y)
                            break
                    else:
                        # Inventory darabok ellenőrzése
                        for i, r in enumerate(cheese_rects):
                            if cheese_used[i]:
                                continue
                            if r.collidepoint(event.pos):
                                dragging_idx = i
                                offset = (event.pos[0] - r.x, event.pos[1] - r.y)
                                break
                
                # Forgatás
                if event.button == 3:  # jobb egérgomb
                    rotated = False
                    # Inventory forgatás
                    for i, r in enumerate(cheese_rects):
                        if cheese_used[i]:
                            continue
                        if r.collidepoint(event.pos):
                            cheese_angles[i] = (cheese_angles[i] - 90) % 360
                            rotated = True
                            break
                    
                    # Elhelyezett darabok forgatása
                    if not rotated:
                        for idx, pc in enumerate(placed_cheese):
                            if pc['rect'].collidepoint(event.pos) and not pc.get('lock'):
                                old = pc['angle']
                                pc['angle'] = (pc['angle'] - 90) % 360
                                
                                if not can_place_piece(pc['rect'], pc['angle'], placed_cheese, 
                                                     grid_origin, cell_size, grid_size, exclude_idx=idx):
                                    pc['angle'] = old
                                break
            
            if event.type == pygame.MOUSEBUTTONUP and not level_completed:
                # Inventory darab húzásának vége
                if dragging_idx is not None:
                    mx, my = pygame.mouse.get_pos()
                    ang = cheese_angles[dragging_idx]
                    w, h = (cheese_cols, cheese_rows) if ang % 180 == 0 else (cheese_rows, cheese_cols)
                    gx = (mx - grid_origin[0]) // cell_size
                    gy = (my - grid_origin[1]) // cell_size
                    
                    if 0 <= gx <= grid_size - w and 0 <= gy <= grid_size - h:
                        sx = grid_origin[0] + gx * cell_size
                        sy = grid_origin[1] + gy * cell_size
                        draw = pygame.transform.rotate(cheese_imgs[dragging_idx], ang)
                        new_rect = draw.get_rect(topleft=(sx, sy))
                        
                        if can_place_piece(new_rect, ang, placed_cheese, grid_origin, cell_size, grid_size):
                            placed_cheese.append({
                                'img': cheese_imgs[dragging_idx], 
                                'rect': new_rect.copy(), 
                                'angle': ang
                            })
                            cheese_used[dragging_idx] = True
                    
                    # Inventory pozíció visszaállítása
                    cheese_rects[dragging_idx].topleft = (INVENTORY_START_X, INVENTORY_START_Y + dragging_idx * INVENTORY_SPACING)
                    dragging_idx = None
                
                # Elhelyezett darab húzásának vége
                if dragging_placed_idx is not None:
                    mx, my = pygame.mouse.get_pos()
                    pc = placed_cheese[dragging_placed_idx]
                    ang = pc['angle']
                    w, h = (cheese_cols, cheese_rows) if ang % 180 == 0 else (cheese_rows, cheese_cols)
                    gx = (mx - grid_origin[0]) // cell_size
                    gy = (my - grid_origin[1]) // cell_size
                    
                    if 0 <= gx <= grid_size - w and 0 <= gy <= grid_size - h:
                        sx = grid_origin[0] + gx * cell_size
                        sy = grid_origin[1] + gy * cell_size
                        draw = pygame.transform.rotate(pc['img'], ang)
                        new_rect = draw.get_rect(topleft=(sx, sy))
                        
                        if can_place_piece(new_rect, ang, placed_cheese, grid_origin, cell_size, 
                                         grid_size, exclude_idx=dragging_placed_idx):
                            placed_cheese[dragging_placed_idx]['rect'] = new_rect.copy()
                    else:
                        # Darab eltávolítása a pályáról
                        if not pc.get('lock'):
                            removed = placed_cheese.pop(dragging_placed_idx)
                            # Vissza inventory-ba
                            for i, im in enumerate(cheese_imgs):
                                if im == removed['img']:
                                    cheese_used[i] = False
                                    cheese_angles[i] = 0
                                    cheese_rects[i].topleft = (INVENTORY_START_X, INVENTORY_START_Y + i * INVENTORY_SPACING)
                                    break
                    
                    dragging_placed_idx = None
            
            if event.type == pygame.MOUSEMOTION and not level_completed:
                if dragging_idx is not None:
                    mx, my = event.pos
                    cheese_rects[dragging_idx].topleft = (mx - offset[0], my - offset[1])
                
                if dragging_placed_idx is not None:
                    mx, my = event.pos
                    placed_cheese[dragging_placed_idx]['rect'].topleft = (mx - offset[0], my - offset[1])
        
        pygame.display.update()


def beginner_levels_menu():
    # A szint választó menü a menü zenét használja, csak akkor indítsuk ha nem szól
    if not pygame.mixer.get_busy():
        menu_music.play(-1)
    while True:
        screen.blit(background, (0,0))
        mouse_pos = pygame.mouse.get_pos()

        title_text = get_font(60).render("BEGINNER LEVELS", True, COLOR_LEVEL_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, 80))
        screen.blit(title_text, title_rect)

        # 5 szint gombok
        level_buttons = []
        start_y = 200
        spacing = 90
        for i in range(5):
            btn = Button(image=pygame.image.load(PLAY_BG_IMAGE),
                         pos=(SCREEN_WIDTH/2, start_y + i*spacing),
                         text_input=f"LEVEL {i+1}", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
            level_buttons.append(btn)

        back_button = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, start_y + 5*spacing),
                              text_input="BACK", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="Red")

        for btn in level_buttons + [back_button]:
            btn.changeColor(mouse_pos)
            btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn in enumerate(level_buttons):
                    if btn.checkForInput(mouse_pos):
                        beginner_mode_with_level(idx+1)
                if back_button.checkForInput(mouse_pos):
                    main_menu()

        pygame.display.update()

def save_beginner_level(level:int, placed_cheese:list, cheese_imgs:list):
    """Beginner mód adott szintjének mentése JSON formátumban.
    Formátum: {"pieces": [{"x": int, "y": int, "angle": int, "flip": bool, "img_index": int, "lock": bool}]}.
    img_index: a cheese_imgs listában lévő index (0-alapú), így visszaállítható az eredeti grafika.
    lock: True esetén a darab nem törölhető / nem mozgatható / nem forgatható.
    """
    data = []
    for pc in placed_cheese:
        # Meghatározzuk melyik indexű az adott img
        img_index = 0
        for idx, im in enumerate(cheese_imgs):
            if im == pc['img']:
                img_index = idx
                break
        data.append({
            'x': pc['rect'].x,
            'y': pc['rect'].y,
            'angle': pc.get('angle', 0),
            # flip eltávolítva
            'img_index': img_index,
            'lock': pc.get('lock', False)
        })
    path = os.path.join(SAVE_DIR, f"beginner_level_{level}.json")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'pieces': data}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_beginner_level(level:int, cheese_imgs:list):
    """Betölti a beginner szint elmentett állapotát, ha létezik.
    Ha nem létezik, üres listát ad vissza.
    lock mező támogatott (alapértelmezés False).
    """
    path = os.path.join(SAVE_DIR, f"beginner_level_{level}.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        pieces = []
        for entry in raw.get('pieces', []):
            idx = entry.get('img_index', 0)
            if 0 <= idx < len(cheese_imgs):
                base_img = cheese_imgs[idx]
            else:
                base_img = cheese_imgs[0] if cheese_imgs else None
            if base_img is None:
                continue
            angle = entry.get('angle', 0)
            flip = entry.get('flip', False)
            # Rekonstruáljuk a megjelenített rect-et a forgatás és flip után is ugyanazzal a topleft-tel
            draw_img = base_img
            if flip:
                draw_img = pygame.transform.flip(draw_img, True, False)
            draw_img = pygame.transform.rotate(draw_img, angle)
            rect = draw_img.get_rect(topleft=(entry.get('x',0), entry.get('y',0)))
            pieces.append({'img': base_img, 'rect': rect, 'angle': angle, 'lock': entry.get('lock', False)})
        return pieces
    except Exception as e:
        print(f"[LOAD ERROR] {e}")
        return []

def expert_mode():
    menu_music.stop()
    # Pálya paraméterek
    grid_size = GRID_SIZE  # 4x4-es rács
    cell_size = CELL_SIZE
    cheese_rows, cheese_cols = CHEESE_ROWS, CHEESE_COLS  # Sajtlap méret: 1 sor magas, 2 oszlop széles
    # Tábla jobbra tolva, de nem teljesen a szélre
    grid_origin = (350, SCREEN_HEIGHT//2 - (grid_size*cell_size)//2)
    # Egerek fix pozícióban (pl. 3 egér)
    # 4x4-es pályán az egerek a rács metszéspontjain (csomópontokon) vannak
    # Pl. 5x5 csomópont, az egérpozíciók (sor, oszlop) 0-4-ig
    # Egerek a kockák közötti éleken (vízszintes vagy függőleges):
    # Minden egér: ((r1, c1), (r2, c2))
    mice = [
        # sor, oszlop indexelés 1-től 4-ig
        # vízszintes élek
        ((1,1), (1,2)), ((1,2), (1,3)), ((1,3), (1,4)),
        ((2,1), (2,2)), ((2,2), (2,3)), ((2,3), (2,4)),
        ((3,1), (3,2)), ((3,2), (3,3)), ((3,3), (3,4)),
        ((4,1), (4,2)), ((4,2), (4,3)), ((4,3), (4,4)),
        # függőleges élek
        ((1,1), (2,1)), ((1,2), (2,2)), ((1,3), (2,3)), ((1,4), (2,4)),
        ((2,1), (3,1)), ((2,2), (3,2)), ((2,3), (3,3)), ((2,4), (3,4)),
        ((3,1), (4,1)), ((3,2), (4,2)), ((3,3), (4,3)), ((3,4), (4,4)),
    ]
    # Sajtlap képek betöltése és átméretezése cellaméretre
    cheese_imgs = []
    cheese_rects = []
    cheese_angles = []  # forgatási szög minden sajtlaphoz (bal oldaliak)
    cheese_flips = []   # horizontális tükrözés állapota
    num_cheese = 8  # bővítve SAJTLAP8-cal (második játékhurok)
    cheese_oversize = -2  # nagyon picivel kisebb csak
    cheese_start_y_offset = 100
    for i in range(1, num_cheese + 1):
        img = pygame.image.load(f"assets/images/cheese/SAJTLAP{i}.png").convert_alpha()
        img = pygame.transform.smoothscale(
            img,
            (cheese_cols*cell_size + cheese_oversize, cheese_rows*cell_size + cheese_oversize)
        )
        cheese_imgs.append(img)
        # A bal oldali készletben egymás alatt
        cheese_rects.append(img.get_rect(topleft=(30, 100 + (i-1)*70 - cheese_oversize//2)))
        cheese_angles.append(0)
        cheese_flips.append(False)
    dragging_idx = None  # Bal oldali sajtlap indexe, ha azt húzzuk
    dragging_placed_idx = None  # Pályán lévő sajtlap indexe, ha azt húzzuk
    offset = (0, 0)

    # placed_cheese: list of dict: {img, rect, angle}
    placed_cheese = []

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        # Háttér kirajzolása minden frame-ben
        screen.fill("black")
        # Pálya rács kirajzolása
        draw_grid(screen, grid_size, cell_size, grid_origin)

        # Egerek kirajzolása
        draw_mice(screen, mice, grid_origin, cell_size)

        # Elhelyezett sajtlapok kirajzolása
        for idx, pc in enumerate(placed_cheese):
            base_img = pc['img']
            if pc.get('flip', False):
                base_img = pygame.transform.flip(base_img, True, False)
            draw_img = pygame.transform.rotate(base_img, pc['angle'])
            # Mindig a bal felső sarokhoz igazítunk
            draw_rect = draw_img.get_rect(topleft=pc['rect'].topleft)
            # Ha ezt húzzuk, az egérnél jelenjen meg
            if dragging_placed_idx == idx:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                draw_rect.topleft = (mouse_x - offset[0], mouse_y - offset[1])
            screen.blit(draw_img, draw_rect)
            pc['rect'] = draw_rect.copy()

        # Sajtlap képek bal oldalon (húzhatóak)
        for i, img in enumerate(cheese_imgs):
            base_img = img
            if cheese_flips[i]:
                base_img = pygame.transform.flip(base_img, True, False)
            draw_img = pygame.transform.rotate(base_img, cheese_angles[i])
            draw_rect = draw_img.get_rect(topleft=cheese_rects[i].topleft)
            # Ha ezt húzzuk, az egérnél jelenjen meg
            if dragging_idx == i:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                draw_rect.topleft = (mouse_x - offset[0], mouse_y - offset[1])
            screen.blit(draw_img, draw_rect)
            cheese_rects[i] = draw_rect.copy()

        # Vissza gomb
        PLAY_BACK = Button(image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60),
                            text_input="BACK", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                # Bal egérgomb: húzás kezdete (csak egyet lehet)
                if event.button == 1 and dragging_idx is None and dragging_placed_idx is None:
                    # Először nézzük a pályán lévő sajtlapokat (fordított sorrend, hogy a legfelsőt kapjuk el)
                    for idx in reversed(range(len(placed_cheese))):
                        pc = placed_cheese[idx]
                        if pc['rect'].collidepoint(event.pos):
                            dragging_placed_idx = idx
                            offset = (event.pos[0] - pc['rect'].x, event.pos[1] - pc['rect'].y)
                            break
                    else:
                        # Ha nem a pályán, akkor bal oldali készletből
                        for i, rect in enumerate(cheese_rects):
                            if rect.collidepoint(event.pos):
                                dragging_idx = i
                                offset = (event.pos[0] - rect.x, event.pos[1] - rect.y)
                                break
                # Jobb egérgomb: forgatás (inventory vagy pályán collision ellenőrzéssel)
                if event.button == 3:
                    rotated_inventory = False
                    for i, rect in enumerate(cheese_rects):
                        if rect.collidepoint(event.pos):
                            cheese_angles[i] = (cheese_angles[i] - 90) % 360
                            rotated_inventory = True
                            break
                    if not rotated_inventory:
                        for idx, pc in enumerate(placed_cheese):
                            if pc['rect'].collidepoint(event.pos):
                                old_angle = pc['angle']
                                pc['angle'] = (pc['angle'] - 90) % 360
                                occ = build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx=idx)
                                cells = piece_cells(pc['rect'], pc['angle'], grid_origin, cell_size)
                                if any(r < 1 or c < 1 or r > grid_size or c > grid_size for (r,c) in cells) or cells & occ:
                                    pc['angle'] = old_angle
                                break
                # Középső egérgomb (button 2): tükrözés
                if event.button == 2:
                    flipped = False
                    for i, rect in enumerate(cheese_rects):
                        if rect.collidepoint(event.pos):
                            cheese_flips[i] = not cheese_flips[i]
                            flipped = True
                            break
                    if not flipped:
                        for pc in placed_cheese:
                            if pc['rect'].collidepoint(event.pos):
                                pc['flip'] = not pc.get('flip', False)
                                break

            if event.type == pygame.MOUSEBUTTONUP:
                # Bal oldali sajtlap húzás vége
                if dragging_idx is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    img = cheese_imgs[dragging_idx]
                    angle = cheese_angles[dragging_idx]
                    if angle % 180 == 0:
                        w, h = cheese_cols, cheese_rows
                    else:
                        w, h = cheese_rows, cheese_cols
                    grid_x = (mouse_x - grid_origin[0]) // cell_size
                    grid_y = (mouse_y - grid_origin[1]) // cell_size
                    if 0 <= grid_x <= grid_size - w and 0 <= grid_y <= grid_size - h:
                        snap_x = grid_origin[0] + grid_x * cell_size
                        snap_y = grid_origin[1] + grid_y * cell_size
                        draw_img = pygame.transform.rotate(img, angle)
                        new_rect = draw_img.get_rect(topleft=(snap_x, snap_y))
                        cells = piece_cells(new_rect, angle, grid_origin, cell_size)
                        occ = build_occupied_cells(placed_cheese, grid_origin, cell_size)
                        if not (cells & occ) and all(1 <= r <= grid_size and 1 <= c <= grid_size for (r,c) in cells):
                            placed_cheese.append({'img': img, 'rect': new_rect.copy(), 'angle': angle})
                    cheese_rects[dragging_idx].topleft = (30, 100 + dragging_idx*70)
                    dragging_idx = None
                # Pályán lévő sajtlap húzás vége
                if dragging_placed_idx is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    pc = placed_cheese[dragging_placed_idx]
                    img = pc['img']
                    angle = pc['angle']
                    if angle % 180 == 0:
                        w, h = cheese_cols, cheese_rows
                    else:
                        w, h = cheese_rows, cheese_cols
                    grid_x = (mouse_x - grid_origin[0]) // cell_size
                    grid_y = (mouse_y - grid_origin[1]) // cell_size
                    if 0 <= grid_x <= grid_size - w and 0 <= grid_y <= grid_size - h:
                        snap_x = grid_origin[0] + grid_x * cell_size
                        snap_y = grid_origin[1] + grid_y * cell_size
                        draw_img = pygame.transform.rotate(img, angle)
                        new_rect = draw_img.get_rect(topleft=(snap_x, snap_y))
                        cells = piece_cells(new_rect, angle, grid_origin, cell_size)
                        occ = build_occupied_cells(placed_cheese, grid_origin, cell_size, exclude_idx=dragging_placed_idx)
                        if not (cells & occ) and all(1 <= r <= grid_size and 1 <= c <= grid_size for (r,c) in cells):
                            placed_cheese[dragging_placed_idx]['rect'] = new_rect.copy()
                        else:
                            # marad az eredeti helyén
                            pass
                    else:
                        placed_cheese.pop(dragging_placed_idx)
                    dragging_placed_idx = None
            if event.type == pygame.MOUSEMOTION:
                if dragging_idx is not None:
                    mouse_x, mouse_y = event.pos
                    cheese_rects[dragging_idx].topleft = (mouse_x - offset[0], mouse_y - offset[1])
                if dragging_placed_idx is not None:
                    mouse_x, mouse_y = event.pos
                    placed_cheese[dragging_placed_idx]['rect'].topleft = (mouse_x - offset[0], mouse_y - offset[1])

        pygame.display.update()

def main_menu():
    # Főmenü: Start Beginner, Start Expert, Quit
    if not pygame.mixer.get_busy():
        menu_music.play(-1)
    while True:
        screen.blit(background, (0,0))
        mouse_pos = pygame.mouse.get_pos()
        title = get_font(70).render("BRAIN CHEESER", True, COLOR_LEVEL_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH/2, 50)))
        madeby = get_font(20).render("by Czuper Tibor", True, COLOR_LEVEL_TEXT)
        screen.blit(madeby, madeby.get_rect(center=(SCREEN_WIDTH/2, 100)))

        beginner_btn = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 250), text_input="BEGINNER", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        expert_btn   = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 375), text_input="EXPERT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        quit_btn     = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, 500), text_input="QUIT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="red")
        # Reset gomb (bal alsó sarok)
        reset_btn = Button(image=None, pos=(120, SCREEN_HEIGHT-50), text_input="RESET", font=get_font(30), base_color="#ff0000", hovering_color=COLOR_BUTTON_HOVER)

        for b in (beginner_btn, expert_btn, quit_btn, reset_btn):
            b.changeColor(mouse_pos); b.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_btn.checkForInput(mouse_pos):
                    reset_saves()
                if beginner_btn.checkForInput(mouse_pos):
                    beginner_levels_menu()
                if expert_btn.checkForInput(mouse_pos):
                    expert_mode()
                if quit_btn.checkForInput(mouse_pos):
                    pygame.quit(); sys.exit()
        pygame.display.update()

if __name__ == '__main__':
    main_menu()