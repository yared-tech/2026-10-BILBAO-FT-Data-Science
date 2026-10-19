# main.py - PARTE 1
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

# --- CONFIGURACIÓN DE SPRITES PREMIUM ---
USING_SPRITES = True
USING_OCEAN_SPRITE = False
USING_SHIPS_SPRITES = True  

img_bg_ocean = None
TILE_SIZE = 512

dict_ships_targaryen = {}
dict_ships_lannister = {}
dict_ships_targaryen_burnt = {}
dict_ships_lannister_burnt = {}

# LISTA PARA LOS 12 FRAMES INDEPENDIENTES DE DROGON
LIST_DROGON_FRAMES = []

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
    
    ocean_path = os.path.join(ASSETS_DIR, "background_ocean.png")
    if os.path.exists(ocean_path):
        img_bg_ocean = pygame.transform.scale(pygame.image.load(ocean_path).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        USING_OCEAN_SPRITE = True

    for i in range(1, 5):
        p_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}.png")
        a_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}.png")
        p_burnt_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}_burnt.png")
        a_burnt_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}_burnt.png")
        
        if os.path.exists(p_path): dict_ships_targaryen[i] = pygame.image.load(p_path).convert_alpha()
        if os.path.exists(a_path): dict_ships_lannister[i] = pygame.image.load(a_path).convert_alpha()
        if os.path.exists(p_burnt_path): dict_ships_targaryen_burnt[i] = pygame.image.load(p_burnt_path).convert_alpha()
        if os.path.exists(a_burnt_path): dict_ships_lannister_burnt[i] = pygame.image.load(a_burnt_path).convert_alpha()

    # Carga de tus 12 archivos HD transparentes de la cinemática
    for i in range(1, 13):
        drogon_path = os.path.join(ASSETS_DIR, f"drogon_{i}.png")
        if os.path.exists(drogon_path):
            LIST_DROGON_FRAMES.append(pygame.image.load(drogon_path).convert_alpha())
except Exception:
    pass

# --- CONTROLADOR COMPLETO SIN AVISOS DE PYLANDS ---
class DragonAnimationController:
    def __init__(self):
        self.is_active = False
        self.current_x = 0.0
        self.current_y = 0.0
        self.target_px_x = 0.0
        self.target_px_y = 0.0
        self.vx = 0.0  
        self.vy = 0.0  
        self.angle_deg = 0.0      
        self.escape_phase = False  
        self.speed = 7             # Tu velocidad pausada y majestuosa elegida
        self.frame_index = 0
        self.fire_triggered = False
        self.direction = "L_TO_R"
        self.step_timer = 0
        
        # Atributos de quema diferida para draw_grid
        self.burn_col = 0
        self.burn_row = 0
        self.active_board = None
        self.burned_done = False

dragon_cinema = DragonAnimationController()


# main.py - PARTE 2

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
                    
                    float_offset = int(math.sin(time_factor + row + col) * 3.0) if not is_completely_sunk else 0
                    surface.blit(final_ship, (tile_x, tile_y + float_offset))


