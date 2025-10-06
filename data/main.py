"""Belépési pont / menük.

Ebben a fájlban nincs játékmenet: a beginner és expert loop a game_core.py
modulban fut egységesen. Itt csak a menük, a némítás és a mentések törlése található meg.
"""

import pygame, sys, os
from config import *
from assets.button import Button
from shared import get_font
from ui import how_to_play_screen
from game_core import run_game_level
from beginner import BEGINNER_LEVEL_LOCKED_PIECES
from expert import EXPERT_LEVEL_LOCKED_PIECES

music_muted = False  # Menü szintű némítás

BEGINNER_LEVEL_COUNT = max(1, len(BEGINNER_LEVEL_LOCKED_PIECES))
EXPERT_LEVEL_COUNT = max(1, len(EXPERT_LEVEL_LOCKED_PIECES))


def reset_saves():
    """Összes .json mentés törlése a saves mappából."""
    removed = 0
    if not os.path.isdir(SAVE_DIR):
        return 0
    for name in os.listdir(SAVE_DIR):
        if name.endswith('.json'):
            try:
                os.remove(os.path.join(SAVE_DIR, name))
                removed += 1
            except Exception as e:
                print('[RESET ERROR]', e)
    print(f'[RESET] {removed} save file deleted')
    return removed

def levels_menu(mode):
    """Univerzális szintválasztó menu mindkét módhoz."""
    global music_muted
    if not pygame.mixer.get_busy() and not music_muted:
        menu_music.play(-1)
        
    title = f"{mode.upper()} LEVELS"
    level_count = BEGINNER_LEVEL_COUNT if mode == 'beginner' else EXPERT_LEVEL_COUNT
    
    while True:
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        
        title_text = get_font(60).render(title, True, COLOR_LEVEL_TEXT)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, 50)))
        
        # Level buttons létrehozása
        level_buttons = []
        start_y, spacing = 150, 120
        for i in range(level_count):
            btn = Button(
                image=pygame.image.load(QUIT_BG_IMAGE), 
                pos=(SCREEN_WIDTH/2, start_y + i*spacing),
                text_input=f"LEVEL {i+1}", 
                font=get_font(35), 
                base_color=COLOR_BUTTON_BASE, 
                hovering_color=COLOR_BUTTON_HOVER
            )
            level_buttons.append(btn)
        
        back_button = Button(
            image=None, pos=(100, SCREEN_HEIGHT-50),
            text_input="BACK", font=get_font(35), 
            base_color=COLOR_BUTTON_BASE, hovering_color="Red"
        )
        
        # Buttons kirajzolása és event handling
        for btn in level_buttons + [back_button]:
            btn.changeColor(mouse_pos)
            btn.update(screen)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Level button ellenőrzés
                for idx, btn in enumerate(level_buttons):
                    if btn.checkForInput(mouse_pos):
                        run_game_level(mode, idx + 1)
                        break
                        
                if back_button.checkForInput(mouse_pos):
                    return
                    
        pygame.display.update()

def main_menu():
    """Főmenü: mód választás, némítás, reset, how-to-play."""
    global music_muted
    if not pygame.mixer.get_busy() and not music_muted:
        menu_music.play(-1)
    while True:
        screen.blit(background, (0,0))
        mouse_pos = pygame.mouse.get_pos()
        title = get_font(50).render("BRAIN CHEESER", True, COLOR_LEVEL_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH/2, 35)))
        madeby = get_font(20).render("by Czuper Tibor", True, COLOR_LEVEL_TEXT)
        screen.blit(madeby, madeby.get_rect(center=(SCREEN_WIDTH/2, 70)))
        
        # Verziószám a jobb felső sarokba
        version_text = get_font(16).render(GAME_VERSION, True, COLOR_LEVEL_TEXT)
        screen.blit(version_text, (SCREEN_WIDTH - 110, 10))

        beginner_btn = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 200), text_input="BEGINNER", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        expert_btn   = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 325), text_input="EXPERT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        how_to_play_btn = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 450), text_input="HOW TO PLAY", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        quit_btn     = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, 575), text_input="QUIT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="red")
        reset_btn = Button(image=None, pos=(180, SCREEN_HEIGHT-40), text_input="RESET ALL LEVELS", font=get_font(20), base_color="#ff0000", hovering_color=COLOR_BUTTON_HOVER)
        mute_text = "MUSIC ON" if music_muted else "MUSIC OFF"
        mute_btn = Button(image=None, pos=(SCREEN_WIDTH-100, SCREEN_HEIGHT-40), text_input=mute_text, font=get_font(20), base_color="#ff2222", hovering_color="#ff5555")

        for b in (beginner_btn, expert_btn, quit_btn, how_to_play_btn, reset_btn, mute_btn):
            b.changeColor(mouse_pos); b.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_btn.checkForInput(mouse_pos):
                    reset_saves()
                if mute_btn.checkForInput(mouse_pos):
                    music_muted = not music_muted
                    if music_muted:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
                        if not pygame.mixer.get_busy():
                            menu_music.play(-1)
                if beginner_btn.checkForInput(mouse_pos):
                    levels_menu('beginner')
                if expert_btn.checkForInput(mouse_pos):
                    levels_menu('expert')
                if how_to_play_btn.checkForInput(mouse_pos):
                    how_to_play_screen()
                if quit_btn.checkForInput(mouse_pos):
                    pygame.quit(); sys.exit()
        pygame.display.update()

if __name__ == '__main__':
    main_menu()