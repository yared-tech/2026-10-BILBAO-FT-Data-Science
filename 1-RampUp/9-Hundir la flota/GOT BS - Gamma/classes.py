# classes.py
import variables as v

class Ship:
    """Clase que define cómo es un barco en el juego."""
    def __init__(self, name, length):
        self.name = name              # Nombre del tipo de barco (ej. "War Galley")
        self.length = length          # Cuántas casillas ocupa de largo
        self.coordinates = []         # Lista de tuplas [(x, y), ...] con su posición en el mapa
        self.hits = 0                 # Contador de veces que ha sido tocado este barco
        # --- NUEVAS VARIABLES PARA LA ANIMACIÓN DE SINKING PROGRESIVO ---
        self.sunk_time = None         # Registrará el milisegundo exacto en el que se hunde
        
    @property
    def is_sunk(self):
        """Devuelve True (Verdadero) si los impactos recibidos igualan al tamaño del barco."""
        return self.hits >= self.length


class Board:
    """Clase que gestiona los dos mapas de cada jugador (el de sus barcos y el de sus tiros)."""
    def __init__(self, player_id):
        self.player_id = player_id    # Guarda si pertenece al "Human" (Jugador) o a la "AI" (Computadora)
        self.size = v.BOARD_SIZE      # Trae el tamaño estándar (10x10) de las variables
        
        # Mapa 1: Registra dónde están colocados los barcos propios de forma oculta
        self.ship_matrix = [[v.TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        # Mapa 2: Registra los disparos que este jugador efectúa sobre el rival (Niebla de guerra)
        self.tracking_matrix = [[v.TILE_WATER for _ in range(self.size)] for _ in range(self.size)]
        
        self.ships_list = []          # Lista donde guardaremos los objetos tipo 'Ship' creados

    def receive_shot(self, x, y):
        """Procesa qué pasa cuando este tablero recibe un disparo en las coordenadas X e Y."""
        # Si la casilla ya tenía un tiro previo (fallado, tocado o hundido), avisa que ya se disparó ahí
        if self.ship_matrix[y][x] in [v.TILE_MISS, v.TILE_HIT, v.TILE_SUNK, v.TILE_EXPLODING]:
            return "ALREADY_SHOT", True

        # Si el disparo da en el agua, cambia el estado a disparo fallado (TILE_MISS)
        if self.ship_matrix[y][x] == v.TILE_WATER:
            self.ship_matrix[y][x] = v.TILE_MISS
            return "MISS", False

        # Si el disparo da en un barco
        if self.ship_matrix[y][x] == v.TILE_SHIP:
            # Ponemos la casilla en estado de explosión intermedia mientras se ejecuta la animación
            self.ship_matrix[y][x] = v.TILE_EXPLODING
            
            # Buscamos a qué barco específico de la lista le corresponden estas coordenadas
            for ship in self.ships_list:
                if (x, y) in ship.coordinates:
                    ship.hits += 1  # Le sumamos un daño al barco encontrado
                    
                    # Si con este golpe el barco se hunde por completo
                    if ship.is_sunk:
                        # Marcamos todas sus casillas como explotando para que la animación haga el efecto completo
                        for bx, by in ship.coordinates:
                            self.ship_matrix[by][bx] = v.TILE_EXPLODING
                        return "SUNK", True
                    
                    # Si le dio pero aún le quedan vidas al barco
                    return "HIT", True
                    
        return "ERROR", False

    def register_own_shot(self, x, y, result):
        """Actualiza el mapa de impactos del jugador actual según lo que respondió el rival."""
        if "HIT" in result:
            self.tracking_matrix[y][x] = v.TILE_HIT    # Guarda que acertó
        elif "SUNK" in result:
            self.tracking_matrix[y][x] = v.TILE_SUNK   # Guarda que lo hundió
        elif result == "MISS":
            self.tracking_matrix[y][x] = v.TILE_MISS   # Guarda que falló

    def has_ships_alive(self):
        """Comprueba si al jugador todavía le queda al menos un barco a flote en el mapa."""
        return any(not ship.is_sunk for ship in self.ships_list)
