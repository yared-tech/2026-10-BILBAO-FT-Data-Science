# variables.py

# Board technical dimensions
BOARD_SIZE = 10  # 10x10 matrix layout

# Official fleet inventory configurations (Ship Type Name : Casillas de eslora)
FLEET_INVENTORY = {
    "Valyrian Dromon": 4,         # 1 ship of 4 positions
    "War Galley": 3,              # 2 ships of 3 positions
    "Winterfell Sailboat": 2,     # 3 ships of 2 positions
    "Landing Boat": 1             # 4 ships of 1 position
}

# Core matrix cell states numerical representation
TILE_WATER = 0          # Unexplored tactical deep ocean
TILE_SHIP = 1           # Tile containing an intact operational ship segment
TILE_MISS = 2           # Fired shot that splashed into the water
TILE_HIT = 3            # Ship segment successfully struck by dragon fire
TILE_SUNK = 4           # Ship completely carbonized and destroyed (Dracarys)

# variables.py (Complete updated color list with uniform tropical sea)

# --- VIBRANT, UNIFORM & BRIGHT RGB COLORS (Tropical sea style) ---
COLOR_WATER = (0, 191, 255)           # Deep Sky Blue (Bright tropical turquoise water)
COLOR_SEA_BACKGROUND = (0, 191, 255)  # EXACTLY THE SAME BLUE for perfect endless sea continuity
COLOR_FRAME = (255, 255, 255)         # Pure White for grids and board dividers
COLOR_MISS = (175, 238, 238)          # Pale Turquoise (Very soft light blue for foam splashes)
COLOR_TARGARYEN_SHIP = (55, 65, 80)    # Steel Grey / Clean hulls for Team Black
COLOR_LANNISTER_SHIP = (210, 105, 30)  # Warm Terracotta / Rich bronze for Team Green
COLOR_DRACARYS_FIRE = (255, 69, 0)    # Blazing high-visibility orange-red for active hits
COLOR_TEXT = (255, 255, 255)          # Pure white typography tint for clean rendering
