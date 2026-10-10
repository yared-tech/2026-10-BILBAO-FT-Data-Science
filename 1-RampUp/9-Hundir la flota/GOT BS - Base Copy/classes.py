import random

from variables import (
    BOARD_SIZE, TILE_WATER, TILE_SHIP, 
    TILE_MISS, TILE_HIT, TILE_SUNK
)

class Ship:
    """Class representing an individual ship in the Westeros universe."""
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.coordinates = []  # List of tuples [(x1, y1), (x2, y2), ...]
        self.hits = 0          # Number of times this ship has been hit

    @property
    def is_sunk(self):
        """Returns True if the ship has taken as many hits as its length."""
        return self.hits >= self.length


class Board:
    """Class modeling the 10x10 grid for either the human player or the AI."""
    def __init__(self, player_id):
        self.player_id = player_id  # "Human" (Targaryen/Stark) or "AI" (Lannister)
        self.size = BOARD_SIZE
        
        # 1. Hidden matrix: Contains placed ships (fog of war for the enemy)
        self.ship_matrix = [[TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        # 2. Tracking matrix: Records shots fired by this player onto the enemy
        self.tracking_matrix = [[TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        # List to store Ship objects belonging to this board
        self.ships_list = []

    def receive_shot(self, x, y):
        """
        Processes an incoming shot on this board.
        Returns a tuple: (result_text, repeat_turn_boolean)
        """
        # Validate if this cell has already been targeted
        if self.ship_matrix[y][x] in [TILE_MISS, TILE_HIT, TILE_SUNK]:
            return "ALREADY_SHOT", True  # Player retains turn to try a new coordinate

        # Case 1: Splash / Miss
        if self.ship_matrix[y][x] == TILE_WATER:
            self.ship_matrix[y][x] = TILE_MISS
            return "MISS", False  # Turn switches to the opponent

        # Case 2: Direct hit on a ship segment
        if self.ship_matrix[y][x] == TILE_SHIP:
            self.ship_matrix[y][x] = TILE_HIT
            
            # Find the specific ship that was struck to register damage
            for ship in self.ships_list:
                if (x, y) in ship.coordinates:
                    ship.hits += 1
                    
                    # Check if the ship is completely destroyed
                    if self.ship_matrix[y][x] == TILE_HIT and ship.is_sunk:
                        # Mark all coordinates of this ship as sunk
                        for bx, by in ship.coordinates:
                            self.ship_matrix[by][bx] = TILE_SUNK
                        return f"SUNK! You destroyed a {ship.name}", True
                    
                    return f"HIT! Direct strike on {ship.name}", True
                    
        return "ERROR", False

    def register_own_shot(self, x, y, result):
        """Updates the tracking matrix of the attacker with the shot result."""
        if "HIT" in result:
            self.tracking_matrix[y][x] = TILE_HIT
        elif "SUNK" in result:
            self.tracking_matrix[y][x] = TILE_SUNK
        elif result == "MISS":
            self.tracking_matrix[y][x] = TILE_MISS

    def has_ships_alive(self):
        """Checks if the player still has any operational ships floating."""
        for ship in self.ships_list:
            if not ship.is_sunk:
                return True
        return False
