# functions.py
import random
import variables as v
from classes import Ship

def is_valid_placement(board, x, y, length, orientation):
    """
    Performs strict perimetric validation tracking within 10x10 bounds.
    SISTEMA ANTI-SOLAPAMIENTO: Comprueba la celda y sus 8 vecinas contiguas
    para impedir que dos barcos se peguen, se crucen o compartan espacio.
    """
    coordinates = []
    
    for i in range(length):
        current_x = x + (i if orientation == "E" else -i if orientation == "W" else 0)
        current_y = y + (i if orientation == "S" else -i if orientation == "N" else 0)
            
        # 1. Filtro de límites estrictos del tablero de 10x10
        if not (0 <= current_x < v.BOARD_SIZE and 0 <= current_y < v.BOARD_SIZE):
            return False, []
            
        # 2. ESCÁNER DE VECINDAD EN 8 DIRECCIONES: Evita colisiones por esquinas o laterales
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy
                # Si la casilla vecina está dentro del tablero, verificamos que sea agua pura (v.TILE_WATER)
                if 0 <= neighbor_x < v.BOARD_SIZE and 0 <= neighbor_y < v.BOARD_SIZE:
                    if board.ship_matrix[neighbor_y][neighbor_x] != v.TILE_WATER:
                        return False, []
            
        coordinates.append((current_x, current_y))
        
    return True, coordinates


def place_ships_randomly(board, fleet_inventory):
    """Algorithmic procedural allocator placing specific fleet components evenly."""
    orientations = ["N", "S", "E", "W"]
    
    for ship_name, length in fleet_inventory.items():
        # Sincronización rigurosa con las restricciones de cantidades obligatorias de tu bootcamp
        count = 2 if ship_name == "War Galley" else 3 if ship_name == "Winterfell Sailboat" else 4 if ship_name == "Landing Boat" else 1
            
        for _ in range(count):
            placed = False
            while not placed:
                x = random.randint(0, v.BOARD_SIZE - 1)
                y = random.randint(0, v.BOARD_SIZE - 1)
                orientation = random.choice(orientations)
                
                is_valid, coords = is_valid_placement(board, x, y, length, orientation)
                
                if is_valid:
                    new_ship = Ship(ship_name, length)
                    new_ship.coordinates = coords
                    board.ships_list.append(new_ship)
                    
                    for cx, cy in coords:
                        board.ship_matrix[cy][cx] = v.TILE_SHIP
                    placed = True


def get_lannister_ai_coordinates(human_board):
    """High-performance vector hunt algorithm."""
    hunting_targets = []

    for y in range(v.BOARD_SIZE):
        for x in range(v.BOARD_SIZE):
            if human_board.ship_matrix[y][x] == v.TILE_HIT:
                cross_vectors = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
                
                for tx, ty in cross_vectors:
                    if 0 <= tx < v.BOARD_SIZE and 0 <= ty < v.BOARD_SIZE:
                        if human_board.ship_matrix[ty][tx] in [v.TILE_WATER, v.TILE_SHIP]:
                            hunting_targets.append((tx, ty))

    if hunting_targets:
        return random.choice(hunting_targets)

    while True:
        rx = random.randint(0, v.BOARD_SIZE - 1)
        ry = random.randint(0, v.BOARD_SIZE - 1)
        if human_board.ship_matrix[ry][rx] in [v.TILE_WATER, v.TILE_SHIP]:
            return rx, ry
