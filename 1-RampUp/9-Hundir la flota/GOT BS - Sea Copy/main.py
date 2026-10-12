# main.py
import pygame
import sys
import math
import os

# Professional alias import pattern ensuring clean variable lookup
import variables as v
from classes import Board
from functions import place_ships_randomly, get_lannister_ai_coordinates

# 1. Initialize Pygame engine hardware modules
pygame.init()

# 2. Centering the application window context during fallback scaling
os.environ['SDL_VIDEO_CENTERED'] = '1'

# 3. Dynamic layout scaling based on native hardware monitor resolution
monitor_info = pygame.display.Info()
screen_max_width = monitor_info.current_w
screen_max_height = monitor_info.current_h

# Math calculation to determine massive grid bounds adaptive sizing (75% of screen height)
CELL_SIZE = int((screen_max_height * 0.75) / v.BOARD_SIZE)
BOARD_WIDTH = CELL_SIZE * v.BOARD_SIZE

# --- METRIC CALCULATION FOR PERFECT CENTERING ---
TACTICAL_GAP = CELL_SIZE * 1.5
TOTAL_FLEET_WIDTH = (BOARD_WIDTH * 2) + TACTICAL_GAP

START_X = (screen_max_width - TOTAL_FLEET_WIDTH) // 2
START_Y = (screen_max_height - BOARD_WIDTH) // 2

