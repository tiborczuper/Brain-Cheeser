"""Belépési pont / menük.

Ebben a fájlban nincs játékmenet: a beginner és expert loop külön modulokban
(game_beginner.py / game_expert.py) futnak. Itt csak a menük, a némítás és a
mentések törlése található meg.
"""

import pygame, sys, os
from config import *
from assets.button import Button
from shared import get_font
from ui import how_to_play_screen
from game_beginner import run_beginner_level
from game_expert import run_expert_level
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

def beginner_levels_menu():
    """Beginner szintválasztó – run_beginner_level hívásával indítja a kiválasztott szintet."""
    global music_muted
    if not pygame.mixer.get_busy() and not music_muted:
        menu_music.play(-1)
    while True:
        screen.fill((0, 0, 0))  # Black background
        mouse_pos = pygame.mouse.get_pos()
        title_text = get_font(60).render("BEGINNER LEVELS", True, COLOR_LEVEL_TEXT)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, 50)))
        level_buttons = []
        start_y = 150; spacing = 120
        for i in range(BEGINNER_LEVEL_COUNT):
            btn = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, start_y + i*spacing),
                         text_input=f"LEVEL {i+1}", font=get_font(35), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
            level_buttons.append(btn)
        back_button = Button(image=None, pos=(100, SCREEN_HEIGHT-50),
                              text_input="BACK", font=get_font(35), base_color=COLOR_BUTTON_BASE, hovering_color="Red")
        for b in level_buttons + [back_button]:
            b.changeColor(mouse_pos); b.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, b in enumerate(level_buttons):
                    if b.checkForInput(mouse_pos):
                        run_beginner_level(idx+1)  # blokkol amíg vissza nem tér
                if back_button.checkForInput(mouse_pos):
                    return
        pygame.display.update()

def expert_levels_menu():
    """Expert szintválasztó – run_expert_level hívásával indítja a kiválasztott szintet."""
    global music_muted
    if not pygame.mixer.get_busy() and not music_muted:
        menu_music.play(-1)
    while True:
        screen.fill((0, 0, 0))  # Black background
        mouse_pos = pygame.mouse.get_pos()
        title_text = get_font(60).render("EXPERT LEVELS", True, COLOR_LEVEL_TEXT)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, 50)))
        level_buttons = []
        start_y = 150; spacing = 120
        for i in range(EXPERT_LEVEL_COUNT):
            btn = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, start_y + i*spacing),
                         text_input=f"LEVEL {i+1}", font=get_font(35), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
            level_buttons.append(btn)
        back_button = Button(image=None, pos=(100, SCREEN_HEIGHT-50),
                              text_input="BACK", font=get_font(35), base_color=COLOR_BUTTON_BASE, hovering_color="Red")
        for btn in level_buttons + [back_button]:
            btn.changeColor(mouse_pos); btn.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn in enumerate(level_buttons):
                    if btn.checkForInput(mouse_pos):
                        run_expert_level(idx+1)
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

        beginner_btn = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 200), text_input="BEGINNER", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        expert_btn   = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 325), text_input="EXPERT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        how_to_play_btn = Button(image=pygame.image.load(PLAY_BG_IMAGE), pos=(SCREEN_WIDTH/2, 450), text_input="HOW TO PLAY", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color=COLOR_BUTTON_HOVER)
        quit_btn     = Button(image=pygame.image.load(QUIT_BG_IMAGE), pos=(SCREEN_WIDTH/2, 575), text_input="QUIT", font=get_font(50), base_color=COLOR_BUTTON_BASE, hovering_color="red")
        reset_btn = Button(image=None, pos=(180, SCREEN_HEIGHT-40), text_input="RESET ALL LEVELS", font=get_font(20), base_color="#ff0000", hovering_color=COLOR_BUTTON_HOVER)
        mute_text = "UNMUTE" if music_muted else "MUTE"
        mute_btn = Button(image=None, pos=(SCREEN_WIDTH-80, SCREEN_HEIGHT-40), text_input=mute_text, font=get_font(20), base_color="#ff2222", hovering_color="#ff5555")

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
                    beginner_levels_menu()
                if expert_btn.checkForInput(mouse_pos):
                    expert_levels_menu()
                if how_to_play_btn.checkForInput(mouse_pos):
                    how_to_play_screen()
                if quit_btn.checkForInput(mouse_pos):
                    pygame.quit(); sys.exit()
        pygame.display.update()

if __name__ == '__main__':
    main_menu()