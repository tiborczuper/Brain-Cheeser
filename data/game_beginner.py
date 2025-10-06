import pygame, sys
from config import *
from assets.button import Button
from shared import (draw_grid, draw_mice, can_place_piece, check_level_completion,
                    init_cheese_inventory, load_cheese_images, get_font, get_cheese_inventory_position,
                    draw_placement_preview)
from beginner import (
    get_beginner_level_mice,
    get_beginner_completion_targets,
    apply_beginner_locked_pieces,
    load_beginner_level,
    save_beginner_level,
    CHEESE_IMAGES as BEGINNER_CHEESE_IMAGES
)

# NOTE: We reuse the CHEESE_IMAGES loaded in beginner.py for consistency in save indexes.
# If images are added at runtime, restart is required.


def run_beginner_level(level:int):
    grid_size = GRID_SIZE
    cell_size = CELL_SIZE
    cheese_rows, cheese_cols = CHEESE_ROWS, CHEESE_COLS
    grid_origin = (350, SCREEN_HEIGHT//2 - (grid_size*cell_size)//2)

    mice = get_beginner_level_mice(level)
    cheese_imgs = BEGINNER_CHEESE_IMAGES
    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)

    # Load global progress (may hold another level)
    saved_level, saved_pieces = load_beginner_level()
    placed_cheese = saved_pieces if saved_level == level else []

    # Apply locked specs for this level (ensures locked pieces always present)
    apply_beginner_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)

    # Mark used inventory pieces
    for pc in placed_cheese:
        for i, im in enumerate(cheese_imgs):
            if im == pc['img']:
                cheese_used[i] = True
                break

    targets = get_beginner_completion_targets(level)
    level_completed = False
    played_completion_sound = False

    dragging_idx = None
    dragging_placed_idx = None
    offset = (0,0)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill("black")
        draw_grid(screen, grid_size, cell_size, grid_origin)

        header = get_font(40).render(f"LEVEL {level}  |  MICE: {len(mice)}", True, COLOR_LEVEL_TEXT)
        screen.blit(header, header.get_rect(center=(SCREEN_WIDTH/2, 40)))

        if not level_completed:
            if check_level_completion(placed_cheese, cheese_imgs, targets, grid_origin, cell_size):
                level_completed = True
                if not played_completion_sound:
                    completed_sound.play(); played_completion_sound = True
                # Save state on completion
                save_beginner_level(level, placed_cheese)

        draw_mice(screen, mice, grid_origin, cell_size)

        # Placed pieces
        for idx, pc in enumerate(placed_cheese):
            draw_img = pygame.transform.rotate(pc['img'], pc['angle'])
            rect = draw_img.get_rect(topleft=pc['rect'].topleft)
            if dragging_placed_idx == idx:
                mx,my = mouse_pos
                rect.topleft = (mx-offset[0], my-offset[1])
            screen.blit(draw_img, rect)
            pc['rect'] = rect.copy()

        # Inventory pieces
        for i, img in enumerate(cheese_imgs):
            if cheese_used[i]:
                continue
            draw_img = pygame.transform.rotate(img, cheese_angles[i])
            rect = draw_img.get_rect(topleft=cheese_rects[i].topleft)
            if dragging_idx == i:
                mx,my = mouse_pos
                rect.topleft = (mx-offset[0], my-offset[1])
            screen.blit(draw_img, rect)
            cheese_rects[i] = rect.copy()

        # Draw placement preview when dragging
        if dragging_idx is not None:
            draw_placement_preview(screen, mouse_pos, cheese_imgs[dragging_idx], cheese_angles[dragging_idx], 
                                 grid_origin, cell_size, grid_size, placed_cheese)
        elif dragging_placed_idx is not None:
            pc = placed_cheese[dragging_placed_idx]
            draw_placement_preview(screen, mouse_pos, pc['img'], pc['angle'], 
                                 grid_origin, cell_size, grid_size, placed_cheese, dragging_placed_idx)

        # Buttons
        back_btn = Button(image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60), text_input="BACK", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="red")
        reset_btn = Button(image=None, pos=(SCREEN_WIDTH-120, SCREEN_HEIGHT-60), text_input="RESET", font=get_font(40), base_color=COLOR_RESET_BUTTON, hovering_color=COLOR_BUTTON_HOVER)
        for b in (back_btn, reset_btn):
            b.changeColor(mouse_pos); b.update(screen)

        if level_completed:
            comp = get_font(70).render("COMPLETED!", True, COLOR_COMPLETION)
            screen.blit(comp, comp.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2 - 225)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Completed state: only buttons work
                if level_completed:
                    if back_btn.checkForInput(mouse_pos):
                        save_beginner_level(level, placed_cheese)
                        return  # caller menu
                    if reset_btn.checkForInput(mouse_pos):
                        # Reset to locked state only
                        placed_cheese = []
                        cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)
                        apply_beginner_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)
                        for pc in placed_cheese:
                            for i, im in enumerate(cheese_imgs):
                                if im == pc['img']:
                                    cheese_used[i] = True
                                    break
                        level_completed = False; played_completion_sound=False
                    continue

                # Buttons
                if back_btn.checkForInput(mouse_pos):
                    save_beginner_level(level, placed_cheese)
                    return
                if reset_btn.checkForInput(mouse_pos):
                    placed_cheese = []
                    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)
                    apply_beginner_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)
                    for pc in placed_cheese:
                        for i, im in enumerate(cheese_imgs):
                            if im == pc['img']:
                                cheese_used[i] = True
                                break
                    level_completed = False; played_completion_sound=False
                    continue

                # Start drag
                if event.button == 1 and dragging_idx is None and dragging_placed_idx is None:
                    for idx in reversed(range(len(placed_cheese))):
                        pc = placed_cheese[idx]
                        if pc['rect'].collidepoint(event.pos) and not pc.get('locked'):
                            dragging_placed_idx = idx
                            offset = (event.pos[0]-pc['rect'].x, event.pos[1]-pc['rect'].y)
                            break
                    else:
                        for i, r in enumerate(cheese_rects):
                            if cheese_used[i]:
                                continue
                            if r.collidepoint(event.pos):
                                dragging_idx = i
                                offset = (event.pos[0]-r.x, event.pos[1]-r.y)
                                break
                # Rotate
                if event.button == 3:
                    rotated = False
                    for i, r in enumerate(cheese_rects):
                        if cheese_used[i]:
                            continue
                        if r.collidepoint(event.pos):
                            cheese_angles[i] = (cheese_angles[i]-90)%360
                            rotated = True
                            break
                    if not rotated:
                        for idx, pc in enumerate(placed_cheese):
                            if pc['rect'].collidepoint(event.pos) and not pc.get('locked'):
                                old = pc['angle']
                                pc['angle'] = (pc['angle']-90)%360
                                if not can_place_piece(pc['rect'], pc['angle'], placed_cheese, grid_origin, cell_size, grid_size, exclude_idx=idx):
                                    pc['angle'] = old
                                break

            if event.type == pygame.MOUSEBUTTONUP and not level_completed:
                # Release inventory piece
                if dragging_idx is not None:
                    mx,my = pygame.mouse.get_pos(); ang = cheese_angles[dragging_idx]
                    w,h = (cheese_cols,cheese_rows) if ang%180==0 else (cheese_rows,cheese_cols)
                    tmp = pygame.transform.rotate(cheese_imgs[dragging_idx], ang)
                    tmp_rect = tmp.get_rect(center=(mx,my))
                    cx,cy = tmp_rect.center
                    gx = int((cx-grid_origin[0])/cell_size)
                    gy = int((cy-grid_origin[1])/cell_size)
                    if 0 <= gx <= grid_size-w and 0 <= gy <= grid_size-h:
                        sx = grid_origin[0]+gx*cell_size
                        sy = grid_origin[1]+gy*cell_size
                        draw_img = pygame.transform.rotate(cheese_imgs[dragging_idx], ang)
                        new_rect = draw_img.get_rect(topleft=(sx,sy))
                        if can_place_piece(new_rect, ang, placed_cheese, grid_origin, cell_size, grid_size):
                            placed_cheese.append({'img': cheese_imgs[dragging_idx], 'rect': new_rect.copy(), 'angle': ang})
                            cheese_used[dragging_idx] = True
                    cheese_rects[dragging_idx].topleft = get_cheese_inventory_position(dragging_idx, cheese_imgs)
                    dragging_idx = None
                # Release placed piece
                if dragging_placed_idx is not None:
                    mx,my = pygame.mouse.get_pos(); pc = placed_cheese[dragging_placed_idx]; ang = pc['angle']
                    w,h = (cheese_cols,cheese_rows) if ang%180==0 else (cheese_rows,cheese_cols)
                    tmp = pygame.transform.rotate(pc['img'], ang)
                    tmp_rect = tmp.get_rect(center=(mx,my))
                    cx,cy = tmp_rect.center
                    gx = int((cx-grid_origin[0])/cell_size)
                    gy = int((cy-grid_origin[1])/cell_size)
                    if 0 <= gx <= grid_size-w and 0 <= gy <= grid_size-h:
                        sx = grid_origin[0]+gx*cell_size
                        sy = grid_origin[1]+gy*cell_size
                        draw_img = pygame.transform.rotate(pc['img'], ang)
                        new_rect = draw_img.get_rect(topleft=(sx,sy))
                        if can_place_piece(new_rect, ang, placed_cheese, grid_origin, cell_size, grid_size, exclude_idx=dragging_placed_idx):
                            placed_cheese[dragging_placed_idx]['rect'] = new_rect.copy()
                    else:
                        if not pc.get('locked'):
                            removed = placed_cheese.pop(dragging_placed_idx)
                            for i, im in enumerate(cheese_imgs):
                                if im == removed['img']:
                                    cheese_used[i] = False
                                    cheese_angles[i] = 0
                                    cheese_rects[i].topleft = get_cheese_inventory_position(i, cheese_imgs)
                                    break
                    dragging_placed_idx = None

            if event.type == pygame.MOUSEMOTION and not level_completed:
                if dragging_idx is not None:
                    mx,my = event.pos
                    cheese_rects[dragging_idx].topleft = (mx-offset[0], my-offset[1])
                if dragging_placed_idx is not None:
                    mx,my = event.pos
                    placed_cheese[dragging_placed_idx]['rect'].topleft = (mx-offset[0], my-offset[1])

        pygame.display.update()