# 4. Instantiate adaptive canvas window forced to Fullscreen real scale mode
screen = pygame.display.set_mode((screen_max_width, screen_max_height), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("BATTLE OF THE NARROW SEA")
clock = pygame.time.Clock()

# 5. Proportional responsive fonts setup linked to calculated cell bounds
font_title = pygame.font.SysFont("serif", int(CELL_SIZE * 0.7), bold=True)
font_sub = pygame.font.SysFont("serif", int(CELL_SIZE * 0.4), italic=True)
font_ui = pygame.font.SysFont("serif", int(CELL_SIZE * 0.35), bold=True)

# 6. Global sprite activation flags locked for native real image loading
USING_SPRITES = True  
USING_OCEAN_SPRITE = False
USING_SHIPS_SPRITES = False
USING_FX_SPRITES = False

# Global object to hold your premium seamless sea texture
img_bg_ocean = None
TILE_SIZE = 512  # CALIBRACIÓN HD: 512px mantiene la nitidez y los reflejos cristalinos de tu imagen

# 7. BULLETPROOF ABSOLUTE PATH RESOLUTION FOR YOUR NEW SEAMLESS IMAGE
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
    ocean_path = os.path.join(ASSETS_DIR, "background_ocean.png")
    
    # Load your pristine, watermark-free sea background from ChatGPT
    raw_ocean = pygame.image.load(ocean_path).convert_alpha()
    img_bg_ocean = pygame.transform.scale(raw_ocean, (TILE_SIZE, TILE_SIZE))
    
    USING_OCEAN_SPRITE = True
    print("SUCCESS: ¡La espectacular textura marina de ChatGPT ha sido cargada en HD!")
except Exception as e:
    print(f"Warning: Ocean sprite missing or path issue. Fallback active. Error: {e}")

# Prevent NameError crashes on uninitialized pointers
img_ship_player_base = None
img_ship_ai_base = None
img_fire = None
img_miss = None


def draw_scrolling_ocean(surface):
    """
    Fills the entire monitor canvas with your custom seamless water texture.
    Smooth diagonal drift creates a premium, organic underwater current flow with zero seams.
    """
    if not USING_OCEAN_SPRITE or img_bg_ocean is None:
        surface.fill(v.COLOR_SEA_BACKGROUND)
        return

    # SLOW PACING: Controlamos el flujo de las olas dividiendo los milisegundos del sistema
    time_ms = pygame.time.get_ticks()
    scroll_x = int((time_ms / 160) % TILE_SIZE)
    scroll_y = int((time_ms / 200) % TILE_SIZE)

    # Seamless tiling layout loops covering the absolute monitor resolution space
    for x in range(-TILE_SIZE, surface.get_width() + TILE_SIZE, TILE_SIZE):
        for y in range(-TILE_SIZE, surface.get_height() + TILE_SIZE, TILE_SIZE):
            surface.blit(img_bg_ocean, (x + scroll_x, y + scroll_y))


def draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """Clean placeholder function for future asset mapping integration."""
    pass


def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """Renders high-fidelity tactical grid layers with thick, semi-transparent white lines and no gaps."""
    time_factor = pygame.time.get_ticks() / 400.0
    
    # --- LAYER 1 & 2: Fallback block rendering for ships if ship images are missing ---
    if not USING_SHIPS_SPRITES:
        for row in range(v.BOARD_SIZE):
            for col in range(v.BOARD_SIZE):
                tile_x = x_offset + (col * CELL_SIZE)
                tile_y = y_offset + (row * CELL_SIZE)
                tile_state = board.ship_matrix[row][col]
                
                # If there's a ship intact, paint its block over the moving water layer
                if tile_state == v.TILE_SHIP and (reveal_ships or is_player):
                    float_y = math.sin(time_factor + row) * 4.0
                    floating_rect = pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 8, CELL_SIZE - 8)
                    ship_core_color = v.COLOR_TARGARYEN_SHIP if is_player else v.COLOR_LANNISTER_SHIP
                    pygame.draw.rect(surface, ship_core_color, floating_rect)
    else:
        draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player)

    # --- LAYER 3: Combat states and hits overlays ---
    for row in range(v.BOARD_SIZE):
        for col in range(v.BOARD_SIZE):
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            tile_state = board.ship_matrix[row][col]
            
            if tile_state == v.TILE_MISS:
                if USING_FX_SPRITES and img_miss is not None:
                    surface.blit(img_miss, (tile_x, tile_y))
                else:
                    pygame.draw.circle(surface, v.COLOR_MISS, (tile_x + CELL_SIZE//2, tile_y + CELL_SIZE//2), CELL_SIZE//4)
                    
            elif tile_state in [v.TILE_HIT, v.TILE_SUNK]:
                if USING_FX_SPRITES and img_fire is not None:
                    surface.blit(img_fire, (tile_x, tile_y))
                    if tile_state == v.TILE_SUNK:
                        dark_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        dark_overlay.fill((0, 0, 0, 150))
                        surface.blit(dark_overlay, (tile_x, tile_y))
                else:
                    tile_color = v.COLOR_DRACARYS_FIRE if tile_state == v.TILE_HIT else (60, 60, 60)
                    rect = pygame.Rect(tile_x, tile_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, tile_color, rect)

    # --- LAYER 4: PREMIUM TRANSPARENT WHITE REJILLA ---
    grid_overlay = pygame.Surface((BOARD_WIDTH + 4, BOARD_WIDTH + 4), pygame.SRCALPHA)
    alpha_white = (255, 255, 255, 120)
    line_thickness = 3

    for col in range(v.BOARD_SIZE + 1):
        x_pos = col * CELL_SIZE
        pygame.draw.line(grid_overlay, alpha_white, (x_pos, 0), (x_pos, BOARD_WIDTH), line_thickness)

    for row in range(v.BOARD_SIZE + 1):
        y_pos = row * CELL_SIZE
        pygame.draw.line(grid_overlay, alpha_white, (0, y_pos), (BOARD_WIDTH, y_pos), line_thickness)

    surface.blit(grid_overlay, (x_offset, y_offset))


def draw_menu():
    """Renders the minimalistic main menu interface with text-only buttons over the endless sea."""
    title_text = font_title.render("BATTLE OF THE NARROW SEA", True, v.COLOR_TEXT)
    subtitle_text = font_sub.render("Targaryen & Stark vs. Lannister Fleet", True, v.COLOR_TEXT)
    
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
    sub_rect = subtitle_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4 + 50))
    
    screen.blit(title_text, title_rect)
    screen.blit(subtitle_text, sub_rect)
    
    text_play = font_ui.render("START BATTLE", True, v.COLOR_TEXT)
    text_exit = font_ui.render("LEAVE GAME", True, v.COLOR_TEXT)
    
    play_btn = text_play.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    exit_btn = text_exit.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 70))
    
    play_btn.inflate_ip(40, 20)
    exit_btn.inflate_ip(40, 20)
    
    screen.blit(text_play, text_play.get_rect(center=play_btn.center))
    screen.blit(text_exit, text_exit.get_rect(center=exit_btn.center))
    
    return play_btn, exit_btn


