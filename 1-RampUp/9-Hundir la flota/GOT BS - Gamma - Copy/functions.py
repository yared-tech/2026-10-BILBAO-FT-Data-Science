# functions.py
import random
import variables as v
from classes import Ship

def is_valid_placement(board, x, y, length, orientation):
    """
    Verifica si un barco se puede colocar en una posición sin salirse del mapa
    y cumpliendo la regla de oro: no tocar a otros barcos en sus 8 casillas vecinas.
    """
    coordinates = []
    
    # Calculamos la trayectoria según la orientación (Norte, Sur, Este, Oeste)
    for i in range(length):
        current_x = x + (i if orientation == "E" else -i if orientation == "W" else 0)
        current_y = y + (i if orientation == "S" else -i if orientation == "N" else 0)
            
        # Regla 1: Validar que el barco no se salga de los límites del tablero (0 a 9)
        if not (0 <= current_x < v.BOARD_SIZE and 0 <= current_y < v.BOARD_SIZE):
            return False, []
            
        # Regla 2: Comprobar la casilla actual y sus 8 direcciones contiguas (evita solapamientos)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy
                # Si la casilla vecina existe en el mapa, nos aseguramos de que sea agua limpia
                if 0 <= neighbor_x < v.BOARD_SIZE and 0 <= neighbor_y < v.BOARD_SIZE:
                    if board.ship_matrix[neighbor_y][neighbor_x] != v.TILE_WATER:
                        return False, []  # Si hay otro barco cerca, la posición no es válida
            
        coordinates.append((current_x, current_y))
        
    return True, coordinates


def place_ships_randomly(board, fleet_inventory):
    """Coloca toda la flota de barcos de forma aleatoria en el tablero al iniciar la partida."""
    orientations = ["N", "S", "E", "W"]
    
    for ship_name, length in fleet_inventory.items():
        # Asignamos cuántos barcos de cada tipo se deben crear en base a las reglas
        count = 2 if ship_name == "War Galley" else 3 if ship_name == "Winterfell Sailboat" else 4 if ship_name == "Landing Boat" else 1
            
        for _ in range(count):
            placed = False
            while not placed:
                # Elegimos una coordenada y orientación al azar
                x = random.randint(0, v.BOARD_SIZE - 1)
                y = random.randint(0, v.BOARD_SIZE - 1)
                orientation = random.choice(orientations)
                
                # Comprobamos si cumple los requisitos de espacio
                is_valid, coords = is_valid_placement(board, x, y, length, orientation)
                
                if is_valid:
                    # Creamos el objeto barco y guardamos sus posiciones confirmadas
                    new_ship = Ship(ship_name, length)
                    new_ship.coordinates = coords
                    board.ships_list.append(new_ship)
                    
                    # Pintamos el barco con el identificador visual en la matriz del tablero
                    for cx, cy in coords:
                        board.ship_matrix[cy][cx] = v.TILE_SHIP
                    placed = True


def get_lannister_ai_coordinates(human_board):
    """
    Inteligencia Artificial: Si hay un barco tocado en el mapa, busca a su alrededor en cruz.
    Si no hay barcos tocados, dispara a una casilla completamente aleatoria.
    """
    hunting_targets = []

    # Escaneamos el mapa del jugador buscando casillas que estén marcadas como "TOCADAS" (TILE_HIT)
    for y in range(v.BOARD_SIZE):
        for x in range(v.BOARD_SIZE):
            if human_board.ship_matrix[y][x] == v.TILE_HIT:
                # Si encuentra una casilla tocada, calcula las casillas adyacentes (Arriba, Abajo, Izquierda, Derecha)
                cross_vectors = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
                
                for tx, ty in cross_vectors:
                    # Si la casilla adyacente está dentro del mapa y es agua o un barco oculto, la añade como objetivo
                    if 0 <= tx < v.BOARD_SIZE and 0 <= ty < v.BOARD_SIZE:
                        if human_board.ship_matrix[ty][tx] in [v.TILE_WATER, v.TILE_SHIP]:
                            hunting_targets.append((tx, ty))

    # Si la IA tiene objetivos marcados en su radar de búsqueda, ataca uno de ellos al azar
    if hunting_targets:
        return random.choice(hunting_targets)

    # Si no hay pistas de barcos tocados en el mapa, dispara al azar en bucle hasta dar con una casilla no atacada
    while True:
        rx = random.randint(0, v.BOARD_SIZE - 1)
        ry = random.randint(0, v.BOARD_SIZE - 1)
        if human_board.ship_matrix[ry][rx] in [v.TILE_WATER, v.TILE_SHIP]:
            return rx, ry
