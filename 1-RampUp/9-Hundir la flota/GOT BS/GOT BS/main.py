import pygame
import sys
import math
import os

import variables as v
from classes import Board
from functions import place_ships_randomly, get_lannister_ai_coordinates

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

monitor_info = pygame.display.Info()
screen_max_width = monitor_info.current_w
screen_max_height = monitor_info.current_h

CELL_SIZE = int((screen_max_height * 0.75) / v.BOARD_SIZE)
BOARD_WIDTH = CELL_SIZE * v.BOARD_SIZE
TACTICAL_GAP = CELL_SIZE * 1.5
TOTAL_FLEET_WIDTH = (BOARD_WIDTH * 2) + TACTICAL_GAP

START_X = (screen_max_width - TOTAL_FLEET_WIDTH) // 2
START_Y = (screen_max_height - BOARD_WIDTH) // 2

screen = pygame.display.set_mode((screen_max_width, screen_max_height), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("BATTLE OF THE NARROW SEA")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("serif", int(CELL_SIZE * 0.7), bold=True)
font_sub = pygame.font.SysFont("serif", int(CELL_SIZE * 0.4), italic=True)
font_ui = pygame.font.SysFont("serif", int(CELL_SIZE * 0.35), bold=True)

# --- CONFIGURACIÓN DE SPRITES (ENCENDIDO FORZADO DIRECTO) ---
USING_SPRITES = True
USING_OCEAN_SPRITE = False
USING_SHIPS_SPRITES = True  # Activado permanentemente para renderizar tus imágenes
USING_FX_SPRITES = False

img_bg_ocean = None
TILE_SIZE = 512
dict_ships_targaryen = {}
dict_ships_lannister = {}

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
    
    # Carga de mar de ChatGPT
    ocean_path = os.path.join(ASSETS_DIR, "background_ocean.png")
    if os.path.exists(ocean_path):
        img_bg_ocean = pygame.transform.scale(pygame.image.load(ocean_path).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        USING_OCEAN_SPRITE = True

    # Carga tolerante de barcos del 1 al 4
    for i in range(1, 5):
        p_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}.png")
        a_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}.png")
        if os.path.exists(p_path):
            dict_ships_targaryen[i] = pygame.image.load(p_path).convert_alpha()
        if os.path.exists(a_path):
            dict_ships_lannister[i] = pygame.image.load(a_path).convert_alpha()
except Exception:
    pass


def draw_scrolling_ocean(surface):
    if not USING_OCEAN_SPRITE or img_bg_ocean is None:
        surface.fill(v.COLOR_SEA_BACKGROUND)
        return
    time_ms = pygame.time.get_ticks()
    scroll_x = int((time_ms / 160) % TILE_SIZE)
    scroll_y = int((time_ms / 200) % TILE_SIZE)
    for x in range(-TILE_SIZE, surface.get_width() + TILE_SIZE, TILE_SIZE):
        for y in range(-TILE_SIZE, surface.get_height() + TILE_SIZE, TILE_SIZE):
            surface.blit(img_bg_ocean, (x + scroll_x, y + scroll_y))


def draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player):
    """
    Renders the warships dynamically on top of the moving sea backdrop.
    SOLUCIÓN ANTI-SOLAPAMIENTO DEFINITIVA: El motor de rescate verifica que ninguna de las celdas
    a ocupar esté en drawn_cells, impidiendo físicamente que dos barcos se solapen en pantalla.
    """
    ship_dict = dict_ships_targaryen if is_player else dict_ships_lannister
    if not USING_SHIPS_SPRITES or not ship_dict:
        return
    
    # Clonamos la matriz original para ir tachando las piezas procesadas
    temp_matrix = [[board.ship_matrix[r][c] for c in range(v.BOARD_SIZE)] for r in range(v.BOARD_SIZE)]
    drawn_cells = set()
    time_factor = pygame.time.get_ticks() / 400.0

    # Conjunto de estados válidos que componen el cuerpo físico e histórico de un barco
    valid_ship_tiles = [v.TILE_SHIP, v.TILE_HIT, v.TILE_SUNK]

    # CUPO REGLAMENTARIO RIGUROSO (1 de 4, 2 de 3, 3 de 2, 4 de 1)
    target_inventory = {4: 1, 3: 2, 2: 3, 1: 4}
    active_inventory = {4: 0, 3: 0, 2: 0, 1: 0}

    # --- PASADA 1: ESCÁNER DE BLOQUES CONTINUOS CON LÍMITE DE CUPO ---
    for target_size in range(4, 0, -1):
        for row in range(v.BOARD_SIZE):
            for col in range(v.BOARD_SIZE):
                if temp_matrix[row][col] in valid_ship_tiles:
                    
                    # Medimos la longitud continua horizontal incluyendo celdas dañadas
                    h_len = 0
                    while (col + h_len < v.BOARD_SIZE and 
                           temp_matrix[row][col + h_len] in valid_ship_tiles):
                        h_len += 1
                    
                    # Medimos la longitud continua vertical incluyendo celdas dañadas
                    v_len = 0
                    while (row + v_len < v.BOARD_SIZE and 
                           temp_matrix[row + v_len][col] in valid_ship_tiles):
                        v_len += 1

                    orientation = None
                    if h_len == target_size and h_len > 1:
                        length, orientation = h_len, "H"
                    elif v_len == target_size and v_len > 1:
                        length, orientation = v_len, "V"
                    elif target_size == 1 and h_len == 1 and v_len == 1:
                        length, orientation = 1, "V"
                    else:
                        continue

                    length = min(4, length)
                    
                    if active_inventory[length] < target_inventory[length]:
                        active_inventory[length] += 1
                        
                        for i in range(length):
                            if orientation == "H": 
                                temp_matrix[row][col + i] = 0
                                drawn_cells.add((row, col + i))
                            else: 
                                temp_matrix[row + i][col] = 0
                                drawn_cells.add((row + i, col))
                        
                        if is_player or reveal_ships:
                            base_asset = ship_dict.get(length)
                            if base_asset is None: 
                                continue
                            tile_x = x_offset + (col * CELL_SIZE)
                            tile_y = y_offset + (row * CELL_SIZE)
                            
                            if orientation == "H":
                                final_ship = pygame.transform.scale(pygame.transform.rotate(base_asset, 90), (CELL_SIZE * length, CELL_SIZE))
                            else:
                                final_ship = pygame.transform.scale(base_asset, (CELL_SIZE, CELL_SIZE * length))
                            
                            float_offset = int(math.sin(time_factor + row) * 3.0) if is_player else 0
                            surface.blit(final_ship, (tile_x, tile_y + float_offset))

    # --- PASADA 2: MOTOR DE RESCATE CALIBRADO ANTI-SOLAPAMIENTO ---
    for size in range(4, 0, -1):
        while active_inventory[size] < target_inventory[size]:
            found_rescue = False
            for r in range(v.BOARD_SIZE):
                for c in range(v.BOARD_SIZE):
                    # Rescatamos celdas que sean barco pero asegurándonos de que NO tengan ya un barco dibujado encima
                    if board.ship_matrix[r][c] in valid_ship_tiles and (r, c) not in drawn_cells:
                        length = size
                        orientation = None
                        
                        # FILTRO CRÍTICO: Comprobamos que TODAS las celdas a ocupar estén libres de otros barcos (not in drawn_cells)
                        if (c + length <= v.BOARD_SIZE and 
                            all(board.ship_matrix[r][c + i] in valid_ship_tiles for i in range(length)) and
                            all((r, c + i) not in drawn_cells for i in range(length))):
                            orientation = "H"
                        elif (r + length <= v.BOARD_SIZE and 
                              all(board.ship_matrix[r + i][c] in valid_ship_tiles for i in range(length)) and
                              all((r + i, c) not in drawn_cells for i in range(length))):
                            orientation = "V"
                        
                        if orientation is None:
                            continue

                        # Bloqueamos el espacio ocupado para que nadie más lo pise
                        for i in range(length):
                            drawn_cells.add((r, c + i) if orientation == "H" else (r + i, c))
                        
                        active_inventory[size] += 1
                        found_rescue = True
                        
                        if is_player or reveal_ships:
                            base_asset = ship_dict.get(length)
                            if base_asset is not None:
                                tile_x = x_offset + (c * CELL_SIZE)
                                tile_y = y_offset + (r * CELL_SIZE)
                                if orientation == "H":
                                    final_ship = pygame.transform.scale(pygame.transform.rotate(base_asset, 90), (CELL_SIZE * length, CELL_SIZE))
                                else:
                                    final_ship = pygame.transform.scale(base_asset, (CELL_SIZE, CELL_SIZE * length))
                                float_offset = int(math.sin(time_factor + r) * 3.0) if is_player else 0
                                surface.blit(final_ship, (tile_x, tile_y + float_offset))
                        break
                if found_rescue: 
                    break
            if not found_rescue:
                active_inventory[size] += 1