def main():
    # Setup state managers loop variables
    game_state = "MENU"
    
    # Instantiate structural battle boards
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    place_ships_randomly(player_board, v.FLEET_INVENTORY)
    place_ships_randomly(ai_board, v.FLEET_INVENTORY)
    
    player_turn = True
    game_over = False
    winner_text = ""
    cheat_mode = False

    # Centered board layouts assignments using calculated START_X and START_Y
    player_x_offset = START_X
    ai_x_offset = START_X + BOARD_WIDTH + TACTICAL_GAP
    boards_y_offset = START_Y

    while True:
        # --- STATE MACHINE CONTROL PANEL ---
        if game_state == "MENU":
            screen.fill(v.COLOR_SEA_BACKGROUND)
            draw_scrolling_ocean(screen)
            
            play_button, exit_button = draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.collidepoint(mouse_pos):
                        game_state = "GAME"
                    elif exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                        
        elif game_state == "GAME":
            screen.fill(v.COLOR_SEA_BACKGROUND)
            draw_scrolling_ocean(screen)
            
            player_label = font_ui.render("TEAM BLACK (TARGARYEN & STARK)", True, v.COLOR_TEXT)
            ai_label = font_ui.render("TEAM GREEN (LANNISTER AI)", True, v.COLOR_TEXT)
            screen.blit(player_label, (player_x_offset, boards_y_offset - 30))
            screen.blit(ai_label, (ai_x_offset, boards_y_offset - 30))
            
            draw_grid(screen, player_x_offset, boards_y_offset, player_board, is_player=True)
            draw_grid(screen, ai_x_offset, boards_y_offset, ai_board, reveal_ships=cheat_mode, is_player=False)
            
            if game_over:
                if winner_text == "PLAYER (TARGARYEN)":
                    victory_message = "VICTORY! THE IRON THRONE BELONGS TO THE TARGARYENS!"
                    text_color = (255, 215, 0)
                else:
                    victory_message = "DEFEAT... A LANNISTER ALWAYS PAYS HIS DEBTS!"
                    text_color = (220, 20, 60)
                
                end_banner = font_ui.render(victory_message, True, text_color)
                text_rect = end_banner.get_rect(center=(screen.get_width() // 2, screen.get_height() - 45))
                screen.blit(end_banner, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_k:
                        cheat_mode = not cheat_mode
                        print(f"DEBUG: Lannister ships layout reveal state toggled to: {cheat_mode}")
                        
                if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                    mx, my = event.pos
                    
                    if ai_x_offset <= mx < ai_x_offset + BOARD_WIDTH and boards_y_offset <= my < boards_y_offset + BOARD_WIDTH:
                        target_x = int((mx - ai_x_offset) // CELL_SIZE)
                        target_y = int((my - boards_y_offset) // CELL_SIZE)
                        
                        shot_result, repeat_turn = ai_board.receive_shot(target_x, target_y)
                        
                        if shot_result != "ALREADY_SHOT":
                            player_board.register_own_shot(target_x, target_y, shot_result)
                            print(f"Player fired at ({target_x}, {target_y}) -> {shot_result}")
                            
                            if not ai_board.has_ships_alive():
                                game_over = True
                                winner_text = "PLAYER (TARGARYEN)"
                                
                            player_turn = repeat_turn

            if not player_turn and not game_over:
                pygame.time.wait(600)
                ai_x, ai_y = get_lannister_ai_coordinates(player_board)
                
                shot_result, repeat_turn = player_board.receive_shot(ai_x, ai_y)
                ai_board.register_own_shot(ai_x, ai_y, shot_result)
                print(f"Lannister AI fired at ({ai_x}, {ai_y}) -> {shot_result}")
                
                if not player_board.has_ships_alive():
                    game_over = True
                    winner_text = "LANNISTER"
                    
                player_turn = not repeat_turn

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
