"""Közös játék motor mindkét módhoz (beginner és expert)."""

import pygame, sys
from config import *
from assets.button import Button
from shared import (draw_grid, draw_mice, can_place_piece, check_level_completion,
                    init_cheese_inventory, get_font, get_cheese_inventory_position,
                    draw_placement_preview)


class GameCore:
    """Közös játéklogika mindkét mód számára."""
    
    def __init__(self, mode, level):
        self.mode = mode  # 'beginner' vagy 'expert'
        self.level = level
        self.grid_size = GRID_SIZE
        self.cell_size = CELL_SIZE
        self.grid_origin = (350, SCREEN_HEIGHT//2 - (self.grid_size*self.cell_size)//2)
        
        # Mode-specifikus importok
        if mode == 'beginner':
            from beginner import (get_beginner_level_mice, get_beginner_completion_targets,
                                apply_beginner_locked_pieces, load_beginner_level, 
                                save_beginner_level, get_cheese_images)
            self.get_mice = get_beginner_level_mice
            self.get_targets = get_beginner_completion_targets
            self.apply_locked = apply_beginner_locked_pieces
            self.load_level = load_beginner_level
            self.save_level = save_beginner_level
            self.cheese_imgs = get_cheese_images()
        else:  # expert
            from expert import (get_expert_level_mice, get_expert_completion_targets,
                              apply_expert_locked_pieces, load_expert_level,
                              save_expert_level, get_cheese_images)
            self.get_mice = get_expert_level_mice
            self.get_targets = get_expert_completion_targets
            self.apply_locked = apply_expert_locked_pieces
            self.load_level = load_expert_level
            self.save_level = save_expert_level
            self.cheese_imgs = get_cheese_images()
        
        self.init_game_state()
        
    def init_game_state(self):
        """Játékállapot inicializálása."""
        self.mice = self.get_mice(self.level)
        self.targets = self.get_targets(self.level)
        self.cheese_rects, self.cheese_angles, self.cheese_used = init_cheese_inventory(self.cheese_imgs)
        
        # Mode-specifikus betöltés
        if self.mode == 'beginner':
            saved_level, saved_pieces = self.load_level()
            self.placed_cheese = saved_pieces if saved_level == self.level else []
            self.money = None
            self.game_over = False
        else:  # expert
            saved_level, saved_pieces, saved_money, saved_completed, saved_game_over = self.load_level(self.level)
            self.placed_cheese = saved_pieces
            self.money = saved_money if saved_money is not None else EXPERT_LEVEL_START_MONEY.get(self.level, 100)
            self.game_over = saved_game_over
            self.level_completed = saved_completed
        
        # Közös állapot változók
        if self.mode == 'beginner':
            self.level_completed = False
        self.played_completion_sound = self.level_completed if self.mode == 'expert' else False
        self.played_failed_sound = self.game_over if self.mode == 'expert' else False
        
        # Locked pieces alkalmazása
        self.apply_locked(self.level, self.placed_cheese, self.cheese_imgs, self.grid_origin, self.cell_size)
        
        # Használt inventory pieces megjelölése
        self.mark_used_inventory_pieces()
        
        # Drag state
        self.dragging_idx = None
        self.dragging_placed_idx = None
        self.offset = (0, 0)
        
    def mark_used_inventory_pieces(self):
        """Elhelyezett pieces alapján megjelöli a használt inventory elemeket."""
        for pc in self.placed_cheese:
            for i, im in enumerate(self.cheese_imgs):
                if im == pc['img']:
                    self.cheese_used[i] = True
                    break
    
    def handle_piece_placement(self, mouse_pos):
        """Inventory piece elhelyezése a táblán."""
        if self.dragging_idx is None:
            return
            
        mx, my = mouse_pos
        ang = self.cheese_angles[self.dragging_idx]
        cheese_cols, cheese_rows = CHEESE_COLS, CHEESE_ROWS
        w, h = (cheese_cols, cheese_rows) if ang % 180 == 0 else (cheese_rows, cheese_cols)
        
        tmp = pygame.transform.rotate(self.cheese_imgs[self.dragging_idx], ang)
        tmp_rect = tmp.get_rect(center=(mx, my))
        cx, cy = tmp_rect.center
        gx = int((cx - self.grid_origin[0]) / self.cell_size)
        gy = int((cy - self.grid_origin[1]) / self.cell_size)
        
        if 0 <= gx <= self.grid_size - w and 0 <= gy <= self.grid_size - h:
            sx = self.grid_origin[0] + gx * self.cell_size
            sy = self.grid_origin[1] + gy * self.cell_size
            draw_img = pygame.transform.rotate(self.cheese_imgs[self.dragging_idx], ang)
            new_rect = draw_img.get_rect(topleft=(sx, sy))
            
            if can_place_piece(new_rect, ang, self.placed_cheese, self.grid_origin, self.cell_size, self.grid_size):
                # Expert mode: pénz ellenőrzés
                if self.mode == 'expert' and self.money < EXPERT_PIECE_COST:
                    return False
                    
                self.placed_cheese.append({
                    'img': self.cheese_imgs[self.dragging_idx], 
                    'rect': new_rect.copy(), 
                    'angle': ang
                })
                self.cheese_used[self.dragging_idx] = True
                
                if self.mode == 'expert':
                    self.money -= EXPERT_PIECE_COST
                    self.check_game_over()
                    
                self.save_game_state()
                return True
        return False
    
    def handle_placed_piece_move(self, mouse_pos):
        """Már elhelyezett piece mozgatása."""
        if self.dragging_placed_idx is None:
            return
            
        mx, my = mouse_pos
        pc = self.placed_cheese[self.dragging_placed_idx]
        ang = pc['angle']
        cheese_cols, cheese_rows = CHEESE_COLS, CHEESE_ROWS
        w, h = (cheese_cols, cheese_rows) if ang % 180 == 0 else (cheese_rows, cheese_cols)
        
        tmp = pygame.transform.rotate(pc['img'], ang)
        tmp_rect = tmp.get_rect(center=(mx, my))
        cx, cy = tmp_rect.center
        gx = int((cx - self.grid_origin[0]) / self.cell_size)
        gy = int((cy - self.grid_origin[1]) / self.cell_size)
        
        if 0 <= gx <= self.grid_size - w and 0 <= gy <= self.grid_size - h:
            sx = self.grid_origin[0] + gx * self.cell_size
            sy = self.grid_origin[1] + gy * self.cell_size
            draw_img = pygame.transform.rotate(pc['img'], ang)
            new_rect = draw_img.get_rect(topleft=(sx, sy))
            
            if can_place_piece(new_rect, ang, self.placed_cheese, self.grid_origin, 
                             self.cell_size, self.grid_size, exclude_idx=self.dragging_placed_idx):
                # Expert mode: mozgatás is pénzbe kerül
                if self.mode == 'expert' and self.money < EXPERT_PIECE_COST:
                    return
                    
                self.placed_cheese[self.dragging_placed_idx]['rect'] = new_rect.copy()
                
                if self.mode == 'expert':
                    self.money -= EXPERT_PIECE_COST
                    self.check_game_over()
                    
                self.save_game_state()
        else:
            # Piece eltávolítása a tábláról
            if not pc.get('locked'):
                removed = self.placed_cheese.pop(self.dragging_placed_idx)
                for i, im in enumerate(self.cheese_imgs):
                    if im == removed['img']:
                        self.cheese_used[i] = False
                        self.cheese_angles[i] = 0
                        self.cheese_rects[i].topleft = get_cheese_inventory_position(i, self.cheese_imgs)
                        break
    
    def check_completion(self):
        """Szint teljesítésének ellenőrzése."""
        if not self.level_completed and check_level_completion(
            self.placed_cheese, self.cheese_imgs, self.targets, self.grid_origin, self.cell_size
        ):
            self.level_completed = True
            self.save_game_state()
            return True
        return False
    
    def check_game_over(self):
        """Game over ellenőrzése (csak expert módban)."""
        if self.mode == 'expert' and self.money < EXPERT_PIECE_COST and not self.level_completed:
            self.game_over = True
    
    def save_game_state(self):
        """Játékállapot mentése."""
        if self.mode == 'beginner':
            self.save_level(self.level, self.placed_cheese)
        else:  # expert
            self.save_level(self.level, self.placed_cheese, self.money, self.level_completed, self.game_over)
    
    def reset_level(self):
        """Szint alaphelyzetbe állítása."""
        self.placed_cheese = []
        self.cheese_rects, self.cheese_angles, self.cheese_used = init_cheese_inventory(self.cheese_imgs)
        self.apply_locked(self.level, self.placed_cheese, self.cheese_imgs, self.grid_origin, self.cell_size)
        self.mark_used_inventory_pieces()
        
        self.level_completed = False
        self.played_completion_sound = False
        
        if self.mode == 'expert':
            self.game_over = False
            self.played_failed_sound = False
            self.money = EXPERT_LEVEL_START_MONEY.get(self.level, 100)
    
    def draw_game(self, screen, mouse_pos):
        """Játék kirajzolása."""
        # Háttér és grid
        if self.mode == 'beginner':
            screen.fill("black")
        else:
            screen.fill((20, 30, 40))
            
        draw_grid(screen, self.grid_size, self.cell_size, self.grid_origin)
        
        # Header
        if self.mode == 'beginner':
            header_text = f"LEVEL {self.level}  |  MICE: {len(self.mice)}"
            header = get_font(40).render(header_text, True, COLOR_LEVEL_TEXT)
        else:
            header_text = f"EXPERT LEVEL {self.level} | MICE: {len(self.mice)}"
            header = get_font(34).render(header_text, True, COLOR_LEVEL_TEXT)
        screen.blit(header, header.get_rect(center=(SCREEN_WIDTH/2, 40)))
        
        # Expert mode: pénz kijelzés
        if self.mode == 'expert':
            money_text = get_font(40).render(f"${self.money}", True, COLOR_LEVEL_TEXT)
            grid_center_x = self.grid_origin[0] + (self.grid_size * self.cell_size) // 2
            grid_bottom_y = self.grid_origin[1] + (self.grid_size * self.cell_size) + 50
            screen.blit(money_text, money_text.get_rect(center=(grid_center_x, grid_bottom_y)))
        
        draw_mice(screen, self.mice, self.grid_origin, self.cell_size)
        
        # Elhelyezett pieces
        for i, pc in enumerate(self.placed_cheese):
            draw_img = pygame.transform.rotate(pc['img'], pc['angle'])
            rect = draw_img.get_rect(topleft=pc['rect'].topleft)
            if self.dragging_placed_idx == i:
                mx, my = mouse_pos
                rect.topleft = (mx - self.offset[0], my - self.offset[1])
            screen.blit(draw_img, rect)
        
        # Inventory pieces
        for i, img in enumerate(self.cheese_imgs):
            if self.cheese_used[i]:
                continue
            draw_img = pygame.transform.rotate(img, self.cheese_angles[i])
            rect = draw_img.get_rect(topleft=self.cheese_rects[i].topleft)
            if self.dragging_idx == i:
                mx, my = mouse_pos
                rect.topleft = (mx - self.offset[0], my - self.offset[1])
            screen.blit(draw_img, rect)
            self.cheese_rects[i] = rect.copy()
        
        # Placement preview
        if self.dragging_idx is not None:
            draw_placement_preview(screen, mouse_pos, self.cheese_imgs[self.dragging_idx], 
                                 self.cheese_angles[self.dragging_idx], self.grid_origin, 
                                 self.cell_size, self.grid_size, self.placed_cheese)
        elif self.dragging_placed_idx is not None:
            pc = self.placed_cheese[self.dragging_placed_idx]
            draw_placement_preview(screen, mouse_pos, pc['img'], pc['angle'], 
                                 self.grid_origin, self.cell_size, self.grid_size, 
                                 self.placed_cheese, self.dragging_placed_idx)
    
    def draw_ui(self, screen, mouse_pos):
        """UI elemek kirajzolása."""
        # Buttons
        back_btn = Button(
            image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60), 
            text_input="BACK", font=get_font(50), 
            base_color=COLOR_BUTTON_BASE, hovering_color="red"
        )
        
        # Reset button - expert módban csak completed/game over állapotban aktív
        if self.mode == 'expert':
            reset_active = (self.level_completed or self.game_over)
            reset_color = COLOR_RESET_BUTTON if reset_active else (100, 100, 100)
            reset_hover = COLOR_BUTTON_HOVER if reset_active else reset_color
        else:
            reset_active = True
            reset_color = COLOR_RESET_BUTTON
            reset_hover = COLOR_BUTTON_HOVER
            
        reset_btn = Button(
            image=None, pos=(SCREEN_WIDTH-120, SCREEN_HEIGHT-60), 
            text_input="RESET", font=get_font(40), 
            base_color=reset_color, hovering_color=reset_hover
        )
        
        for btn in (back_btn, reset_btn):
            btn.changeColor(mouse_pos)
            btn.update(screen)
            
        # Status messages
        if self.level_completed:
            comp = get_font(70).render("COMPLETED!", True, COLOR_COMPLETION)
            screen.blit(comp, comp.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2 - 225)))
            if not self.played_completion_sound:
                completed_sound = pygame.mixer.Sound(COMPLETED_SOUND)
                completed_sound.play()
                self.played_completion_sound = True
        elif self.mode == 'expert' and self.game_over:
            go = get_font(70).render("GAME OVER", True, (200, 40, 40))
            screen.blit(go, go.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT//2 - 225)))
            if not self.played_failed_sound:
                failed_sound = pygame.mixer.Sound("assets/sounds/failed.mp3")
                failed_sound.play()
                self.played_failed_sound = True
        
        return back_btn, reset_btn, reset_active


def run_game_level(mode, level):
    """Univerzális játék futtatás beginner és expert módhoz."""
    game = GameCore(mode, level)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # Completion ellenőrzés
        if game.mode == 'beginner' or (game.mode == 'expert' and not game.game_over):
            game.check_completion()
        
        # Kirajzolás
        game.draw_game(screen, mouse_pos)
        back_btn, reset_btn, reset_active = game.draw_ui(screen, mouse_pos)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Buttons
                if back_btn.checkForInput(mouse_pos):
                    game.save_game_state()
                    return
                    
                if reset_active and reset_btn.checkForInput(mouse_pos):
                    game.reset_level()
                    continue
                
                # Game logic - csak ha nincs befejezve (beginner) vagy nincs game over (expert)
                if (game.mode == 'beginner' and game.level_completed) or \
                   (game.mode == 'expert' and (game.level_completed or game.game_over)):
                    continue
                
                # Drag start
                if event.button == 1:
                    # Placed pieces check (fordított sorrendben)
                    for idx in reversed(range(len(game.placed_cheese))):
                        pc = game.placed_cheese[idx]
                        if pc['rect'].collidepoint(event.pos) and not pc.get('locked'):
                            game.dragging_placed_idx = idx
                            game.offset = (event.pos[0] - pc['rect'].x, event.pos[1] - pc['rect'].y)
                            break
                    else:
                        # Inventory pieces check
                        for i, rect in enumerate(game.cheese_rects):
                            if game.cheese_used[i]:
                                continue
                            if rect.collidepoint(event.pos):
                                game.dragging_idx = i
                                game.offset = (event.pos[0] - rect.x, event.pos[1] - rect.y)
                                break
                
                # Rotate with right click
                elif event.button == 3:
                    rotated = False
                    # Inventory pieces
                    for i, rect in enumerate(game.cheese_rects):
                        if game.cheese_used[i]:
                            continue
                        if rect.collidepoint(event.pos):
                            game.cheese_angles[i] = (game.cheese_angles[i] - 90) % 360
                            rotated = True
                            break
                    
                    if not rotated:
                        # Placed pieces
                        for idx, pc in enumerate(game.placed_cheese):
                            if pc['rect'].collidepoint(event.pos) and not pc.get('locked'):
                                old_angle = pc['angle']
                                pc['angle'] = (pc['angle'] - 90) % 360
                                
                                # Rotation validity check
                                if not can_place_piece(pc['rect'], pc['angle'], game.placed_cheese, 
                                                     game.grid_origin, game.cell_size, game.grid_size, 
                                                     exclude_idx=idx):
                                    pc['angle'] = old_angle  # Revert if invalid
                                else:
                                    game.save_game_state()
                                break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if (game.mode == 'beginner' and not game.level_completed) or \
                   (game.mode == 'expert' and not game.level_completed and not game.game_over):
                    
                    # Release inventory piece
                    if game.dragging_idx is not None:
                        if game.handle_piece_placement(mouse_pos):
                            pass  # Successfully placed
                        # Reset position
                        game.cheese_rects[game.dragging_idx].topleft = get_cheese_inventory_position(
                            game.dragging_idx, game.cheese_imgs)
                        game.dragging_idx = None
                    
                    # Release placed piece
                    if game.dragging_placed_idx is not None:
                        game.handle_placed_piece_move(mouse_pos)
                        game.dragging_placed_idx = None
            
            elif event.type == pygame.MOUSEMOTION:
                if (game.mode == 'beginner' and not game.level_completed) or \
                   (game.mode == 'expert' and not game.level_completed):
                    
                    if game.dragging_idx is not None:
                        mx, my = event.pos
                        game.cheese_rects[game.dragging_idx].topleft = (mx - game.offset[0], my - game.offset[1])
                    
                    if game.dragging_placed_idx is not None:
                        mx, my = event.pos
                        game.placed_cheese[game.dragging_placed_idx]['rect'].topleft = (mx - game.offset[0], my - game.offset[1])
        
        pygame.display.update()