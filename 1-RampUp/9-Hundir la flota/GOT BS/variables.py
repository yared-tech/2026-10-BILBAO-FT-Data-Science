# Board dimensions
BOARD_SIZE = 10  # 10x10 grid

# Official fleet inventory (Ship Type Name : Size/Length)
# Adapted to Game of Thrones and House of the Dragon naval warfare
FLEET_INVENTORY = {
    "Valyrian Dromon": 4,         # 1 ship of 4 positions
    "War Galley": 3,              # 2 ships of 3 positions
    "Winterfell Sailboat": 2,     # 3 ships of 2 positions
    "Landing Boat": 1             # 4 ships of 1 position
}

# Internal matrix state representations (List of lists)
TILE_WATER = 0          # Unexplored ocean (The Narrow Sea)
TILE_SHIP = 1           # Tile occupied by an allied/enemy ship
TILE_MISS = 2           # Shot fired into the water (Fitted splash)
TILE_HIT = 3            # Ship struck by the enemy
TILE_SUNK = 4           # Ship completely destroyed (Dracarys)

# RGB Colors for our future Pygame user interface
COLOR_WATER = (20, 40, 65)          # Dark ocean blue
COLOR_MISS = (40, 75, 110)          # Light blue with foam
COLOR_TARGARYEN_SHIP = (40, 40, 40) # Valyrian Black / Red sails
COLOR_LANNISTER_SHIP = (180, 30, 40)# Crimson Red / Golden details
COLOR_DRACARYS_FIRE = (255, 69, 0)  # Orange/Red fire for impacts
COLOR_TEXT = (240, 230, 140)        # Parchment gold for menus and fonts