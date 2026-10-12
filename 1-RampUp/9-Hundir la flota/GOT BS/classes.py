# classes.py
import variables as v

class Ship:
    """Represents an individual combat vessel with distinct positional coordinates."""
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.coordinates = []  # Storage for positional matrix tuples [(x, y), ...]
        self.hits = 0          # Real-time damage counter tracking

    @property
    def is_sunk(self):
        """Returns True if the vessel damage matches its total length."""
        return self.hits >= self.length


class Board:
    """Manages the double-matrix tracking system requested by the bootcamp rules."""
    def __init__(self, player_id):
        self.player_id = player_id  # "Human" (Targaryen) or "AI" (Lannister)
        self.size = v.BOARD_SIZE
        
        # Matrix 1: Hidden layer containing operational ships architecture
        self.ship_matrix = [[v.TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        # Matrix 2: Tracking layer for public tactical display (fog of war system)
        self.tracking_matrix = [[v.TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        self.ships_list = []  # Collection storing local Ship instances

    def receive_shot(self, x, y):
        """
        Processes offensive coordinates.
        Returns a tuple string indicator and a turn repetition boolean flag.
        """
        # Prevention filter checking if target was already selected
        if self.ship_matrix[y][x] in [v.TILE_MISS, v.TILE_HIT, v.TILE_SUNK]:
            return "ALREADY_SHOT", True

        # Case 1: Missed calculation splashing into ocean water
        if self.ship_matrix[y][x] == v.TILE_WATER:
            self.ship_matrix[y][x] = v.TILE_MISS
            return "MISS", False

        # Case 2: Hit registered successfully on an active vessel segment
        if self.ship_matrix[y][x] == v.TILE_SHIP:
            self.ship_matrix[y][x] = v.TILE_HIT
            
            # Target identification algorithm lookup
            for ship in self.ships_list:
                if (x, y) in ship.coordinates:
                    ship.hits += 1
                    
                    if ship.is_sunk:
                        # Update all corresponding ship grids to catastrophic SUNK status
                        for bx, by in ship.coordinates:
                            self.ship_matrix[by][bx] = v.TILE_SUNK
                        return f"SUNK! {ship.name} destroyed", True
                    
                    return f"HIT! Strike on {ship.name}", True
                    
        return "ERROR", False

    def register_own_shot(self, x, y, result):
        """Updates internal tracking matrix grids following an offensive sequence outcome."""
        if "HIT" in result:
            self.tracking_matrix[y][x] = v.TILE_HIT
        elif "SUNK" in result:
            self.tracking_matrix[y][x] = v.TILE_SUNK
        elif result == "MISS":
            self.tracking_matrix[y][x] = v.TILE_MISS

    def has_ships_alive(self):
        """Boolean check tracking global operational fleet state."""
        return any(not ship.is_sunk for ship in self.ships_list)

