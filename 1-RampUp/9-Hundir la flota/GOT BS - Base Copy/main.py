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

# Screen setup
CELL_SIZE = 40
MARGIN = 40
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE
SCREEN_WIDTH = (BOARD_WIDTH * 2) + (MARGIN * 3)
SCREEN_HEIGHT = BOARD_WIDTH + (MARGIN * 3)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("serif", 18, bold=True)

def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """Renders a 10x10 tactical board grid with flotation offsets for floating ships."""
    time_factor = pygame.time.get_ticks() / 400.0  # Controls floating speed
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Calculate base screen coordinates for this tile
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            
            # Default tile color (Fog of war / unexplored ocean)
            tile_color = COLOR_WATER
            tile_state = board.ship_matrix[row][col]
            
            # Determine visualization states based on permissions
            if tile_state == TILE_MISS:
                tile_color = COLOR_MISS
            elif tile_state == TILE_HIT:
                tile_color = COLOR_DRACARYS_FIRE
            elif tile_state == TILE_SUNK:
                tile_color = (100, 10, 10)  # Ash burn tone
            elif tile_state == TILE_SHIP:
                if reveal_ships or is_player:
                    tile_color = COLOR_TARGARYEN_SHIP if is_player else COLOR_LANNISTER_SHIP

            # Render background grid block
            rect = pygame.Rect(tile_x, tile_y, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(surface, tile_color, rect)
            
            # Bonus Track: Apply subtle math sin flotation bounce to active floating ships
            if tile_state == TILE_SHIP and (reveal_ships or is_player):
                # Unique offset per row prevents a rigid block wave feel
                float_y = math.sin(time_factor + row) * 4.0 
                floating_rect = pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 10, CELL_SIZE - 10)
                
                ship_core_color = (70, 70, 75) if is_player else (210, 160, 40)
                pygame.draw.rect(surface, ship_core_color, floating_rect)

def main():
    # Instantiating the tactical boards required by the bootcamp
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    
    # Run the structural layout positioning functions
    place_ships_randomly(player_board, FLEET_INVENTORY)
    place_ships_randomly(ai_board, FLEET_INVENTORY)
    
    # Match management switches
    player_turn = True
    game_over = False
    winner_text = ""
    cheat_mode = False  # Activates with 'K' key for evaluation demo purposes

    # Main structural execution loop
    while True:
        screen.fill((10, 20, 30))  # Slate background layout
        
        # Draw labels and text interfaces
        player_label = font.render("TEAM BLACK (TARGARYEN & STARK)", True, COLOR_TEXT)
        ai_label = font.render("TEAM GREEN (LANNISTER AI)", True, COLOR_TEXT)
        screen.blit(player_label, (MARGIN, 15))
        screen.blit(ai_label, (BOARD_WIDTH + (MARGIN * 2), 15))
        
        # Render tactical matrices
        draw_grid(screen, MARGIN, MARGIN * 2, player_board, is_player=True)
        draw_grid(screen, BOARD_WIDTH + (MARGIN * 2), MARGIN * 2, ai_board, reveal_ships=cheat_mode, is_player=False)
        
        if game_over:
            end_banner = font.render(f"GAME OVER - {winner_text} WINS PONIENTE!", True, COLOR_DRACARYS_FIRE)
            screen.blit(end_banner, (SCREEN_WIDTH // 3, SCREEN_HEIGHT - 35))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Key trigger checking
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:  # Toggle layout reveal trick for presentations
                    cheat_mode = not cheat_mode
                    
            # Mouse interactive tracking (Player attack shot placement selection)
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                mx, my = pygame.mouse.get_pos()
                
                # Check if click falls within enemy board box space
                ai_start_x = BOARD_WIDTH + (MARGIN * 2)
                ai_start_y = MARGIN * 2
                
                if ai_start_x <= mx < ai_start_x + BOARD_WIDTH and ai_start_y <= my < ai_start_y + BOARD_WIDTH:
                    # Translate pixel mouse point coordinates to matrix matrix coordinates
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

        # AI Tactical execution phase (Lannister turn automation handler)
        if not player_turn and not game_over:
            pygame.time.wait(600)  # Deliberate sleep pause pacing so the computer looks like it's thinking
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
