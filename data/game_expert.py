import pygame, sys
from config import *
from assets.button import Button
from shared import (draw_grid, draw_mice, can_place_piece, check_level_completion,
                    init_cheese_inventory, load_cheese_images, get_font, get_cheese_inventory_position,
                    draw_placement_preview)
from expert import (
    get_expert_level_mice,
    get_expert_completion_targets,
    apply_expert_locked_pieces,
    load_expert_level,
    save_expert_level,
    CHEESE_IMAGES as EXPERT_CHEESE_IMAGES
)

def run_expert_level(level:int):
    grid_size = GRID_SIZE
    cell_size = CELL_SIZE
    cheese_rows, cheese_cols = CHEESE_ROWS, CHEESE_COLS
    grid_origin = (350, SCREEN_HEIGHT//2 - (grid_size*cell_size)//2)

    mice = get_expert_level_mice(level)
    cheese_imgs = EXPERT_CHEESE_IMAGES
    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)

    # Load saved progress for this specific level
    saved_level, saved_pieces, saved_money, saved_completed, saved_game_over = load_expert_level(level)
    placed_cheese = saved_pieces

    # Apply locked specs for this level (ensures locked pieces always present)
    apply_expert_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)

    # Mark used inventory pieces
    for pc in placed_cheese:
        for i, im in enumerate(cheese_imgs):
            if im == pc['img']:
                cheese_used[i] = True
                break

    targets = get_expert_completion_targets(level)
    
    # Load saved status for this level
    level_completed = saved_completed
    game_over = saved_game_over
    money = saved_money if saved_money is not None else EXPERT_LEVEL_START_MONEY.get(level, 100)
    
    played_completion_sound = False
    played_failed_sound = False

    dragging_idx = None
    dragging_placed_idx = None
    offset = (0,0)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((20, 30, 40))  # Dark blue background

        draw_grid(screen, grid_size, cell_size, grid_origin)
        
        header = get_font(34).render(f"EXPERT LEVEL {level} | MICE: {len(mice)}", True, COLOR_LEVEL_TEXT)
        screen.blit(header, header.get_rect(center=(SCREEN_WIDTH/2, 40)))
        
        # Money display below the grid, centered
        money_text = get_font(40).render(f"${money}", True, COLOR_LEVEL_TEXT)
        grid_center_x = grid_origin[0] + (grid_size * cell_size) // 2
        grid_bottom_y = grid_origin[1] + (grid_size * cell_size) + 50
        screen.blit(money_text, money_text.get_rect(center=(grid_center_x, grid_bottom_y)))

        # Check completion
        if not level_completed and not game_over:
            if check_level_completion(placed_cheese, cheese_imgs, targets, grid_origin, cell_size):
                level_completed = True
                if not played_completion_sound:
                    completed_sound.play(); played_completion_sound = True
                # Save state on completion
                save_expert_level(level, placed_cheese, money, level_completed, game_over)

        draw_mice(screen, mice, grid_origin, cell_size)

        # Draw placed cheese
        for i, pc in enumerate(placed_cheese):
            draw_img = pygame.transform.rotate(pc['img'], pc['angle'])
            rect = draw_img.get_rect(topleft=pc['rect'].topleft)
            if dragging_placed_idx == i:
                mx,my = mouse_pos
                rect.topleft = (mx-offset[0], my-offset[1])
            screen.blit(draw_img, rect)

        # Draw inventory cheese
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

        # Buttons - Reset csak completed vagy game over állapotban
        back_btn = Button(image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60), text_input="BACK", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="red")
        
        reset_active = (level_completed or game_over)
        reset_color = COLOR_RESET_BUTTON if reset_active else (100, 100, 100)
        reset_hover = COLOR_BUTTON_HOVER if reset_active else reset_color
        reset_btn = Button(image=None, pos=(SCREEN_WIDTH-120, SCREEN_HEIGHT-60), text_input="RESET", font=get_font(40), base_color=reset_color, hovering_color=reset_hover)
        
        for b in (back_btn, reset_btn):
            b.changeColor(mouse_pos); b.update(screen)

        if level_completed:
            comp = get_font(70).render("COMPLETED!", True, COLOR_COMPLETION)
            screen.blit(comp, comp.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2 - 225)))
        elif game_over:
            go = get_font(70).render("GAME OVER", True, (200,40,40))
            screen.blit(go, go.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2 - 225)))
            if not played_failed_sound:
                failed_sound = pygame.mixer.Sound("assets/sounds/failed.mp3")
                failed_sound.play()
                played_failed_sound = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Buttons work in all states
                if back_btn.checkForInput(mouse_pos):
                    save_expert_level(level, placed_cheese, money, level_completed, game_over)
                    return
                
                # Reset only works when level completed or game over
                if reset_active and reset_btn.checkForInput(mouse_pos):
                    placed_cheese = []
                    cheese_rects, cheese_angles, cheese_used = init_cheese_inventory(cheese_imgs)
                    apply_expert_locked_pieces(level, placed_cheese, cheese_imgs, grid_origin, cell_size)
                    for pc in placed_cheese:
                        for i, im in enumerate(cheese_imgs):
                            if im == pc['img']:
                                cheese_used[i] = True
                                break
                    level_completed = False
                    game_over = False
                    played_completion_sound = False
                    money = EXPERT_LEVEL_START_MONEY.get(level, 100)  # Reset money
                    continue

                # Game logic only works if not completed and not game over
                if level_completed or game_over:
                    continue

                # Check inventory dragging
                for i, rect in enumerate(cheese_rects):
                    if cheese_used[i]:
                        continue
                    if rect.collidepoint(mouse_pos):
                        dragging_idx = i
                        offset = (mouse_pos[0] - rect.x, mouse_pos[1] - rect.y)
                        break

                # Check placed pieces dragging  
                for i, pc in enumerate(placed_cheese):
                    if pc.get('locked'):  # Skip locked pieces
                        continue
                    draw_img = pygame.transform.rotate(pc['img'], pc['angle'])
                    rect = draw_img.get_rect(topleft=pc['rect'].topleft)
                    if rect.collidepoint(mouse_pos):
                        dragging_placed_idx = i
                        offset = (mouse_pos[0] - rect.x, mouse_pos[1] - rect.y)
                        break

                # Rotate with right click (same as beginner mode)
                if event.button == 3 and not level_completed and not game_over:
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
                                # Check if rotation is valid
                                w,h = (cheese_cols,cheese_rows) if pc['angle']%180==0 else (cheese_rows,cheese_cols)
                                tmp_img = pygame.transform.rotate(pc['img'], pc['angle'])
                                new_rect = tmp_img.get_rect(topleft=pc['rect'].topleft)
                                if not can_place_piece(new_rect, pc['angle'], placed_cheese, grid_origin, cell_size, grid_size, exclude_idx=idx):
                                    pc['angle'] = old  # Revert if invalid
                                else:
                                    pc['rect'] = new_rect
                                save_expert_level(level, placed_cheese, money, level_completed, game_over)
                                break

            elif event.type == pygame.MOUSEBUTTONUP and not level_completed and not game_over:
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
                            # Expert specific: check money and deduct cost
                            if money >= EXPERT_PIECE_COST:
                                placed_cheese.append({'img': cheese_imgs[dragging_idx], 'rect': new_rect.copy(), 'angle': ang})
                                cheese_used[dragging_idx] = True
                                money -= EXPERT_PIECE_COST
                            
                            # Check for game over - if no money and level not completed
                            if money < EXPERT_PIECE_COST and not level_completed:
                                game_over = True
                                if not played_failed_sound:
                                    failed_sound = pygame.mixer.Sound("assets/sounds/failed.mp3")
                                    failed_sound.play()
                                    played_failed_sound = True
                                    
                            save_expert_level(level, placed_cheese, money, level_completed, game_over)
                    
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
                            # Expert specific: moving pieces also costs money
                            if money >= EXPERT_PIECE_COST:
                                placed_cheese[dragging_placed_idx]['rect'] = new_rect.copy()
                                money -= EXPERT_PIECE_COST
                                
                                # Check for game over after moving - if no money and level not completed
                                if money < EXPERT_PIECE_COST and not level_completed:
                                    game_over = True
                                    if not played_failed_sound:
                                        failed_sound = pygame.mixer.Sound("assets/sounds/failed.mp3")
                                        failed_sound.play()
                                        played_failed_sound = True
                                
                                save_expert_level(level, placed_cheese, money, level_completed, game_over)
                            # If not enough money, piece stays in original position
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
