# main.py
import pygame
import sys
import math
from variables import (
    BOARD_SIZE, TILE_WATER, TILE_SHIP, TILE_MISS, TILE_HIT, TILE_SUNK,
    FLEET_INVENTORY, COLOR_WATER, COLOR_MISS, COLOR_TARGARYEN_SHIP,
    COLOR_LANNISTER_SHIP, COLOR_DRACARYS_FIRE, COLOR_TEXT
)
from classes import Board
from functions import place_ships_randomly, get_lannister_ai_coordinates

# Initialize Pygame engine
pygame.init()
pygame.display.set_caption("PROJECT X: Battle of the Narrow Sea")

# Screen setup dimensions
CELL_SIZE = 40
MARGIN = 40
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE
SCREEN_WIDTH = (BOARD_WIDTH * 2) + (MARGIN * 3)
SCREEN_HEIGHT = BOARD_WIDTH + (MARGIN * 3)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Fonts setup
font_title = pygame.font.SysFont("serif", 36, bold=True)
font_sub = pygame.font.SysFont("serif", 20, italic=True)
font_ui = pygame.font.SysFont("serif", 18, bold=True)

def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """Renders a 10x10 tactical board grid with high contrast and flotation offsets."""
    time_factor = pygame.time.get_ticks() / 400.0  # Controls floating speed
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            
            tile_color = COLOR_WATER
            tile_state = board.ship_matrix[row][col]
            
            # --- HIGH CONTRAST COLOR LOGIC ---
            if tile_state == TILE_MISS:
                tile_color = COLOR_MISS
            elif tile_state == TILE_HIT:
                tile_color = (255, 140, 0)  # Bright blazing orange
            elif tile_state == TILE_SUNK:
                tile_color = (60, 60, 60)   # Charcoal dark tone
            elif tile_state == TILE_SHIP:
                if reveal_ships or is_player:
                    tile_color = (45, 60, 85) if is_player else (90, 45, 50)

            rect = pygame.Rect(tile_x, tile_y, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(surface, tile_color, rect)
            
            # --- SHIP STYLING & FLOTATION ---
            if tile_state == TILE_SHIP and (reveal_ships or is_player):
                float_y = math.sin(time_factor + row) * 4.0 
                floating_rect = pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 10, CELL_SIZE - 10)
                
                ship_core_color = (30, 30, 35) if is_player else (210, 165, 45)
                pygame.draw.rect(surface, ship_core_color, floating_rect)

def draw_menu():
    """Renders the main menu splash screen layout interface."""
    screen.fill((15, 20, 30))  # Dark ambient background
    
    # Render titles text
    title_text = font_title.render("PROJECT X: BATTLE OF THE NARROW SEA", True, COLOR_TEXT)
    subtitle_text = font_sub.render("Targaryen & Stark vs. Lannister Fleet", True, (170, 160, 130))
    
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    sub_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50))
    
    screen.blit(title_text, title_rect)
    screen.blit(subtitle_text, sub_rect)
    
    # UI Buttons boundaries calculation
    play_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    exit_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
    
    # Draw button shapes with nice border highlights
    pygame.draw.rect(screen, (30, 50, 75), play_btn)
    pygame.draw.rect(screen, (80, 35, 40), exit_btn)
    pygame.draw.rect(screen, COLOR_TEXT, play_btn, 2)
    pygame.draw.rect(screen, COLOR_TEXT, exit_btn, 2)
    
    # Labels onto buttons
    text_play = font_ui.render("START BATTLE", True, (255, 255, 255))
    text_exit = font_ui.render("LEAVE GAME", True, (255, 255, 255))
    
    screen.blit(text_play, text_play.get_rect(center=play_btn.center))
    screen.blit(text_exit, text_exit.get_rect(center=exit_btn.center))
    
    return play_btn, exit_btn

def main():
    # Setup state managers
    game_state = "MENU"  # States: "MENU", "GAME"
    
    # Instantiating structural items
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    place_ships_randomly(player_board, FLEET_INVENTORY)
    place_ships_randomly(ai_board, FLEET_INVENTORY)
    
    player_turn = True
    game_over = False
    winner_text = ""
    cheat_mode = False

    while True:
        # --- STATE MACHINE CONTROL ---
        if game_state == "MENU":
            play_button, exit_button = draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.collidepoint(mouse_pos):
                        game_state = "GAME"  # Transitions directly into active match loop
                    elif exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                        
        elif game_state == "GAME":
            screen.fill((10, 20, 30))
            
            # Print bando labels interfaces
            player_label = font_ui.render("TEAM BLACK (TARGARYEN & STARK)", True, COLOR_TEXT)
            ai_label = font_ui.render("TEAM GREEN (LANNISTER AI)", True, COLOR_TEXT)
            screen.blit(player_label, (MARGIN, 15))
            screen.blit(ai_label, (BOARD_WIDTH + (MARGIN * 2), 15))
            
            # Render game matrices grids
            draw_grid(screen, MARGIN, MARGIN * 2, player_board, is_player=True)
            draw_grid(screen, BOARD_WIDTH + (MARGIN * 2), MARGIN * 2, ai_board, reveal_ships=cheat_mode, is_player=False)
            
            # End banner conditional check
            if game_over:
                if winner_text == "PLAYER (TARGARYEN)":
                    victory_message = "VICTORY! THE IRON THRONE BELONGS TO THE TARGARYENS!"
                    text_color = (255, 215, 0)  # Golden
                else:
                    victory_message = "DEFEAT... A LANNISTER ALWAYS PAYS HIS DEBTS!"
                    text_color = (220, 20, 60)   # Crimson Red
                
                end_banner = font_ui.render(victory_message, True, text_color)
                text_rect = end_banner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35))
                screen.blit(end_banner, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k:  # Presentation trick layout toggle key
                        cheat_mode = not cheat_mode
                        
                if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                    mx, my = pygame.mouse.get_pos()
                    ai_start_x = BOARD_WIDTH + (MARGIN * 2)
                    ai_start_y = MARGIN * 2
                    
                    if ai_start_x <= mx < ai_start_x + BOARD_WIDTH and ai_start_y <= my < ai_start_y + BOARD_WIDTH:
                        target_x = (mx - ai_start_x) // CELL_SIZE
                        target_y = (my - ai_start_y) // CELL_SIZE
                        
                        shot_result, repeat_turn = ai_board.receive_shot(target_x, target_y)
                        
                        if shot_result != "ALREADY_SHOT":
                            player_board.register_own_shot(target_x, target_y, shot_result)
                            print(f"Player fired at ({target_x}, {target_y}) -> {shot_result}")
                            
                            if not ai_board.has_ships_alive():
                                game_over = True
                                winner_text = "PLAYER (TARGARYEN)"
                                
                            player_turn = repeat_turn

            # AI execution automation handler
            if not player_turn and not game_over:
                pygame.time.wait(600)  # Pacing pause delay simulation
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