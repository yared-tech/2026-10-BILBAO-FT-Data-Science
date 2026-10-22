# variables.py

# Tamaño del tablero de juego (10 casillas de ancho por 10 de alto)
BOARD_SIZE = 10  

# Inventario de barcos disponibles y su tamaño (eslora/casillas que ocupan)
FLEET_INVENTORY = {
    "Valyrian Dromon": 4,         # 1 barco de 4 casillas
    "War Galley": 3,              # 2 barcos de 3 casillas
    "Winterfell Sailboat": 2,     # 3 barcos de 2 casillas
    "Landing Boat": 1             # 4 barcos de 1 casilla
}

# Representación numérica de los estados de cada casilla del tablero
TILE_WATER = 0       # Casilla de agua donde nadie ha disparado
TILE_SHIP = 1        # Casilla que contiene un trozo de barco intacto
TILE_MISS = 2        # Disparo fallado (cayó al agua)
TILE_HIT = 3         # Trozo de barco tocado/al que han dado
TILE_SUNK = 4        # Barco completamente hundido y destruido
TILE_EXPLODING = 5   # Estado interno para cuando el proyectil viaja por el aire

# --- COLORES EN FORMATO RGB (Rojo, Verde, Azul) PARA LA INTERFAZ ---
COLOR_WATER = (0, 191, 255)           # Azul cielo brillante para el mar visible
COLOR_SEA_BACKGROUND = (0, 191, 255)  # El mismo azul para el fondo del océano infinito
COLOR_FRAME = (255, 255, 255)         # Blanco puro para las líneas de la cuadrícula
COLOR_MISS = (10, 50, 110)            # Azul oscuro para marcar los disparos fallados
COLOR_TARGARYEN_SHIP = (55, 65, 80)    # Gris acero para los barcos del jugador
COLOR_LANNISTER_SHIP = (210, 105, 30)  # Terracota/Bronce para los barcos de la IA
COLOR_DRACARYS_FIRE = (255, 69, 0)    # Naranja-rojo brillante para los barcos tocados
COLOR_TEXT = (255, 255, 255)          # Blanco puro para los textos de la pantalla
