import random
from variables import BOARD_SIZE, TILE_WATER, TILE_SHIP, TILE_HIT
from classes import Ship, Board

def is_valid_placement(board, x, y, length, orientation):
    """
    Checks if a ship of a given length can be placed at (x, y) 
    with the specified orientation without overlapping or going out of bounds.
    """
    coordinates = []
    
    for i in range(length):
        current_x = x
        current_y = y
        
        if orientation == "N":    # North / Up
            current_y = y - i
        elif orientation == "S":  # South / Down
            current_y = y + i
        elif orientation == "E":  # East / Right
            current_x = x + i
        elif orientation == "W":  # West / Left
            current_x = x - i
            
        # Check if coordinates are within the 10x10 boundaries
        if not (0 <= current_x < BOARD_SIZE and 0 <= current_y < BOARD_SIZE):
            return False, []
            
        # Check for overlap with existing ships
        if board.ship_matrix[current_y][current_x] != TILE_WATER:
            return False, []
            
        coordinates.append((current_x, current_y))
        
    return True, coordinates


def place_ships_randomly(board, fleet_inventory):
    """
    Iterates through the fleet inventory and places each ship randomly
    on the board, ensuring rules are followed and updating the matrix.
    """
    orientations = ["N", "S", "E", "W"]
    
    for ship_name, length in fleet_inventory.items():
        # Handle multiple ships of the same type based on rules (e.g., 2 War Galleys)
        count = 1
        if ship_name == "War Galley":
            count = 2
        elif ship_name == "Winterfell Sailboat":
            count = 3
        elif ship_name == "Landing Boat":
            count = 4
            
        for _ in range(count):
            placed = False
            while not placed:
                # Pick random start coordinates and orientation
                x = random.randint(0, BOARD_SIZE - 1)
                y = random.randint(0, BOARD_SIZE - 1)
                orientation = random.choice(orientations)
                
                # Validate selection
                is_valid, coords = is_valid_placement(board, x, y, length, orientation)
                
                if is_valid:
                    # Create the Ship instance and store its metadata
                    new_ship = Ship(ship_name, length)
                    new_ship.coordinates = coords
                    board.ships_list.append(new_ship)
                    
                    # Carve the ship onto the logical matrix
                    for cx, cy in coords:
                        board.ship_matrix[cy][cx] = TILE_SHIP
                    
                    placed = True


def get_lannister_ai_coordinates(human_board):
    """
    Advanced AI Targeting (Bonus Track 4).
    Scans the player's board for injured ships to hunt down, 
    otherwise falls back to a smart random layout shot.
    """
    hunting_targets = []

    # 1. Scan the entire board to collect ALL possible smart targets
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if human_board.ship_matrix[y][x] == TILE_HIT:
                potential_cross = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
                
                for tx, ty in potential_cross:
                    if 0 <= tx < BOARD_SIZE and 0 <= ty < BOARD_SIZE:
                        # If the adjacent cell is pristine water or a hidden ship, we can hunt it
                        if human_board.ship_matrix[ty][tx] in [TILE_WATER, TILE_SHIP]:
                            hunting_targets.append((tx, ty))

    # If we found active coordinates around ANY injured ship, pick one at random
    if hunting_targets:
        return random.choice(hunting_targets)

    # 2. Fallback: If no wounded hunting targets exist, fire a smart random shot
    while True:
        rx = random.randint(0, BOARD_SIZE - 1)
        ry = random.randint(0, BOARD_SIZE - 1)
        
        # Ensure we only return locations that haven't been shot yet
        if human_board.ship_matrix[ry][rx] in [TILE_WATER, TILE_SHIP]:
            return rx, ry

