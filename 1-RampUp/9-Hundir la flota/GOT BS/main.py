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
# --- CONFIGURACIÓN DE SPRITES (ACTUALIZADO CON ARSENAL QUEMADO) ---
USING_SPRITES = True
USING_OCEAN_SPRITE = False
USING_SHIPS_SPRITES = True  

img_bg_ocean = None
TILE_SIZE = 512

# Diccionarios de barcos vivos
dict_ships_targaryen = {}
dict_ships_lannister = {}

# Diccionarios de barcos quemados (¡NUEVOS!)
dict_ships_targaryen_burnt = {}
dict_ships_lannister_burnt = {}

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
    
    # Carga de mar de ChatGPT
    ocean_path = os.path.join(ASSETS_DIR, "background_ocean.png")
    if os.path.exists(ocean_path):
        img_bg_ocean = pygame.transform.scale(pygame.image.load(ocean_path).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        USING_OCEAN_SPRITE = True

    # Carga automática de barcos vivos y quemados del 1 al 4
    for i in range(1, 5):
        p_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}.png")
        a_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}.png")
        p_burnt_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}_burnt.png")
        a_burnt_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}_burnt.png")
        
        # Guardamos vivos
        if os.path.exists(p_path): dict_ships_targaryen[i] = pygame.image.load(p_path).convert_alpha()
        if os.path.exists(a_path): dict_ships_lannister[i] = pygame.image.load(a_path).convert_alpha()
        
        # Guardamos quemados
        if os.path.exists(p_burnt_path): dict_ships_targaryen_burnt[i] = pygame.image.load(p_burnt_path).convert_alpha()
        if os.path.exists(a_burnt_path): dict_ships_lannister_burnt[i] = pygame.image.load(a_burnt_path).convert_alpha()
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
    REPARACIÓN DE VAIVÉN: Activa la oscilación marina en ambos tableros simultáneamente,
    haciendo que la IA Lannister flote de forma orgánica y descompasada igual que el jugador.
    """
    live_dict = dict_ships_targaryen if is_player else dict_ships_lannister
    burnt_dict = dict_ships_targaryen_burnt if is_player else dict_ships_lannister_burnt
    if not live_dict or not burnt_dict: return
    
    temp_matrix = [[board.ship_matrix[r][c] for c in range(v.BOARD_SIZE)] for r in range(v.BOARD_SIZE)]
    drawn_cells = set()
    time_factor = pygame.time.get_ticks() / 400.0
    valid_ship_tiles = [v.TILE_SHIP, v.TILE_HIT, v.TILE_SUNK]

    for row in range(v.BOARD_SIZE):
        for col in range(v.BOARD_SIZE):
            if (row, col) in drawn_cells: continue
            if temp_matrix[row][col] in valid_ship_tiles:
                
                h_len = 0
                while (col + h_len < v.BOARD_SIZE and temp_matrix[row][col + h_len] in valid_ship_tiles and (row, col + h_len) not in drawn_cells): h_len += 1
                v_len = 0
                while (row + v_len < v.BOARD_SIZE and temp_matrix[row + v_len][col] in valid_ship_tiles and (row + v_len, col) not in drawn_cells): v_len += 1

                if h_len > v_len and h_len > 1: length, orientation = h_len, "H"
                elif v_len >= h_len and v_len > 1: length, orientation = v_len, "V"
                else: length, orientation = 1, "V"

                if orientation == "H" and col > 0 and board.ship_matrix[row][col - 1] in valid_ship_tiles: continue
                if orientation == "V" and row > 0 and board.ship_matrix[row - 1][col] in valid_ship_tiles: continue

                length = min(4, length)
                
                is_damaged = False
                is_completely_sunk = True 
                
                for i in range(length):
                    r_cell = row + i if orientation == "V" else row
                    c_cell = col if orientation == "V" else col + i
                    cell_state = board.ship_matrix[r_cell][c_cell]
                    if cell_state in [v.TILE_HIT, v.TILE_SUNK]: is_damaged = True
                    if cell_state != v.TILE_SUNK: is_completely_sunk = False

                for i in range(length):
                    if orientation == "H": temp_matrix[row][col + i] = 0; drawn_cells.add((row, col + i))
                    else: temp_matrix[row + i][col] = 0; drawn_cells.add((row + i, col))
                
                if is_player or reveal_ships:
                    current_dict = burnt_dict if is_damaged else live_dict
                    base_asset = current_dict.get(length, current_dict.get(1))
                    if base_asset is None: continue
                    
                    # --- MOTOR DE ANIMACIÓN DE FUEGO ULTRA-LENTO Y SUTIL (Mantenido a petición) ---
                    if is_damaged and not is_completely_sunk:
                        fire_pulse = math.sin(pygame.time.get_ticks() / 250.0) * 0.003
                        scale_w_factor = 1.0 + fire_pulse
                        scale_h_factor = 1.0 - fire_pulse
                    else:
                        scale_w_factor = 1.0
                        scale_h_factor = 1.0

                    if orientation == "H":
                        rotated_asset = pygame.transform.rotate(base_asset, 90)
                        target_w = int(CELL_SIZE * length * scale_w_factor)
                        target_h = int(CELL_SIZE * scale_h_factor)
                        final_ship = pygame.transform.scale(rotated_asset, (target_w, target_h))
                    else:
                        target_w = int(CELL_SIZE * scale_w_factor)
                        target_h = int(CELL_SIZE * length * scale_h_factor)
                        final_ship = pygame.transform.scale(base_asset, (target_w, target_h))
                    
                    if is_completely_sunk:
                        dark_mask = pygame.Surface(final_ship.get_size(), pygame.SRCALPHA)
                        dark_mask.fill((0, 0, 0, 110))
                        final_ship.blit(dark_mask, (0, 0))

                    offset_x = (CELL_SIZE * length - target_w) // 2 if orientation == "H" else (CELL_SIZE - target_w) // 2
                    offset_y = (CELL_SIZE - target_h) // 2 if orientation == "H" else (CELL_SIZE * length - target_h) // 2

                    tile_x = x_offset + (col * CELL_SIZE) + offset_x
                    tile_y = y_offset + (row * CELL_SIZE) + offset_y
                    
                    # CORRECCIÓN DE OLEAJE GLOBAL: Quitamos 'if is_player' para que afecte a ambos bandos.
                    # Añadimos '+ col' para romper la sincronía y que el movimiento del océano se vea natural.
                    float_offset = int(math.sin(time_factor + row + col) * 3.0) if not is_completely_sunk else 0
                    
                    surface.blit(final_ship, (tile_x, tile_y + float_offset))



def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    """
    Renders the tactical transparent grid and game states layer by layer with absolute alignment.
    FILTRO ALFA TRANSLÚCIDO: Aplica una capa naranja transparente sobre las celdas TILE_HIT
    para marcar el impacto táctico permitiendo ver las llamas y el humo del barco por debajo.
    """
    time_factor = pygame.time.get_ticks() / 400.0
    
    # --- CAPA 1: Renderizado de los sprites de los barcos de fondo ---
    if USING_SHIPS_SPRITES:
        draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player)
    else:
        # Modo fallback antiguo: Solo si los sprites están apagados pintamos los bloques de la flota intacta
        for row in range(v.BOARD_SIZE):
            for col in range(v.BOARD_SIZE):
                tile_x = x_offset + (col * CELL_SIZE)
                tile_y = y_offset + (row * CELL_SIZE)
                if board.ship_matrix[row][col] == v.TILE_SHIP and (reveal_ships or is_player):
                    float_y = math.sin(time_factor + row) * 4.0
                    pygame.draw.rect(surface, v.COLOR_TARGARYEN_SHIP if is_player else v.COLOR_LANNISTER_SHIP, 
                                     pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 8, CELL_SIZE - 8))

    # --- CAPA 2: Superposición de impactos con transparencias premium (Canal Alfa) ---
    for row in range(v.BOARD_SIZE):
        for col in range(v.BOARD_SIZE):
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            tile_state = board.ship_matrix[row][col]
            
            # Disparo al agua: Círculo de agua fallada original
            if tile_state == v.TILE_MISS:
                pygame.draw.circle(surface, v.COLOR_MISS, (tile_x + CELL_SIZE//2, tile_y + CELL_SIZE//2), CELL_SIZE//4)
            
            # NUEVO EFECTO TÁCTICO: Celda Tocada (TILE_HIT) -> Capa Naranja Transparente
            elif tile_state == v.TILE_HIT:
                # Creamos una superficie del tamaño exacto de la casilla con soporte Alpha
                hit_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                
                # Desempaquetamos tu color de fuego original (v.COLOR_DRACARYS_FIRE) 
                # y le añadimos un valor alfa de 125 (escala de 0 a 255, 125 es un 50% de transparencia)
                r, g, b = v.COLOR_DRACARYS_FIRE
                hit_overlay.fill((r, g, b, 125)) 
                
                # Volcamos el filtro naranja encima del barco visual
                surface.blit(hit_overlay, (tile_x, tile_y))
                
            # Celda Hundida (TILE_SUNK) -> Capa Gris/Negra Oscura Transparente
            elif tile_state == v.TILE_SUNK:
                sunk_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                # Filtro gris oscuro quemado con un 55% de transparencia (140) para marcar que ya no opera
                sunk_overlay.fill((40, 40, 40, 140)) 
                surface.blit(sunk_overlay, (tile_x, tile_y))

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