def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    time_factor = pygame.time.get_ticks() / 400.0
    
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

    for row in range(v.BOARD_SIZE):
        for col in range(v.BOARD_SIZE):
            tile_x = x_offset + (col * CELL_SIZE)
            tile_y = y_offset + (row * CELL_SIZE)
            tile_state = board.ship_matrix[row][col]
            
            # --- MÁSCARA DE CAMUFLAJE ESPECÍFICA POR COORDENADAS ---
            # Solo camuflamos si la celda es del tablero atacado, está en TILE_SUNK lógicamente,
            # pero Drogon todavía no ha pasado por encima de esta coordenada exacta.
            if tile_state == v.TILE_SUNK and dragon_cinema.is_active and dragon_cinema.active_board == board:
                if not dragon_cinema.burned_done:
                    # Buscamos si la celda actual forma parte del barco que se está atacando
                    for ship in board.ships_list:
                        if (dragon_cinema.burn_col, dragon_cinema.burn_row) in ship.coordinates:
                            if (col, row) in ship.coordinates:
                                tile_state = v.TILE_HIT  # Se mantiene naranja provisionalmente

            if tile_state == v.TILE_MISS:
                pygame.draw.circle(surface, v.COLOR_MISS, (tile_x + CELL_SIZE//2, tile_y + CELL_SIZE//2), CELL_SIZE//4)
            elif tile_state == v.TILE_HIT:
                hit_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                r, g, b = v.COLOR_DRACARYS_FIRE
                hit_overlay.fill((r, g, b, 125)) 
                surface.blit(hit_overlay, (tile_x, tile_y))
            elif tile_state == v.TILE_SUNK:
                sunk_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                sunk_overlay.fill((40, 40, 40, 140)) 
                surface.blit(sunk_overlay, (tile_x, tile_y))

    grid_overlay = pygame.Surface((BOARD_WIDTH + 4, BOARD_WIDTH + 4), pygame.SRCALPHA)
    for i in range(v.BOARD_SIZE + 1):
        pygame.draw.line(grid_overlay, (255, 255, 255, 120), (i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_WIDTH), 3)
        pygame.draw.line(grid_overlay, (255, 255, 255, 120), (0, i * CELL_SIZE), (BOARD_WIDTH, i * CELL_SIZE), 3)
    surface.blit(grid_overlay, (x_offset, y_offset))

# main.py - PARTE 3 REPARADA (CUELLO CORRECTO, SALIDA INFINITA Y QUEMA RETRASADA BAJO EL FUEGO)

def update_and_draw_dragon_cinematic(surface):
    if not dragon_cinema.is_active or not LIST_DROGON_FRAMES: return

    dragon_cinema.step_timer += 1
    
    # 1. AVANCE VECTORIAL CONSTANTE INFINITO DE SALIDA
    dragon_cinema.current_x += dragon_cinema.vx
    dragon_cinema.current_y += dragon_cinema.vy

    # 2. LOGÍSTICA DE DISTANCIA PARA EL GATILLO DEL FUEGO
    dx_target = dragon_cinema.target_px_x - dragon_cinema.current_x
    dy_target = dragon_cinema.target_px_y - dragon_cinema.current_y
    distance_to_target = math.sqrt(dx_target**2 + dy_target**2)

    # 3. CONTROL DE FOTOGRAMAS ESTRICTO DE 3 FASES SIN SEGUNDOS DISPAROS
    if not dragon_cinema.fire_triggered:
        if dragon_cinema.step_timer % 6 == 0:
            dragon_cinema.frame_index = (dragon_cinema.frame_index + 1) % 4
        # Lanza el fuego según tu calibración de anticipación lenta a 260px
        if distance_to_target < 260:
            dragon_cinema.fire_triggered = True
            dragon_cinema.frame_index = 4  
            dragon_cinema.escape_phase = False 
            
    elif dragon_cinema.fire_triggered and not dragon_cinema.escape_phase:
        if dragon_cinema.step_timer % 5 == 0:
            if dragon_cinema.frame_index < 11:
                dragon_cinema.frame_index += 1
            else:
                dragon_cinema.escape_phase = True
                dragon_cinema.frame_index = 2 
                
        # --- GATILLO VISUAL REPARADO: EN PLENA PASADA SOBRE EL BARCO ---
        # En el instante exacto en que la distancia al centro de la celda es menor a 50px
        # (es decir, cuando Drogon pasa justo por encima con la llamarada masiva),
        # desactivamos el camuflaje para que el barco se vuelva negro bajo el fuego
        if distance_to_target < 50 and not dragon_cinema.burned_done:
            dragon_cinema.burned_done = True     
    else:
        if dragon_cinema.step_timer % 6 == 0:
            if dragon_cinema.frame_index == 2: dragon_cinema.frame_index = 1 
            else: dragon_cinema.frame_index = (dragon_cinema.frame_index + 1) % 4 

    # 4. COMPENSADOR DE ESCALA QUIRÚRGICO SEGÚN EL FRAME
    raw_sprite = LIST_DROGON_FRAMES[dragon_cinema.frame_index]
    if 4 <= dragon_cinema.frame_index <= 11:
        target_size = int(CELL_SIZE * 7.5)
    else:
        target_size = int(CELL_SIZE * 3.8)

    scaled_dragon = pygame.transform.scale(raw_sprite, (target_size, target_size))
    
    # 5. CONTROL DE ROTACIÓN ESTÁTICO DE TUS ÁNGULOS ORIGINALES PERFECTOS (90 y 270)
    rotated_dragon = pygame.transform.rotate(scaled_dragon, dragon_cinema.angle_deg)

    dragon_rect = rotated_dragon.get_rect()
    dragon_rect.center = (int(dragon_cinema.current_x), int(dragon_cinema.current_y))
    surface.blit(rotated_dragon, dragon_rect)

    if (dragon_cinema.current_x < -400 or dragon_cinema.current_x > surface.get_width() + 400 or
        dragon_cinema.current_y < -400 or dragon_cinema.current_y > surface.get_height() + 400):
        dragon_cinema.is_active = False

def trigger_dragon_strike(target_col, target_row, target_is_ai, target_board):
    offset_x = (START_X + BOARD_WIDTH + TACTICAL_GAP) if target_is_ai else START_X
    px_x = offset_x + (target_col * CELL_SIZE) + (CELL_SIZE // 2)
    px_y = START_Y + (target_row * CELL_SIZE) + (CELL_SIZE // 2)

    dragon_cinema.is_active = True
    dragon_cinema.target_px_x = px_x
    dragon_cinema.target_px_y = px_y
    dragon_cinema.fire_triggered = False
    dragon_cinema.escape_phase = False
    dragon_cinema.frame_index = 0
    dragon_cinema.step_timer = 0
    
    dragon_cinema.burn_col = target_col
    dragon_cinema.burn_row = target_row
    dragon_cinema.active_board = target_board
    dragon_cinema.burned_done = False 

    if target_is_ai:
        dragon_cinema.direction = "L_TO_R"
        dragon_cinema.current_x = -300
        dragon_cinema.current_y = px_y - 300  
        dragon_cinema.angle_deg = 90.0  
    else:
        dragon_cinema.direction = "R_TO_L"
        dragon_cinema.current_x = screen_max_width + 300
        dragon_cinema.current_y = px_y - 300
        dragon_cinema.angle_deg = 270.0

    dx = px_x - dragon_cinema.current_x
    dy = px_y - dragon_cinema.current_y
    angle = math.atan2(dy, dx)
    
    dragon_cinema.vx = math.cos(angle) * dragon_cinema.speed
    dragon_cinema.vy = math.sin(angle) * dragon_cinema.speed


def main():
    game_state = "MENU"
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    place_ships_randomly(player_board, v.FLEET_INVENTORY)
    place_ships_randomly(ai_board, v.FLEET_INVENTORY)
    player_turn, game_over, cheat_mode = True, False, False
    winner_text = ""

    ai_scheduled_shot = None

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
            
            if game_over and not dragon_cinema.is_active:
                msg = "VICTORY! THE IRON THRONE BELONGS TO THE TARGARYENS!" if winner_text == "PLAYER" else "DEFEAT... A LANNISTER ALWAYS PAYS HIS DEBTS!"
                end_banner = font_ui.render(msg, True, (255, 215, 0) if winner_text == "PLAYER" else (220, 20, 60))
                screen.blit(end_banner, end_banner.get_rect(center=(screen.get_width() // 2, screen.get_height() - 45)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                    cheat_mode = not cheat_mode
                    
                if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over and not dragon_cinema.is_active:
                    mx, my = event.pos
                    ai_x_offset = START_X + BOARD_WIDTH + TACTICAL_GAP
                    if ai_x_offset <= mx < ai_x_offset + BOARD_WIDTH and START_Y <= my < START_Y + BOARD_WIDTH:
                        target_x = int((mx - ai_x_offset) // CELL_SIZE)
                        target_y = int((my - START_Y) // CELL_SIZE)
                        shot_result, repeat_turn = ai_board.receive_shot(target_x, target_y)
                        
                        if shot_result != "ALREADY_SHOT":
                            player_board.register_own_shot(target_x, target_y, shot_result)
                            
                            if shot_result == "SUNK":
                                trigger_dragon_strike(target_x, target_y, target_is_ai=True, target_board=ai_board)
                                
                            if not ai_board.has_ships_alive(): game_over, winner_text = True, "PLAYER"
                            player_turn = repeat_turn

            if not player_turn and not game_over and not dragon_cinema.is_active:
                if ai_scheduled_shot is None:
                    ai_scheduled_shot = pygame.time.get_ticks() + 600
                
                if pygame.time.get_ticks() >= ai_scheduled_shot:
                    ai_x, ai_y = get_lannister_ai_coordinates(player_board)
                    shot_result, repeat_turn = player_board.receive_shot(ai_x, ai_y)
                    ai_board.register_own_shot(ai_x, ai_y, shot_result)
                    
                    if shot_result == "SUNK":
                        trigger_dragon_strike(ai_x, ai_y, target_is_ai=False, target_board=player_board)
                        
                    if not player_board.has_ships_alive(): game_over, winner_text = True, "LANNISTER"
                    player_turn = not repeat_turn
                    ai_scheduled_shot = None

            if dragon_cinema.is_active:
                update_and_draw_dragon_cinematic(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()


