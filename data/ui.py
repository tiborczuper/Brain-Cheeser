import pygame
from config import *
from shared import get_font

# Simple UI screens extracted for cleanliness

def draw_centered_text(screen, text, y, size=40, color=(255,255,255)):
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
    screen.blit(surf, rect)

def draw_left_text(screen, text, x, y, size=20, color=(255,255,0)):
    font = get_font(size)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def how_to_play_screen():
    from assets.button import Button
    
    while True:
        screen = pygame.display.get_surface()
        screen.fill((0,0,0))  # Black background
        mouse_pos = pygame.mouse.get_pos()
        
        draw_left_text(screen, 'How to Play', 20, 30, 40, (255,255,0))
        
        lines = [
            '',
            'RULES:',
            '',
            'To solve each challenge, place all cheese puzzle',
            'pieces on the game board to form a large square',
            'slice of cheese, with mice peeking through the holes:',
            ' - Cheese pieces must not overlap mice or extend'
            ' beyond the edge of the grid.',
            ' - Empty holes are allowed when two cheese pieces with',
            ' cut-outs are placed side by side.',
            ' - Half holes in the middle of the cheese are',
            ' not permitted.',
            ' They are only allowed at the edge of the board.',
            ' - In Expert mode, placing a cheese slice deducts $10',
            ' from your starting budget. Plan your moves carefully!',
            'Each challenge has only one correct solution.',
            '',
            '',
            'CONTROLS:',
            '',
            ' - Drag and drop cheese pieces from the inventory',
            ' - To rotate the slice of cheese press right click',


        ]
        
        y = 80
        for line in lines:
            if line:  # Skip empty lines
                draw_left_text(screen, line, 20, y, 18, (255,255,0))
            y += 22
        
        # Back button
        back_btn = Button(image=None, pos=(SCREEN_WIDTH/2, SCREEN_HEIGHT-60), 
                         text_input="BACK", font=get_font(50), 
                         base_color=COLOR_BUTTON_BASE, hovering_color="red")
        back_btn.changeColor(mouse_pos)
        back_btn.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.checkForInput(mouse_pos):
                    return
        
        pygame.display.update()