def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """Renders the tactical grid layers with absolute mathematical alignment."""
    time_factor = pygame.time.get_ticks() / 400.0
    
    # --- CAPA 1: Renderizado de los barcos en sus coordenadas reales ---
    if USING_SHIPS_SPRITES:
        draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player)
    else:
        for row in range(v.BOARD_SIZE):
            for col in range(v.BOARD_SIZE):
                tile_x = x_offset + (col * CELL_SIZE)
                tile_y = y_offset + (row * CELL_SIZE)
                if board.ship_matrix[row][col] == v.TILE_SHIP and (reveal_ships or is_player):
                    float_y = math.sin(time_factor + row) * 4.0
                    pygame.draw.rect(surface, v.COLOR_TARGARYEN_SHIP if is_player else v.COLOR_LANNISTER_SHIP, 
                                     pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 8, CELL_SIZE - 8))

    # --- CAPA 2: Superposición de estados de combate (Sincronización milimétrica) ---
    for row in range(v.BOARD_SIZE):
        for col in range(v.BOARD_SIZE):
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            tile_state = board.ship_matrix[row][col]
            
            # Disparo al agua fallado
            if tile_state == v.TILE_MISS:
                pygame.draw.circle(surface, v.COLOR_MISS, (tile_x + CELL_SIZE//2, tile_y + CELL_SIZE//2), CELL_SIZE//4)
            
            # Impacto real (Tocado o Hundido) -> Se dibuja encima de la misma celda de datos
            elif tile_state in [v.TILE_HIT, v.TILE_SUNK]:
                tile_color = v.COLOR_DRACARYS_FIRE if tile_state == v.TILE_HIT else (60, 60, 60)
                rect_impacto = pygame.Rect(tile_x, tile_y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, tile_color, rect_impacto)

    # --- CAPA 3: Rejilla blanca premium transparente ---
    grid_overlay = pygame.Surface((BOARD_WIDTH + 4, BOARD_WIDTH + 4), pygame.SRCALPHA)
    for i in range(v.BOARD_SIZE + 1):
        pygame.draw.line(grid_overlay, (255, 255, 255, 120), (i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_WIDTH), 3)
        pygame.draw.line(grid_overlay, (255, 255, 255, 120), (0, i * CELL_SIZE), (BOARD_WIDTH, i * CELL_SIZE), 3)
    surface.blit(grid_overlay, (x_offset, y_offset))

def main():
    game_state = "MENU"
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    place_ships_randomly(player_board, v.FLEET_INVENTORY)
    place_ships_randomly(ai_board, v.FLEET_INVENTORY)
    player_turn, game_over, cheat_mode = True, False, False
    winner_text = ""

    while True:
        screen.fill(v.COLOR_SEA_BACKGROUND)
        draw_scrolling_ocean(screen)

        if game_state == "MENU":
            title_text = font_title.render("BATTLE OF THE NARROW SEA", True, v.COLOR_TEXT)
            subtitle_text = font_sub.render("Targaryen & Stark vs. Lannister Fleet", True, v.COLOR_TEXT)
            screen.blit(title_text, title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4)))
            screen.blit(subtitle_text, subtitle_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4 + 50)))
            
            text_play, text_exit = font_ui.render("START BATTLE", True, v.COLOR_TEXT), font_ui.render("LEAVE GAME", True, v.COLOR_TEXT)
            play_btn = text_play.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            exit_btn = text_exit.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 70))
            screen.blit(text_play, play_btn)
            screen.blit(text_exit, exit_btn)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.inflate(40, 20).collidepoint(event.pos): game_state = "GAME"
                    elif exit_btn.inflate(40, 20).collidepoint(event.pos): pygame.quit(); sys.exit()
                        
        elif game_state == "GAME":
            player_label = font_ui.render("TEAM BLACK (TARGARYEN & STARK)", True, v.COLOR_TEXT)
            ai_label = font_ui.render("TEAM GREEN (LANNISTER AI)", True, v.COLOR_TEXT)
            screen.blit(player_label, (START_X, START_Y - 30))
            screen.blit(ai_label, (START_X + BOARD_WIDTH + TACTICAL_GAP, START_Y - 30))
            
            draw_grid(screen, START_X, START_Y, player_board, is_player=True)
            draw_grid(screen, START_X + BOARD_WIDTH + TACTICAL_GAP, START_Y, ai_board, reveal_ships=cheat_mode, is_player=False)
            
            if game_over:
                msg = "VICTORY! THE IRON THRONE BELONGS TO THE TARGARYENS!" if winner_text == "PLAYER" else "DEFEAT... A LANNISTER ALWAYS PAYS HIS DEBTS!"
                end_banner = font_ui.render(msg, True, (255, 215, 0) if winner_text == "PLAYER" else (220, 20, 60))
                screen.blit(end_banner, end_banner.get_rect(center=(screen.get_width() // 2, screen.get_height() - 45)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                    cheat_mode = not cheat_mode
                    
                if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                    mx, my = event.pos
                    ai_x_offset = START_X + BOARD_WIDTH + TACTICAL_GAP
                    if ai_x_offset <= mx < ai_x_offset + BOARD_WIDTH and START_Y <= my < START_Y + BOARD_WIDTH:
                        target_x = int((mx - ai_x_offset) // CELL_SIZE)
                        target_y = int((my - START_Y) // CELL_SIZE)
                        shot_result, repeat_turn = ai_board.receive_shot(target_x, target_y)
                        if shot_result != "ALREADY_SHOT":
                            player_board.register_own_shot(target_x, target_y, shot_result)
                            if not ai_board.has_ships_alive(): game_over, winner_text = True, "PLAYER"
                            player_turn = repeat_turn

            if not player_turn and not game_over:
                pygame.time.wait(600)
                ai_x, ai_y = get_lannister_ai_coordinates(player_board)
                shot_result, repeat_turn = player_board.receive_shot(ai_x, ai_y)
                ai_board.register_own_shot(ai_x, ai_y, shot_result)
                if not player_board.has_ships_alive(): game_over, winner_text = True, "LANNISTER"
                player_turn = not repeat_turn

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()