# Importamos la librería Pygame para el motor gráfico y el manejo de ventanas
import pygame
# Importamos sys para poder cerrar el programa de forma limpia y liberar memoria
import sys
# Importamos math para los cálculos de ángulos, rotaciones y parábolas balísticas
import math
# Importamos os para gestionar rutas de archivos de forma compatible en cualquier sistema operativo
import os
# Importamos random para generar números y elecciones aleatorias durante el juego
import random

# Importamos el archivo de configuración con los colores, tamaños y estados de casillas
import variables as v
# Importamos el objeto Tablero desde el módulo de clases
from classes import Board
# Importamos las funciones para colocar los barcos y calcular los movimientos de la IA
from functions import place_ships_randomly, get_lannister_ai_coordinates

# Arrancamos los módulos base del motor gráfico Pygame
pygame.init()
# Forzamos a que la ventana de juego aparezca centrada en el monitor del usuario
os.environ['SDL_VIDEO_CENTERED'] = '1'

# --- INICIALIZACIÓN DE AUDIO NATIVO ---
# Arrancamos el mezclador de sonido de Pygame para gestionar los canales de audio
pygame.mixer.init()
# Obtenemos la ruta absoluta de la carpeta donde se está ejecutando este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Forzamos las variables globales de efectos de sonido
global sound_fireball, sound_dracarys, sound_fly, sound_intro, sound_explosion, sound_burning, sound_splash
sound_fireball = None
sound_dracarys = None
sound_fly = None
sound_intro = None
sound_explosion = None
sound_burning = None
sound_splash = None

try:
    # Construimos las rutas universales hacia la carpeta de almacenamiento de sonidos
    path_fire = os.path.join(BASE_DIR, "assets", "sounds", "fireball_launch.wav")
    path_dragon = os.path.join(BASE_DIR, "assets", "sounds", "dracarys_fire.wav")
    path_fly = os.path.join(BASE_DIR, "assets", "sounds", "dragon_wings.wav")
    path_intro = os.path.join(BASE_DIR, "assets", "sounds", "dragon_fly.wav")
    path_explosion = os.path.join(BASE_DIR, "assets", "sounds", "fireball_explosion.wav")
    path_burning = os.path.join(BASE_DIR, "assets", "sounds", "ship_burning.wav")
    path_splash = os.path.join(BASE_DIR, "assets", "sounds", "water_splash.wav") # <-- NUEVO
    
    # Si los archivos existen físicamente en el ordenador, los cargamos y asignamos su volumen máximo (1.0)
    if os.path.exists(path_fire):
        sound_fireball = pygame.mixer.Sound(path_fire)
        sound_fireball.set_volume(1.0)
        
    if os.path.exists(path_dragon):
        sound_dracarys = pygame.mixer.Sound(path_dragon)
        sound_dracarys.set_volume(1.0)
        
    if os.path.exists(path_fly):
        sound_fly = pygame.mixer.Sound(path_fly)
        sound_fly.set_volume(1.0)
        
    if os.path.exists(path_intro):
        sound_intro = pygame.mixer.Sound(path_intro)
        sound_intro.set_volume(1.0)
        
    if os.path.exists(path_explosion):
        sound_explosion = pygame.mixer.Sound(path_explosion)
        sound_explosion.set_volume(1.0)
        
    if os.path.exists(path_burning):
        sound_burning = pygame.mixer.Sound(path_burning)
        sound_burning.set_volume(1.0)
        
    if os.path.exists(path_splash):
        sound_splash = pygame.mixer.Sound(path_splash)
        sound_splash.set_volume(1.0) # Potencia total para el impacto en el mar
except Exception as e:
    # Si falla algún hardware de audio o falta un archivo, capturamos el fallo para que el juego no se cierre en seco
    print(f"Aviso en precarga de efectos de sonido: {e}")

# --- CÁLCULO PROPORCIONAL DE DIMENSIONES DINÁMICAS ---
# Le preguntamos a Pygame el tamaño real de la pantalla de la máquina donde se ejecuta
monitor_info = pygame.display.Info()
# Guardamos el ancho máximo de la pantalla detectado en píxeles
screen_max_width = monitor_info.current_w
# Guardamos el alto máximo de la pantalla detectado en píxeles
screen_max_height = monitor_info.current_h

# Ajustamos el tamaño de cada casilla del tablero para que ocupe el 75% del alto disponible de la pantalla
CELL_SIZE = int((screen_max_height * 0.75) / v.BOARD_SIZE)
# Calculamos el ancho total del tablero multiplicando el tamaño de casilla por las 10 de juego
BOARD_WIDTH = CELL_SIZE * v.BOARD_SIZE
# Dejamos una separación táctica entre los dos tableros equivalente a una casilla y media
TACTICAL_GAP = CELL_SIZE * 1.5
# Ancho total que ocuparán los dos mapas juntos en horizontal con su separación intermedia
TOTAL_FLEET_WIDTH = (BOARD_WIDTH * 2) + TACTICAL_GAP

# Calculamos el punto de inicio X exacto para que todo el bloque de juego quede perfectamente centrado horizontalmente
START_X = (screen_max_width - TOTAL_FLEET_WIDTH) // 2
# Calculamos el punto de inicio Y exacto para que todo el bloque de juego quede perfectamente centrado verticalmente
START_Y = (screen_max_height - BOARD_WIDTH) // 2

# Iniciamos la ventana a pantalla completa absoluta utilizando escalado nativo acelerado
screen = pygame.display.set_mode((screen_max_width, screen_max_height), pygame.FULLSCREEN | pygame.SCALED)
# Definimos el título superior de la ventana del juego
pygame.display.set_caption("BATTLE OF THE NARROW SEA")
# Inicializamos el reloj interno de control de tiempo del motor gráfico
clock = pygame.time.Clock()

# --- CONFIGURACIÓN DE TIPOGRAFÍAS DE LA INTERFAZ ---
# Creamos la fuente tipográfica para los títulos principales basándonos en el tamaño de casilla calculado
font_title = pygame.font.SysFont("serif", int(CELL_SIZE * 0.7), bold=True)
# Creamos la fuente para los subtítulos decorativos aplicando estilo itálico o cursivo
font_sub = pygame.font.SysFont("serif", int(CELL_SIZE * 0.4), italic=True)
# Creamos la fuente estándar para los elementos e indicadores de la interfaz de usuario
font_ui = pygame.font.SysFont("serif", int(CELL_SIZE * 0.35), bold=True)
# --- NUEVA FUENTE DUPLICADA PARA LA INTERFAZ DE COMBATE ---
# Creamos una tipografía específica y de gran tamaño para rotular los nombres de los bandos en partida
font_game_ui = pygame.font.SysFont("serif", int(CELL_SIZE * 0.7), bold=True)

# --- CONFIGURACIÓN DE SPRITES ---
# Bandera lógica para activar el uso de archivos de imágenes para los gráficos del juego
USING_SPRITES = True
# Bandera para controlar si se dibuja la textura repetible para el fondo marino
USING_OCEAN_SPRITE = False
# Bandera para activar el renderizado avanzado de barcos con imágenes en lugar de formas planas
USING_SHIPS_SPRITES = True  

# Variable para almacenar el lienzo o textura de la imagen de fondo del océano
img_bg_ocean = None
# Definimos el tamaño estándar en píxeles (512x512) para los fragmentos del mosaico marino
TILE_SIZE = 512

# Diccionario para guardar las imágenes de los barcos intactos pertenecientes al bando Targaryen
dict_ships_targaryen = {}
# Diccionario para guardar las imágenes de los barcos intactos pertenecientes al bando Lannister
dict_ships_lannister = {}
# Diccionario para las imágenes de los barcos Targaryen dañados o parcialmente quemados
dict_ships_targaryen_burnt = {}
# Diccionario para las imágenes de los barcos Lannister dañados o parcialmente quemados
dict_ships_lannister_burnt = {}

# LISTA PARA LOS 12 FRAMES INDEPENDIENTES DE DROGON
# Lista ordenada para almacenar los 12 fotogramas individuales de la animación del dragón
LIST_DROGON_FRAMES = []
# Lista para guardar las imágenes secuenciales que componen la animación del logotipo del menú
LIST_TITLE_FRAMES = []
# --- LISTA PARA LA ANIMACIÓN REAL DE LA BOLA DE FUEGO ---
# Lista dedicada a almacenar las 4 imágenes consecutivas del proyectil balístico normal de fuego
LIST_FIREBALL_FRAMES = []
# Lista dinámica para registrar y actualizar las partículas activas de las explosiones comunes
LIST_ACTIVE_EXPLOSIONS = []


try:
    # Obtenemos el directorio base donde se encuentra ejecutándose el script de Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Construimos la ruta de acceso al directorio que almacena todas las imágenes del juego
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

    # Carga secuencial exacta de title_1.png, title_2.png y title_3.png
    # Bucle para leer y cargar uno a uno los tres fotogramas correspondientes al logotipo principal
    for i in range(1, 4):
        # Generamos la ruta específica para el archivo del logotipo con su índice correspondiente
        title_path = os.path.join(ASSETS_DIR, f"title_{i}.png")
        # Si el archivo gráfico existe físicamente dentro del disco del ordenador
        if os.path.exists(title_path):
            # Cargamos la imagen aplicando optimización de transparencia alfa a la lista de títulos
            LIST_TITLE_FRAMES.append(pygame.image.load(title_path).convert_alpha())
    
    # Construimos la ruta correspondiente para la imagen de fondo del océano repetible
    ocean_path = os.path.join(ASSETS_DIR, "background_ocean.png")
    # Si el archivo del fondo marino se localiza correctamente dentro del directorio de imágenes
    if os.path.exists(ocean_path):
        # Cargamos el fondo y lo escalamos fijamente a las dimensiones del azulejo estándar (512x512)
        img_bg_ocean = pygame.transform.scale(pygame.image.load(ocean_path).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        # Activamos la bandera para permitir el renderizado del fondo marino con movimiento fluido
        USING_OCEAN_SPRITE = True

    # Bucle automático para cargar en orden las texturas de los barcos desde el tamaño 1 al 4
    for i in range(1, 5):
        # Generamos la ruta para la imagen del barco intacto del jugador (Targaryen)
        p_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}.png")
        # Generamos la ruta para la imagen del barco intacto de la computadora (Lannister)
        a_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}.png")
        # Generamos la ruta para la imagen del barco dañado y quemado del jugador humano
        p_burnt_path = os.path.join(ASSETS_DIR, f"ship_targaryen_{i}_burnt.png")
        # Generamos la ruta para la imagen del barco dañado y quemado del oponente electrónico
        a_burnt_path = os.path.join(ASSETS_DIR, f"ship_lannister_{i}_burnt.png")
        
        # Si el sprite del barco sano Targaryen existe, lo añadimos indexed a su respectivo diccionario
        if os.path.exists(p_path): dict_ships_targaryen[i] = pygame.image.load(p_path).convert_alpha()
        # Si el sprite del barco sano Lannister existe, lo añadimos indexed a su respectivo diccionario
        if os.path.exists(a_path): dict_ships_lannister[i] = pygame.image.load(a_path).convert_alpha()
        # Si el sprite del barco en llamas Targaryen existe, lo añadimos a su almacén correspondiente
        if os.path.exists(p_burnt_path): dict_ships_targaryen_burnt[i] = pygame.image.load(p_burnt_path).convert_alpha()
        # Si el sprite del barco en llamas Lannister existe, lo añadimos a su almacén correspondiente
        if os.path.exists(a_burnt_path): dict_ships_lannister_burnt[i] = pygame.image.load(a_burnt_path).convert_alpha()

    # Carga de tus 12 archivos HD transparentes de la cinemática
    # Bucle secuencial para importar las 12 imágenes consecutivas que dan forma al vuelo del dragón Drogon
    for i in range(1, 13):
        # Trazamos la ruta del archivo de imagen individual asignándole su número correlativo
        drogon_path = os.path.join(ASSETS_DIR, f"drogon_{i}.png")
        # Si el fotograma transparente de la criatura se encuentra en la ruta especificada
        if os.path.exists(drogon_path):
            # Guardamos el gráfico procesado con transparencia optimizada dentro de la lista de Drogon
            LIST_DROGON_FRAMES.append(pygame.image.load(drogon_path).convert_alpha())

    # Carga automática secuencial de fireball_1.png a fireball_4.png de fábrica
    # Bucle indexado para cargar las 4 texturas de las animaciones balísticas comunes de fuego
    for i in range(1, 5):
        # Trazamos el enlace hacia la imagen de la bola de fuego correspondiente a su índice
        ball_path = os.path.join(ASSETS_DIR, f"fireball_{i}.png")
        # Si el recurso visual de artillería existe de manera efectiva en los archivos
        if os.path.exists(ball_path):
            # Incorporamos el fotograma optimizado dentro de la lista estructurada para proyectiles comunes
            LIST_FIREBALL_FRAMES.append(pygame.image.load(ball_path).convert_alpha())
except Exception:
    # Capturamos cualquier error en la lectura de ficheros gráficos para impedir el cuelgue prematuro
    pass

# --- CONTROLADOR COMPLETO SIN AVISOS DE TIPADO ---
# Definimos la clase encargada de gobernar todos los estados y datos del vuelo del dragón Drogon
class DragonAnimationController:
    # Método constructor para iniciar las propiedades de control internas de la animación de la criatura
    def __init__(self):
        # Propiedad lógica para saber si el dragón está actualmente cruzando la pantalla de juego
        self.is_active = False
        # Almacena el valor de píxel de la coordenada horizontal actual de la posición del dragón
        self.current_x = 0.0
        # Almacena el valor de píxel de la coordenada vertical actual de la posición del dragón
        self.current_y = 0.0
        # Coordenada horizontal en píxeles del punto de destino exacto donde debe atacar el dragón
        self.target_px_x = 0.0
        # Coordenada vertical en píxeles del punto de destino exacto donde debe atacar el dragón
        self.target_px_y = 0.0
        # Factor incremental constante para controlar el desplazamiento en horizontal por fotograma
        self.vx = 0.0  
        # Factor incremental constante para controlar el desplazamiento en vertical por fotograma
        self.vy = 0.0  
        # Guarda los grados de inclinación que debe tener la imagen para que apunte hacia donde se mueve
        self.angle_deg = 0.0      
        # Cambia a True cuando el dragón termina su ráfaga de fuego y comienza a escapar del mapa
        self.escape_phase = False  
        # Velocidad constante medida en píxeles de avance que utiliza la criatura en su recorrido
        self.speed = 7             
        # Índice que apunta a cuál de las 12 imágenes del dragón se debe dibujar en el frame actual
        self.frame_index = 0
        # Indicador lógico que cambia a True en el instante en que el dragón desata su aliento de fuego
        self.fire_triggered = False
        # Registra el sentido del vuelo de la criatura (de izquierda a derecha o de derecha a izquierda)
        self.direction = "L_TO_R"
        # Temporizador incremental de ciclos de reloj para regular la velocidad del batido de las alas
        self.step_timer = 0
        
        # --- NUEVA VARIABLE DE CONTROL DE PLANEO ---
        # Guarda la distancia geométrica original en píxeles desde el spawn hasta la casilla diana
        self.initial_distance = 0.0
        
        # Almacena de forma fija la columna exacta del tablero que el dragón va a carbonizar
        self.burn_col = 0
        # Almacena de forma fija la fila exacta del tablero que el dragón va a carbonizar
        self.burn_row = 0
        # Retiene una referencia de memoria directa hacia el objeto del tablero que está sufriendo el ataque
        self.active_board = None
        # Bandera que cambia a verdadero para evitar que el daño del tablero se compute más de una vez
        self.burned_done = False


# --- CONTROLADOR COMPLETO PARA LA BOLA DE FUEGO DE ARTILLERÍA ---
# Definimos la clase encargada de gestionar los tiros parabólicos en impactos comunes (TOCADO)
class FireballAnimationController:
    # Método constructor para iniciar los atributos de control internos de la bola de fuego
    def __init__(self):
        # Propiedad que marca si el proyectil balístico se encuentra actualmente cruzando el mapa
        self.is_active = False
        # Ubicación horizontal de píxel en tiempo real que ocupa la bola de fuego en la pantalla
        self.current_x = 0.0
        # Ubicación vertical de píxel en tiempo real que ocupa la bola de fuego en la pantalla
        self.current_y = 0.0
        # Coordenada horizontal del píxel exacto del centro de la casilla que recibirá la explosión
        self.target_px_x = 0.0
        # Coordenada vertical del píxel exacto del centro de la casilla que recibirá la explosión
        self.target_px_y = 0.0
        # Coordenada horizontal de inicio desde donde fue disparada la bola de fuego
        self.start_x = 0.0
        # Coordenada vertical de inicio desde donde fue disparada la bola de fuego
        self.start_y = 0.0
        # Velocidad de progresión constante calculada en el eje horizontal
        self.vx = 0.0
        # Velocidad de progresión constante calculada en el eje vertical
        self.vy = 0.0
        # Establece la velocidad del proyectil balístico, configurada más rápida que la del dragón
        self.speed = 11.0         
        # Determina cuál de las 4 imágenes de fuego de la lista se debe mostrar en este fotograma
        self.frame_index = 4       
        # Temporizador para controlar de manera fluida las transiciones de las llamas de artillería
        self.step_timer = 0
        # Almacena el recorrido total inicial para poder deducir la hipérbole tridimensional de altura
        self.initial_distance = 0.0
        # --- AÑADE ESTAS 3 LÍNEAS AQUÍ ABAJO ---
        # Registra la columna de la cuadrícula sobre la cual se va a registrar de forma oficial el impacto
        self.burn_col = 0
        # Registra la fila de la cuadrícula sobre la cual se va a registrar de forma oficial el impacto
        self.burn_row = 0
        # Guarda un enlace hacia la instancia de tablero que está bajo fuego balístico activo
        self.active_board = None


# Inicializamos las instancias de los controladores gráficos globales para el motor de animaciones
fireball_cinema = FireballAnimationController()
dragon_cinema = DragonAnimationController()

def draw_scrolling_ocean(surface):
    # Si la opción de usar imágenes de fondo está desactivada o la imagen no existe
    if not USING_OCEAN_SPRITE or img_bg_ocean is None:
        # Rellenamos toda la pantalla con el color azul marino plano definido en las variables
        surface.fill(v.COLOR_SEA_BACKGROUND)
        # Salimos inmediatamente de la función para no ejecutar el resto del código
        return
    # Obtenemos el tiempo transcurrido en milisegundos desde que se inició el juego
    time_ms = pygame.time.get_ticks()
    # Calculamos el desplazamiento horizontal del agua dividiendo el tiempo para controlar la velocidad
    scroll_x = int((time_ms / 160) % TILE_SIZE)
    # Calculamos el desplazamiento vertical del agua dividiendo el tiempo entre un valor diferente para dar un ángulo diagonal
    scroll_y = int((time_ms / 200) % TILE_SIZE)
    # Recorremos la pantalla a lo ancho en bucle saltando según el tamaño del sprite para crear un mosaico
    for x in range(-TILE_SIZE, surface.get_width() + TILE_SIZE, TILE_SIZE):
        # Recorremos la pantalla a lo alto en bucle saltando según el tamaño del sprite de manera vertical
        for y in range(-TILE_SIZE, surface.get_height() + TILE_SIZE, TILE_SIZE):
            # Dibujamos el trozo de océano en la pantalla aplicando los desfases de movimiento calculados
            surface.blit(img_bg_ocean, (x + scroll_x, y + scroll_y))


def draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player):
    # Elegimos el diccionario de barcos normales (intactos) según si el tablero analizado pertenece al jugador o a la IA
    live_dict = dict_ships_targaryen if is_player else dict_ships_lannister
    # Elegimos el diccionario de barcos quemados (dañados) según el bando del jugador correspondiente
    burnt_dict = dict_ships_targaryen_burnt if is_player else dict_ships_lannister_burnt
    # Si alguno de los diccionarios con las imágenes de los barcos está vacío, salimos para evitar errores de dibujo
    if not live_dict or not burnt_dict: return
    
    # Creamos una copia exacta del mapa de barcos para poder modificarlo internamente mientras leemos sus casillas
    temp_matrix = [[board.ship_matrix[r][c] for c in range(v.BOARD_SIZE)] for r in range(v.BOARD_SIZE)]
    # Creamos un conjunto de datos vacío para registrar qué casillas del mapa ya hemos dibujado en este fotograma
    drawn_cells = set()
    # Capturamos los milisegundos transcurridos en el reloj del procesador para controlar las animaciones de tiempo
    current_time = pygame.time.get_ticks()
    # Calculamos un factor de tiempo basado en los milisegundos para controlar la velocidad del oleaje del barco
    time_factor = current_time / 400.0
    # Definimos la lista con todos los estados del mapa que identifican que en esa casilla hay o hubo un barco
    valid_ship_tiles = [v.TILE_SHIP, v.TILE_HIT, v.TILE_SUNK, v.TILE_EXPLODING]

    # Recorremos las 10 filas del tablero una a una en un bucle vertical principal
    for row in range(v.BOARD_SIZE):
        # Recorremos las 10 columnas de cada fila una a una en un bucle horizontal secundario
        for col in range(v.BOARD_SIZE):
            # Si esta casilla concreta ya fue procesada y dibujada anteriormente, la saltamos para no repetir el proceso
            if (row, col) in drawn_cells: continue
            # Si el valor de la casilla actual coincide con alguno de los estados que contienen barcos
            if temp_matrix[row][col] in valid_ship_tiles:
                
                # Inicializamos a cero un contador para medir cuánto mide el barco de forma horizontal
                h_len = 0
                # Contamos cuántas casillas seguidas hacia la derecha contienen trozos de barco y no han sido dibujadas aún
                while (col + h_len < v.BOARD_SIZE and temp_matrix[row][col + h_len] in valid_ship_tiles and (row, col + h_len) not in drawn_cells): h_len += 1
                # Inicializamos a cero un contador para medir cuánto mide el barco de forma vertical
                v_len = 0
                # Contamos cuántas casillas seguidas hacia abajo contienen trozos de barco y no han sido dibujadas aún
                while (row + v_len < v.BOARD_SIZE and temp_matrix[row + v_len][col] in valid_ship_tiles and (row + v_len, col) not in drawn_cells): v_len += 1

                # Si el conteo horizontal es mayor que el vertical y supera la casilla, el barco está tumbado (Horizontal)
                if h_len > v_len and h_len > 1: length, orientation = h_len, "H"
                # Si el conteo vertical es mayor o igual al horizontal y supera la casilla, el barco está de pie (Vertical)
                elif v_len >= h_len and v_len > 1: length, orientation = v_len, "V"
                # Si solo mide una casilla de tamaño, por defecto le asignamos orientación vertical básica
                else: length, orientation = 1, "V"

                # Si el barco es horizontal y la casilla de su izquierda también es barco, saltamos porque no es el inicio real
                if orientation == "H" and col > 0 and board.ship_matrix[row][col - 1] in valid_ship_tiles: continue
                # Si el barco es vertical y la casilla de arriba también es barco, saltamos porque no es el inicio real del barco
                if orientation == "V" and row > 0 and board.ship_matrix[row - 1][col] in valid_ship_tiles: continue

                # Limitamos el tamaño a un máximo de 4 casillas por seguridad para que encaje con las imágenes disponibles
                length = min(4, length)

                # Inicializamos una variable en falso para detectar si este barco ha recibido algún disparo
                is_damaged = False
                # Inicializamos una variable en verdadero suponiendo que el barco está hundido por completo
                is_completely_sunk = True 
                # Inicializamos una variable en falso para comprobar si el barco se encuentra en estado de explosión activa
                has_exploding_tile = False

                # Inicializamos a None un puntero de memoria para buscar el objeto físico Ship real dentro de la lista
                current_ship_obj = None
                # Recorremos la lista de barcos que posee este tablero de juego para sincronizar sus datos de tiempo
                for ship in board.ships_list:
                    # Si las coordenadas actuales del mapa coinciden con las guardadas en la estructura de este barco
                    if (col, row) in ship.coordinates:
                        # Guardamos la referencia de este objeto barco en nuestra variable y rompemos la búsqueda
                        current_ship_obj = ship
                        # Interrumpimos el bucle de escaneo al haber localizado el barco correspondiente
                        break

                # Recorremos cada una de las casillas que componen el largo total del barco detectado
                for i in range(length):
                    # Calculamos la fila exacta de la casilla actual dependiendo de si el barco avanza en vertical o en horizontal
                    r_cell = row + i if orientation == "V" else row
                    # Calculamos la columna exacta de la casilla actual dependiendo de si el barco avanza en vertical o en horizontal
                    c_cell = col if orientation == "V" else col + i
                    # Leemos el estado real en el que se encuentra esa casilla concreta dentro del tablero de juego
                    cell_state = board.ship_matrix[r_cell][c_cell]
                    
                    # Si el estado es TOCADO o HUNDIDO, marcamos de forma definitiva que este barco ha sufrido daños
                    if cell_state in [v.TILE_HIT, v.TILE_SUNK]: is_damaged = True
                    # Si el estado es EXPLOTANDO, activamos la bandera correspondiente para controlar la animación del proyectil
                    if cell_state == v.TILE_EXPLODING: has_exploding_tile = True
                    # Si detectamos que al menos una sola de las casillas del barco no está hundida, el barco sigue vivo
                    if cell_state != v.TILE_SUNK: is_completely_sunk = False

                # Inicializamos una variable para forzar el dibujado del barco del rival durante una cinemática de ataque
                force_reveal_this_ship = False
                # Si la animación del dragón está activa y está atacando a este tablero en concreto
                if dragon_cinema.is_active and dragon_cinema.active_board == board:
                    # Validamos de forma segura si el barco actual contiene las coordenadas exactas de la llamarada de Drogon
                    if (dragon_cinema.burn_col, dragon_cinema.burn_row) in current_ship_obj.coordinates if current_ship_obj else False:
                        # Activamos el revelado forzado para que el barco se pinte en pantalla aunque sea del rival oculto
                        force_reveal_this_ship = True

                # Si el barco tiene celdas explotando y Drogon está activo en este tablero, significa que es el barco entero atacado
                if has_exploding_tile and dragon_cinema.is_active and dragon_cinema.active_board == board:
                    # Forzamos el estado de dañado para que el sistema dibuje el aspecto quemado del barco
                    is_damaged = True
                    # Forzamos la visibilidad del barco en pantalla mientras es consumido por las llamas
                    force_reveal_this_ship = True
                    # Si el dragón aún no ha terminado su ráfaga, impedimos que se dibuje como hundido total
                    if not dragon_cinema.burned_done:
                        # Desactivamos temporalmente el estado hundido para que mantenga su escala fija de fuego
                        is_completely_sunk = False

                # Recorremos de nuevo las casillas del barco para marcarlas como procesadas y que no se vuelvan a leer
                for i in range(length):
                    # Si el barco es horizontal, borramos y registramos la casilla correspondiente en esa fila
                    if orientation == "H": temp_matrix[row][col + i] = 0; drawn_cells.add((row, col + i))
                    # Si el barco es vertical, borramos y registramos la casilla correspondiente en esa columna
                    else: temp_matrix[row + i][col] = 0; drawn_cells.add((row + i, col))
                
                # Inicializamos la opacidad del barco al máximo valor permitido (255 significa totalmente opaco)
                ship_alpha = 255
                # Inicializamos a cero los píxeles de desplazamiento vertical de hundimiento del barco en el agua
                sink_offset = 0
                # Inicializamos a cero el porcentaje de progreso decimal para usarlo en los cálculos de renderizado
                progress = 0.0
                
                # Si las casillas confirman destrucción total y el enlace al objeto barco de la lista es válido
                if is_completely_sunk and current_ship_obj:
                    # Si es el primer fotograma en el que se hunde y el temporizador interno está vacío
                    if current_ship_obj.sunk_time is None:
                        # Registramos el milisegundo exacto de Pygame en el que se ha completado la destrucción
                        current_ship_obj.sunk_time = current_time
                    
                    # Calculamos cuántos milisegundos han pasado desde que el barco comenzó a hundirse
                    elapsed = current_time - current_ship_obj.sunk_time
                    # Definimos el tiempo exacto que durará la animación de inmersión en el mar (2 segundos)
                    duration = 2000.0
                    
                    # Si el tiempo transcurrido supera el límite de los dos segundos configurados de animación
                    if elapsed >= duration:
                        # Saltamos por completo el renderizado del barco para que desaparezca definitivamente
                        continue
                    
                    # CORRECCIÓN DEFINITIVA: Forzamos la división con decimales limpios usando float() para evitar redondeos a cero
                    progress = float(elapsed) / float(duration)
                    # Calculamos el desplazamiento vertical hacia abajo multiplicando el progreso decimal por más de media casilla
                    sink_offset = int(progress * (CELL_SIZE * 0.6))
                    # Calculamos la atenuación de opacidad reduciendo el valor de 255 a 0 según el progreso exacto obtenido
                    ship_alpha = int(255 * (1.0 - progress))

                # Si la casilla pertenece al jugador humano, o el truco está activo, o se fuerza la visibilidad por animación
                if is_player or reveal_ships or force_reveal_this_ship:
                    # Seleccionamos el grupo de imágenes de barcos quemados si está dañado, o los normales si está intacto
                    current_dict = burnt_dict if is_damaged else live_dict
                    # Extraemos la imagen que coincida con el largo del barco, usando el tamaño 1 como recurso de auxilio
                    base_asset = current_dict.get(length, current_dict.get(1))
                    # Si por algún fallo de archivos no se encuentra ninguna imagen, saltamos a la siguiente casilla
                    if base_asset is None: continue
                    
                    # Si el barco ha recibido daños pero todavía tiene puntos de vida y sigue a flote en el mapa
                    if is_damaged and not is_completely_sunk:
                        # Generamos una oscilación matemática usando el seno del tiempo para simular el pulso del fuego activo
                        fire_pulse = math.sin(pygame.time.get_ticks() / 250.0) * 0.003
                        # Modificamos el factor de escala horizontal sumándole la vibración calculada del pulso
                        scale_w_factor = 1.0 + fire_pulse
                        # Modificamos el factor de escala vertical restándole la vibración para crear un efecto de deformación viva
                        scale_h_factor = 1.0 - fire_pulse
                    # Si el barco está intacto o en fase de hundimiento dinámico, mantenemos sus proporciones estables
                    else:
                        # Clavamos el modificador horizontal al 100% de escala para que no vibre
                        scale_w_factor = 1.0
                        # Clavamos el modificador vertical al 100% de escala para mantener su rigidez estructural
                        scale_h_factor = 1.0

                    # Si el barco está orientado de forma horizontal en el mapa
                    if orientation == "H":
                        # Rotamos la imagen original 90 grados hacia la izquierda para tumbarla correctamente
                        rotated_asset = pygame.transform.rotate(base_asset, 90)
                        # Calculamos el ancho final en píxeles multiplicando el tamaño de casilla por el largo y el pulso
                        target_w = int(CELL_SIZE * length * scale_w_factor)
                        # Calculamos el alto final en píxeles ajustándolo al tamaño estándar de una casilla del tablero
                        target_h = int(CELL_SIZE * scale_h_factor)
                        # Escalamos de forma definitiva la imagen rotada al tamaño en píxeles que le corresponde ocupar
                        final_ship = pygame.transform.scale(rotated_asset, (target_w, target_h))
                    # Si el barco está orientado de forma vertical en el mapa
                    else:
                        # Calculamos el ancho final en píxeles ajustándolo al tamaño estándar de una sola casilla de la cuadrícula
                        target_w = int(CELL_SIZE * scale_w_factor)
                        # Calculamos el alto final en píxeles multiplicando el tamaño de casilla por el largo y el factor de pulso
                        target_h = int(CELL_SIZE * length * scale_h_factor)
                        # Escalamos la imagen original directamente al tamaño en píxeles vertical que calculamos
                        final_ship = pygame.transform.scale(base_asset, (target_w, target_h))
                    
                    # Realizamos una copia en memoria de la superficie del barco para poder aplicar transparencias por canal alfa
                    final_ship = final_ship.copy()
                    # Creamos una capa vacía de las mismas dimensiones exactas compatible con canales de transparencia SRCALPHA
                    alpha_surface = pygame.Surface(final_ship.get_size(), pygame.SRCALPHA)
                    # Rellenamos toda la capa con un color blanco neutro inyectándole el valor de opacidad variable ship_alpha
                    alpha_surface.fill((255, 255, 255, ship_alpha))
                    # Fusionamos ambas capas multiplicando sus canales para desvanecer uniformemente el sprite del barco entero
                    final_ship.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    # Si el barco cumple las condiciones de estar totalmente destruido y hundiéndose en el mar
                    if is_completely_sunk:
                        # Creamos una superficie transparente vacía que mida exactamente lo mismo que el barco escalado
                        dark_mask = pygame.Surface(final_ship.get_size(), pygame.SRCALPHA)
                        # CORRECCIÓN DEFINITIVA: Rellenamos de color negro restando la sombra de manera proporcional con el progreso flotante seguro
                        dark_mask.fill((0, 0, 0, int(110 * (1.0 - progress))))
                        # Fusionamos la capa negra encima de la imagen del barco para mantener el oscurecido de madera quemada
                        final_ship.blit(dark_mask, (0, 0))

                    # Calculamos el ajuste de centrado en el eje X para corregir las deformaciones visuales del pulso de fuego
                    offset_x = (CELL_SIZE * length - target_w) // 2 if orientation == "H" else (CELL_SIZE - target_w) // 2
                    # Calculamos el ajuste de centrado en el eje Y para corregir las deformaciones visuales del pulso de fuego
                    offset_y = (CELL_SIZE - target_h) // 2 if orientation == "H" else (CELL_SIZE * length - target_h) // 2

                    # Determinamos la coordenada X exacta en la pantalla combinando el inicio del tablero, la columna y el ajuste
                    tile_x = x_offset + (col * CELL_SIZE) + offset_x
                    # Determinamos la coordenada Y exacta en la pantalla combinando el inicio del tablero, la fila y el ajuste
                    tile_y = y_offset + (row * CELL_SIZE) + offset_y
                    
                    # Si el barco está vivo, le sumamos un movimiento flotante vertical usando una onda senoidal basada en su posición
                    float_offset = int(math.sin(time_factor + row + col) * 3.0) if not is_completely_sunk else 0
                    
                    # Dibujamos el barco aplicando la oscilación por flote y sumándole el desplazamiento vertical de inmersión en el mar
                    surface.blit(final_ship, (tile_x, tile_y + float_offset + sink_offset))



def draw_grid(surface, x_offset, y_offset, board, reveal_ships=False, is_player=False):
    # Calculamos un factor de tiempo continuo dividiendo los milisegundos para animar los barcos sin sprites si hiciera falta
    time_factor = pygame.time.get_ticks() / 400.0
    
    # --- CAPA 1 (INFERIOR): DIBUJAMOS LA REJILLA BLANCA OPACA DE FONDO ---
    # Al pintarla primero, garantizamos que se vea con un contraste colosal en el mar turquesa.
    grid_overlay = pygame.Surface((BOARD_WIDTH + 4, BOARD_WIDTH + 4), pygame.SRCALPHA)
    # Iniciamos un bucle para dibujar las líneas horizontales y verticales basándonos en el tamaño del tablero (10)
    for i in range(v.BOARD_SIZE + 1):
        # RESTABLECIDO: Quitamos la transparencia (el 120 de alpha) y la ponemos a 255 (blanco opaco puro)
        # Dibujamos una línea blanca vertical desde el borde superior al inferior saltando según el tamaño de la casilla
        pygame.draw.line(grid_overlay, (255, 255, 255, 255), (i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_WIDTH), 3)
        # Dibujamos una línea blanca horizontal desde el borde izquierdo al derecho saltando según el tamaño de la casilla
        pygame.draw.line(grid_overlay, (255, 255, 255, 255), (0, i * CELL_SIZE), (BOARD_WIDTH, i * CELL_SIZE), 3)
    # Volcamos la superficie con las líneas blancas opacas directamente en las coordenadas iniciales del tablero correspondientes
    surface.blit(grid_overlay, (x_offset, y_offset))

    # --- CAPA 2 (INTERMEDIA): SPRITES DE LOS BARCO SUPERPUESTOS ---
    # Al mover esta llamada aquí abajo, los barcos tapan las líneas del tablero donde hay madera.
    if USING_SHIPS_SPRITES:
        # Llamamos a la función compleja de dibujo para colocar las texturas HD de los barcos adaptadas en horizontal o vertical
        draw_ships_as_single_assets(surface, x_offset, y_offset, board, reveal_ships, is_player)
    # Si la opción de usar sprites de barcos estuviera desactivada por completo en las configuraciones
    else:
        # Recorremos las filas del mapa una por una en un bucle vertical básico
        for row in range(v.BOARD_SIZE):
            # Recorremos las columnas de cada fila una por una en un bucle horizontal
            for col in range(v.BOARD_SIZE):
                # Calculamos el punto X exacto en píxeles de la pantalla para situar el cuadro plano de color
                tile_x = x_offset + (col * CELL_SIZE)
                # Calculamos el punto Y exacto en píxeles de la pantalla para situar el cuadro plano de color
                tile_y = y_offset + (row * CELL_SIZE)
                # Si la casilla contiene un barco y se cumplen las condiciones de visibilidad (ser el jugador o tener trucos)
                if board.ship_matrix[row][col] == v.TILE_SHIP and (reveal_ships or is_player):
                    # Calculamos una variación flotante vertical para que los bloques de color planos no se queden completamente rígidos
                    float_y = math.sin(time_factor + row) * 4.0
                    # Dibujamos un rectángulo relleno del color de equipo correspondiente dentro de los límites de la casilla
                    pygame.draw.rect(surface, v.COLOR_TARGARYEN_SHIP if is_player else v.COLOR_LANNISTER_SHIP, 
                                     pygame.Rect(tile_x + 4, tile_y + 4 + float_y, CELL_SIZE - 8, CELL_SIZE - 8))

    # --- CAPA 3 (SUPERIOR): ESTADOS DE LOS TIROS (AGUA, TOCADO, HUNDIDO) ---
    # Iniciamos un bucle vertical para recorrer todas las filas del tablero y procesar los impactos visuales
    for row in range(v.BOARD_SIZE):
        # Iniciamos un bucle horizontal para recorrer todas las columnas de la fila actual del tablero
        for col in range(v.BOARD_SIZE):
            # Calculamos la posición de píxel horizontal en la pantalla para esta casilla exacta de la cuadrícula
            tile_x = x_offset + (col * CELL_SIZE)
            # Calculamos la posición de píxel vertical en la pantalla para esta casilla exacta de la cuadrícula
            tile_y = y_offset + (row * CELL_SIZE)
            # Leemos el estado real en el que se encuentra la casilla dentro del tablero (agua, tocado, fallado, etc)
            tile_state = board.ship_matrix[row][col]
            
            # Máscara cinemática premium: oculta marcas en el barco atacado por Drogon
            if dragon_cinema.is_active and dragon_cinema.active_board == board and not dragon_cinema.burned_done:
                # Buscamos a través de la lista de barcos que posee este tablero de juego
                for ship in board.ships_list:
                    # Si la coordenada del incendio provocado por el dragón pertenece a los datos de este barco
                    if (dragon_cinema.burn_col, dragon_cinema.burn_row) in ship.coordinates:
                        # Si la celda de la cuadrícula que estamos analizando forma parte del cuerpo de ese mismo barco
                        if (col, row) in ship.coordinates:
                            # Si esa casilla concreta estaba en estado TOCADO o HUNDIDO por disparos previos
                            if tile_state in [v.TILE_HIT, v.TILE_SUNK]:
                                # Cambiamos de forma temporal el estado visual a agua para que el fuego del dragón tape las marcas viejas limpia y estéticamente
                                tile_state = v.TILE_WATER

            if tile_state == v.TILE_MISS:
                # Agua: Dibujamos un círculo de salpicadura azul oscuro en el centro
                pygame.draw.circle(surface, v.COLOR_MISS, (tile_x + CELL_SIZE//2, tile_y + CELL_SIZE//2), CELL_SIZE//4)
            elif tile_state == v.TILE_HIT:
                # Tocado: Cuadro naranja translúcido brillante que representa fuego activo
                hit_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                r, g, b = v.COLOR_DRACARYS_FIRE
                hit_overlay.fill((r, g, b, 125)) 
                surface.blit(hit_overlay, (tile_x, tile_y))
            elif tile_state == v.TILE_SUNK:
                # Hundido: Capa gris oscuro semitransparente para denotar destrucción total
                sunk_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                sunk_overlay.fill((40, 40, 40, 140)) 
                surface.blit(sunk_overlay, (tile_x, tile_y))


def update_and_draw_fireball_cinematic(surface):
    # Si la animación de la bola de fuego no está activa, salimos de la función
    if not fireball_cinema.is_active: return

    # --- CONTROL DE AUDIO NATIVO DURANTE EL VUELO ---
    global sound_fireball, sound_explosion
    # Si el sonido de lanzamiento está cargado en memoria
    if sound_fireball:
        # Fijamos el volumen del canal 1 al máximo (1.0)
        pygame.mixer.Channel(1).set_volume(1.0)
        # Si el canal 1 está libre, reproducimos el sonido del vuelo
        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(sound_fireball)

    # Incrementamos el contador de fotogramas interno de la bola de fuego
    fireball_cinema.step_timer += 1
    
    # Avanzamos la posición del proyectil según su velocidad calculada
    fireball_cinema.current_x += fireball_cinema.vx
    fireball_cinema.current_y += fireball_cinema.vy

    # Calculamos la distancia restante hasta la celda diana de impacto
    dx_target = fireball_cinema.target_px_x - fireball_cinema.current_x
    dy_target = fireball_cinema.target_px_y - fireball_cinema.current_y
    distance_to_target = math.sqrt(dx_target**2 + dy_target**2)

    # Calculamos el porcentaje de trayectoria recorrido (entre 0.0 y 1.0)
    pct_travelled = 1.0 - (distance_to_target / fireball_cinema.initial_distance)
    pct_travelled = max(0.0, min(1.0, pct_travelled))
    
    # Parábola invertida pura: aumenta el tamaño en el cénit para simular altura
    height_factor = 1.0 + (math.sin(pct_travelled * math.pi) * 2.2)
    
    # Controlamos los fotogramas de la animación de la llama del proyectil
    if LIST_FIREBALL_FRAMES:
        frame_idx = (fireball_cinema.step_timer // 5) % len(LIST_FIREBALL_FRAMES)
        img_ball_raw = LIST_FIREBALL_FRAMES[frame_idx]
    else:
        img_logo_path = os.path.join(ASSETS_DIR, "fireball_1.png")
        img_ball_raw = pygame.image.load(img_logo_path).convert_alpha() if os.path.exists(img_logo_path) else None

    # Si la textura es válida, la escalamos aplicando el factor de altura
    if img_ball_raw is not None:
        scale_ratio = (CELL_SIZE * 0.9 / img_ball_raw.get_width()) * height_factor
        target_w = int(img_ball_raw.get_width() * scale_ratio)
        target_h = int(img_ball_raw.get_height() * scale_ratio)
        final_fireball = pygame.transform.scale(img_ball_raw, (target_w, target_h))

        # Centramos el dibujo en la coordenada de vuelo actual
        fireball_rect = final_fireball.get_rect()
        fireball_rect.center = (int(fireball_cinema.current_x), int(fireball_cinema.current_y))
        surface.blit(final_fireball, fireball_rect)
    else:
        # Círculo plano de auxilio si fallan las imágenes en el disco
        base_size = int(CELL_SIZE * 0.5)
        target_size = int(base_size * height_factor)
        pygame.draw.circle(surface, (255, 69, 0), (int(fireball_cinema.current_x), int(fireball_cinema.current_y)), target_size // 2)

    # --- DETECCION DEL IMPACTO EN LA CELDA OBJETIVO ---
    if distance_to_target < 12:
        # Desactivamos el vuelo en el controlador lógico
        fireball_cinema.is_active = False
        
        # Paramos de inmediato el audio de vuelo en el canal 1
        if sound_fireball:
            pygame.mixer.Channel(1).stop()

        # ACTIVACIÓN DEL SONIDO DE EXPLOSIÓN EN EL IMPACTO
        if sound_explosion:
            sound_explosion.play()
        
        # Tiñamos la celda afectada de forma definitiva como TOCADO (TILE_HIT)
        if fireball_cinema.active_board:
            row, col = fireball_cinema.burn_row, fireball_cinema.burn_col
            fireball_cinema.active_board.ship_matrix[row][col] = v.TILE_HIT
        
        # Generamos las 20 partículas de la explosión visual
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2.0, 5.5)
            particle = {
                "x": fireball_cinema.target_px_x,
                "y": fireball_cinema.target_px_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "radius": random.uniform(6.0, 12.0),
                "alpha": 255,
                "color": random.choice([(255, 69, 0), (255, 140, 0), (255, 215, 0)])
            }
            LIST_ACTIVE_EXPLOSIONS.append(particle)



def update_and_draw_dragon_cinematic(surface):
    # Si la animación del dragón no está activa o faltan los fotogramas, salimos de la función
    if not dragon_cinema.is_active or not LIST_DROGON_FRAMES: return

    # --- DECLARACIÓN GLOBAL EN LA PRIMERA LÍNEA (AÑADIDO SOUND_INTRO) ---
    global sound_dracarys, sound_fly, sound_intro
    # --------------------------------------------------------------------------

    # Incrementamos el contador de fotogramas interno para llevar el ritmo de las alas
    dragon_cinema.step_timer += 1
    
    # 1. AVANCE VECTORIAL EN LÍNEA RECTA ABSOLUTA HACIA SU DIANA
    # Avanzamos la posición horizontal del dragón sumándole su velocidad vx constante
    dragon_cinema.current_x += dragon_cinema.vx
    # Avanzamos la posición vertical del dragón sumándole su velocidad vy constante
    dragon_cinema.current_y += dragon_cinema.vy

    # 2. LOGÍSTICA DE DISTANCIA PARA EL GATILLO DEL FUEGO Y AUDIO
    # Calculamos la distancia horizontal restante restando la posición actual a la del píxel objetivo
    dx_target = dragon_cinema.target_px_x - dragon_cinema.current_x
    # Calculamos la distancia vertical restante restando la posición actual a la del píxel objetivo
    dy_target = dragon_cinema.target_px_y - dragon_cinema.current_y
    # Hallamos la distancia geométrica real restante en línea recta usando el teorema de Pitágoras
    distance_to_target = math.sqrt(dx_target**2 + dy_target**2)

    # ANTICIPACIÓN ACÚSTICA DEL RUGIDO (Cambio cinematográfico de Dracarys)
    # Si el dragón no está escapando y se encuentra a menos de 680 píxeles del barco rival
    if not dragon_cinema.escape_phase:
        if distance_to_target < 680 and sound_dracarys:
            # Fijamos el volumen del canal número 2 dedicado al rugido del dragón al 100%
            pygame.mixer.Channel(2).set_volume(1.0)
            # Si el canal número 2 no está ocupado reproduciendo sonido actualmente
            if not pygame.mixer.Channel(2).get_busy():
                # Reproducimos el efecto de sonido de Dracarys de forma controlada
                pygame.mixer.Channel(2).play(sound_dracarys)

    # 3. CONTROL DE FOTOGRAMAS ESTRICTO DE 3 FASES CON PLANEO DINÁMICO
    # Si el dragón aún no ha llegado a la zona exacta para desatar el fuego sobre el barco
    if not dragon_cinema.fire_triggered:
        # FASE 1: Si está en la primera mitad del trayecto total, planea majestuoso con alas abiertas
        if distance_to_target > (dragon_cinema.initial_distance / 2):
            # Clavamos el índice de fotograma en 0 (imagen estática con las alas totalmente extendidas)
            dragon_cinema.frame_index = 0
            
            # --- MIENTRAS PLANEA AL INICIO: DISPARAMOS EL RUGIDO EN EL CANAL 4 ---
            if sound_intro:
                if not pygame.mixer.Channel(4).get_busy():
                    pygame.mixer.Channel(4).play(sound_intro)
            
            if sound_fly:
                # Silenciamos el aleteo común para priorizar el rugido majestuoso inicial
                pygame.mixer.Channel(3).stop()
        else:
            # --- TERMINA EL PLANEO: APAGAMOS EL RUGIDO INICIAL CON UN SUAVE FADEOUT ---
            if sound_intro:
                pygame.mixer.Channel(4).fadeout(500) # Se desvanece rápido en medio segundo
                
            # En la segunda mitad del trayecto, empieza a batir las alas con fuerza cada 6 frames
            if dragon_cinema.step_timer % 6 == 0:
                # Alternamos de forma cíclica entre los primeros 4 fotogramas de vuelo de la criatura
                dragon_cinema.frame_index = (dragon_cinema.frame_index + 1) % 4
                
                # MOMENTO 1 DE ALETEO: Solo si no está ocupado y guarda cierta distancia
                if sound_fly and distance_to_target >= 260:
                    if not pygame.mixer.Channel(3).get_busy():
                        pygame.mixer.Channel(3).play(sound_fly)
                
        # Si la criatura llega a menos de 260 píxeles de la diana, activa el gatillo de ataque
        if distance_to_target < 260:
            dragon_cinema.fire_triggered = True
            # Forzamos el fotograma 4 donde el dragón abre las fauces para escupir fuego
            dragon_cinema.frame_index = 4  
            dragon_cinema.escape_phase = False 
            
    elif dragon_cinema.fire_triggered and not dragon_cinema.escape_phase:
        # FASE 2: Crescendo progresivo del Dracarys (Cada 5 frames)
        if sound_fly:
            # Apagamos las alas mientras la ráfaga de fuego está activa
            pygame.mixer.Channel(3).stop()
            
        # Avanzamos la animación de la llamarada cada 5 fotogramas del reloj
        if dragon_cinema.step_timer % 5 == 0:
            # Recorremos de forma progresiva los fotogramas del 4 al 11 (llamarada máxima)
            if dragon_cinema.frame_index < 11:
                dragon_cinema.frame_index += 1
            else:
                # Al alcanzar el fotograma 11 la ráfaga termina y el dragón pasa a fase de huida
                dragon_cinema.escape_phase = True
                dragon_cinema.frame_index = 2 
                
        # MOMENTO DEL IMPACTO REAL: Si está muy encima de la celda y el daño no se ha ejecutado
        if distance_to_target < 60 and not dragon_cinema.burned_done:
            dragon_cinema.burned_done = True     
            if dragon_cinema.active_board:
                # Recorremos la matriz entera buscando los segmentos del barco que estaban ocultos explotando
                for r in range(v.BOARD_SIZE):
                    for c in range(v.BOARD_SIZE):
                        if dragon_cinema.active_board.ship_matrix[r][c] == v.TILE_EXPLODING:
                            # Cambiamos las casillas del barco a estado HUNDIDO (TILE_SUNK) de forma definitiva
                            dragon_cinema.active_board.ship_matrix[r][c] = v.TILE_SUNK
    else:
        # FASE 3: Huida majestuosa batiendo alas con ritmo pausado premium (% 18)
        if sound_dracarys:
            # Aplicamos un desvanecimiento progresivo de 1 segundo al sonido del fuego del dragón
            pygame.mixer.Channel(2).fadeout(1000) 
        
        # Ralentizamos la animación de las alas a 18 fotogramas para dar un aspecto pesado y realista
        if dragon_cinema.step_timer % 18 == 0:
            if dragon_cinema.frame_index == 2: 
                dragon_cinema.frame_index = 1 
            else:
                dragon_cinema.frame_index = (dragon_cinema.frame_index + 1) % 4 
                
            # MOMENTO 2 DE ALETEO: Mientras huye de la pantalla
            if sound_fly:
                if not pygame.mixer.Channel(3).get_busy():
                    pygame.mixer.Channel(3).play(sound_fly)

    # 4. COMPENSADOR DE ESCALA QUIRÚRGICO SEGÚN EL FRAME
    # Obtenemos el sprite crudo que corresponde al índice de animación actual
    raw_sprite = LIST_DROGON_FRAMES[dragon_cinema.frame_index]
    # Si está escupiendo fuego (fotogramas 4 al 11) se agranda a 7.5 casillas; si vuela solo mide 3.8
    target_size = int(CELL_SIZE * 7.5) if 4 <= dragon_cinema.frame_index <= 11 else int(CELL_SIZE * 3.8)
    # Escalamos el sprite al tamaño correspondiente para simular cercanía o ráfaga
    scaled_dragon = pygame.transform.scale(raw_sprite, (target_size, target_size))
    
    # 5. ENFOQUE MATEMÁTICO REAL DE LA TEXTURA
    # Hallamos el ángulo del movimiento usando el arcotangente de las velocidades vx y vy
    movement_angle = math.atan2(dragon_cinema.vy, dragon_cinema.vx)
    # Convertimos los radianes a grados y sumamos 90 para orientar la cabeza hacia el vector de avance
    angle_degrees = math.degrees(-movement_angle) + 90.0
    # Rotamos la superficie de la imagen de forma limpia siguiendo los grados calculados
    rotated_dragon = pygame.transform.rotate(scaled_dragon, angle_degrees)

    # Centramos de forma matemática la textura rotada sobre la posición de vuelo real
    dragon_rect = rotated_dragon.get_rect()
    dragon_rect.center = (int(dragon_cinema.current_x), int(dragon_cinema.current_y))
    # Volcamos de forma definitiva el dragón sobre la superficie del juego
    surface.blit(rotated_dragon, dragon_rect)

    # PARCHE DE SEGURIDAD EXTREMA: Si el dragón vuela a más de 500 píxeles fuera de los márgenes
    if (dragon_cinema.current_x < -500 or dragon_cinema.current_x > surface.get_width() + 500 or
        dragon_cinema.current_y < -500 or dragon_cinema.current_y > surface.get_height() + 500):
        # Desactivamos por completo el controlador para liberar el turno de juego
        dragon_cinema.is_active = False
        
        # Apagamos en seco todos los canales de audio vinculados a la cinemática
        if sound_dracarys: pygame.mixer.Channel(2).stop()
        if sound_fly: pygame.mixer.Channel(3).stop()
        if sound_intro: pygame.mixer.Channel(4).stop()

def trigger_dragon_strike(target_col, target_row, target_is_ai, target_board):
    """
    Inicializa el vector de movimiento de Drogon de lado a lado.
    Sale SIEMPRE del medio vertical exacto de la pantalla y calcula la distancia inicial.
    """
    # Determinamos el desplazamiento horizontal en píxeles dependiendo de si se ataca a la IA o al humano
    offset_x = (START_X + BOARD_WIDTH + TACTICAL_GAP) if target_is_ai else START_X
    # Hallamos la coordenada X exacta en píxeles del centro de la casilla que va a ser atacada
    px_x = offset_x + (target_col * CELL_SIZE) + (CELL_SIZE // 2)
    # Hallamos la coordenada Y exacta en píxeles del centro de la casilla que va a ser atacada
    px_y = START_Y + (target_row * CELL_SIZE) + (CELL_SIZE // 2)

    # Activamos el controlador lógico del dragón y restablecemos sus estados de animación a cero
    dragon_cinema.is_active = True
    dragon_cinema.target_px_x = px_x
    dragon_cinema.target_px_y = px_y
    dragon_cinema.fire_triggered = False
    dragon_cinema.escape_phase = False
    dragon_cinema.frame_index = 0
    dragon_cinema.step_timer = 0
    
    # Registramos las coordenadas de la celda y el tablero concreto para aplicar los daños retrasados
    dragon_cinema.burn_col = target_col
    dragon_cinema.burn_row = target_row
    dragon_cinema.active_board = target_board
    dragon_cinema.burned_done = False

    # SPAWN RIGIDAMENTE CENTRADO: Nace siempre estrictamente en la mitad del lateral de la pantalla
    # Guardamos el centro vertical del monitor del usuario para calcular el nacimiento simétrico
    medio_pantalla_y = float(screen_max_height // 2)

    # Si el ataque va hacia el mapa de la IA, el dragón emerge por la izquierda; si va al humano, por la derecha
    if target_is_ai:
        dragon_cinema.direction = "L_TO_R"
        dragon_cinema.current_x = -250.0
        dragon_cinema.current_y = medio_pantalla_y
    else:
        dragon_cinema.direction = "R_TO_L"
        dragon_cinema.current_x = float(screen_max_width + 250)
        dragon_cinema.current_y = medio_pantalla_y

    # TRAYECTORIA LINEAL PURA: Calculamos el ángulo real y fijo directo hacia la celda del barco
    # Restamos las posiciones actuales a las posiciones de destino para hallar los catetos del triángulo
    dx = px_x - dragon_cinema.current_x
    dy = px_y - dragon_cinema.current_y
    # Aplicamos el arcotangente matemático para obtener el ángulo de inclinación de la trayectoria de vuelo
    angle = math.atan2(dy, dx)
    
    # --- REGISTRO DE DISTANCIA INICIAL ---
    # Almacenamos la distancia exacta de spawn para poder calcular la mitad del camino en el update
    dragon_cinema.initial_distance = math.sqrt(dx**2 + dy**2)
    
    # Guardamos los componentes fijos vx y vy de forma constante para el tiro rectilíneo
    # Multiplicamos el coseno del ángulo por la velocidad para obtener el desplazamiento por frame en X
    dragon_cinema.vx = math.cos(angle) * dragon_cinema.speed
    # Multiplicamos el seno del ángulo por la velocidad para obtener el desplazamiento por frame en Y
    dragon_cinema.vy = math.sin(angle) * dragon_cinema.speed


def trigger_fireball_strike(target_col, target_row, target_is_ai, target_board):
    # Calculamos la coordenada X de la celda en píxeles basándonos en si el disparo va al mapa de la IA o no
    offset_x = (START_X + BOARD_WIDTH + TACTICAL_GAP) if target_is_ai else START_X
    # Hallamos el centro en píxeles horizontal de la casilla objetivo del tiro
    px_x = offset_x + (target_col * CELL_SIZE) + (CELL_SIZE // 2)
    # Hallamos el centro en píxeles vertical de la casilla objetivo del tiro
    px_y = START_Y + (target_row * CELL_SIZE) + (CELL_SIZE // 2)

    # Activamos el controlador de la bola de fuego y ponemos su reloj interno a cero
    fireball_cinema.is_active = True
    fireball_cinema.target_px_x = px_x
    fireball_cinema.target_px_y = px_y
    fireball_cinema.step_timer = 0
    
    # --- ASIGNAMOS LOS DATOS DE QUEMA ---
    # Guardamos la columna, la fila y la referencia del tablero para teñir la casilla al impactar
    fireball_cinema.burn_col = target_col
    fireball_cinema.burn_row = target_row
    fireball_cinema.active_board = target_board

    # El proyectil se genera fijado verticalmente en el centro de la pantalla y en los extremos horizontales
    medio_pantalla_y = float(screen_max_height // 2)
    fireball_cinema.current_x = -250.0 if target_is_ai else float(screen_max_width + 250)
    fireball_cinema.current_y = medio_pantalla_y

    # Calculamos la inclinación angular directa hacia la casilla diana usando el arcotangente
    dx = px_x - fireball_cinema.current_x
    dy = px_y - fireball_cinema.current_y
    angle = math.atan2(dy, dx)
    
    # Registramos la distancia inicial y descomponemos la velocidad constante en los componentes vx y vy
    fireball_cinema.initial_distance = math.sqrt(dx**2 + dy**2)
    fireball_cinema.vx = math.cos(angle) * fireball_cinema.speed
    fireball_cinema.vy = math.sin(angle) * fireball_cinema.speed


def check_any_ship_burning(board1, board2):
    """Escanea ambos tableros en tiempo real buscando celdas en estado TOCADO."""
    # Recorremos de manera anidada las 10 filas del mapa
    for row in range(v.BOARD_SIZE):
        # Recorremos de manera anidada las 10 columnas del mapa
        for col in range(v.BOARD_SIZE):
            # Si en alguno de los dos tableros hay una celda marcada con estado TOCADO (barco en llamas)
            if board1.ship_matrix[row][col] == v.TILE_HIT or board2.ship_matrix[row][col] == v.TILE_HIT:
                # Devolvemos True inmediatamente confirmando que hay incendios activos en el mapa
                return True
    # Si tras revisar las 100 casillas de ambos mapas no encuentra nada, devuelve falso
    return False

def main():
    # Recuperamos la referencia global del sonido de agua para poder activarlo desde aquí
    global sound_splash
    # Declaramos el estado de arranque inicial del juego apuntando a la pantalla del menú
    game_state = "MENU"
    # Instanciamos los dos tableros de juego asignándoles sus respectivos bandos lógicos
    player_board = Board(player_id="Human")
    ai_board = Board(player_id="AI")
    # Invocamos al colocador procedural aleatorio para desplegar la flota del jugador humano
    place_ships_randomly(player_board, v.FLEET_INVENTORY)
    # Invocamos al colocador procedural aleatorio para desplegar la flota del rival electrónico (IA)
    place_ships_randomly(ai_board, v.FLEET_INVENTORY)
    # Declaramos las banderas para el turno del jugador, el fin de partida y el modo trucos
    player_turn, game_over, cheat_mode = True, False, False
    # Variable de texto para registrar el bando que consiga alzarse con la victoria
    winner_text = ""

    # Inicializamos a None el temporizador del disparo programado para la inteligencia artificial
    ai_scheduled_shot = None

    # --- MÚSICA DE FONDO EN BUCLE INFINITO PARA LA EXPOSICIÓN ---
    # Inicializamos la variable vacía para que sea accesible globalmente en toda la función main
    musica_fondo = None
    # Intentamos cargar de forma segura la música ambiente para el juego
    try:
        # Construimos la ruta de acceso directa hacia el archivo de sonido de la música de fondo
        PATH_MUSICA = os.path.join(BASE_DIR, "assets", "sounds", "got_ambient.wav")
        # Si el archivo de audio got_ambient.wav existe físicamente en el ordenador
        if os.path.exists(PATH_MUSICA):
            # Cargamos la pista de audio ambiental dentro del motor de sonido de Pygame
            musica_fondo = pygame.mixer.Sound(PATH_MUSICA)
            # Fijamos el volumen inicial bajo (0.20) para que actúe de ambiente y no tape los efectos
            musica_fondo.set_volume(0.20)
            # Activamos la reproducción asignando loops=-1 para que la música se repita de forma infinita
            musica_fondo.play(loops=-1)
        # Si el archivo no existe en el ordenador, mostramos un aviso en la consola de comandos
        else:
            print(f"Aviso: Guarda el archivo convertido como got_ambient.wav en: {PATH_MUSICA}")
    # Si falla la tarjeta de sonido del monitor o hay un problema de hardware en la exposición
    except Exception as e:
        # Capturamos el fallo de audio para que el juego arranque y funcione de manera 100% segura
        print(f"El juego continuará de forma segura sin audio debido a un conflicto de hardware: {e}")


    # --- BUCLE DE JUEGO PRINCIPAL E INFINITO (60 FPS) ---
    while True:
        # Rellenamos de forma fija el fondo con el color plano azul marino de seguridad
        screen.fill(v.COLOR_SEA_BACKGROUND)
        # Invocamos la función para dibujar y desplazar el mosaico con las texturas del océano
        draw_scrolling_ocean(screen)

        # --- CONTROL DE VOLUMEN DINÁMICO SEGÚN LA PANTALLA ---
        # Si el objeto de la música se ha cargado correctamente en memoria y no ha dado error de hardware
        if musica_fondo is not None:
            # Si el jugador se encuentra actualmente en la pantalla de inicio
            if game_state == "MENU":
                # Ponemos la potencia de la música alta al 0.8 como me has pedido para el menú
                musica_fondo.set_volume(0.8)
            # Si el jugador ya ha pulsado jugar y está en la pantalla del mapa de combate
            elif game_state == "GAME":
                # Bajamos el volumen de fondo al 0.20 para que no moleste ni tape las explosiones o al dragón
                musica_fondo.set_volume(0.20)

        # Si el estado de flujo del juego se encuentra clavado en la pantalla de inicio (MENU)
        if game_state == "MENU":
            # --- ANIMACIÓN DEL LOGOTIPO GRANDE CON EFECTO PING-PONG ---
            # Consultamos los milisegundos transcurridos en el reloj del procesador
            time_ms = pygame.time.get_ticks()
            
            # Si las imágenes del logotipo animado de las fuentes se cargaron con éxito
            if LIST_TITLE_FRAMES and len(LIST_TITLE_FRAMES) >= 3:
                # Generamos un ciclo de 4 pasos espaciados por segundo y medio (1500 milisegundos)
                virtual_step = (time_ms // 1500) % 4
                # Si llega al paso 3, forzamos el fotograma 1 para crear el efecto de rebote simétrico
                if virtual_step == 3:
                    frame_title_idx = 1  
                # En cualquier otro paso, seguimos de forma correlativa el índice del paso virtual
                else:
                    frame_title_idx = virtual_step  
                # Extraemos la textura del logotipo que corresponde dibujar en este instante
                img_raw_logo = LIST_TITLE_FRAMES[frame_title_idx]
            # Si las listas de fotogramas están vacías, cargamos directamente el recurso base plano
            else:
                img_logo_path = os.path.join(ASSETS_DIR, "title_1.png")
                img_raw_logo = pygame.image.load(img_logo_path).convert_alpha() if os.path.exists(img_logo_path) else None

            # Si el puntero gráfico del logotipo contiene una textura válida cargada en memoria
            if img_raw_logo is not None:
                # Fijamos el ancho del logotipo para que ocupe de forma estable el 45% de la pantalla
                logo_w = int(screen_max_width * 0.45)
                # Calculamos el alto de forma proporcional dividiendo las dimensiones de la imagen cruda
                logo_h = int(logo_w * (img_raw_logo.get_height() / img_raw_logo.get_width()))
                # Redimensionamos la textura final aplicando el ancho y alto corregidos proporcionalmente
                img_final_logo = pygame.transform.scale(img_raw_logo, (logo_w, logo_h))
                
                # Obtenemos el rectángulo contenedor de la textura del título para su posicionamiento
                logo_rect = img_final_logo.get_rect()
                # Colocamos el centro del logo en mitad del ancho y a un tercio del alto, sumándole un leve flote senoidal
                logo_rect.center = (screen.get_width() // 2, screen.get_height() // 3 + int(math.sin(time_ms / 250.0) * 3))
                # Dibujamos de manera definitiva la imagen final del logotipo animado en el lienzo
                screen.blit(img_final_logo, logo_rect)

            # --- INTERFAZ DE BOTONERA INTERNACIONAL AJUSTADA ---
            # Capturamos las coordenadas X e Y en píxeles de la posición del puntero del ratón
            mouse_pos = pygame.mouse.get_pos()
            # Almacenamos el centro horizontal absoluto de la pantalla
            center_x = screen.get_width() // 2
            
            # Calculamos las dimensiones del botón Jugar (ancho y alto) basándonos en las casillas
            btn_w, btn_h = int(CELL_SIZE * 2.5), int(CELL_SIZE * 0.7)
            # Calculamos las dimensiones del botón Salir basándonos en la misma proporción de casillas
            btn_leave_w, btn_leave_h = int(CELL_SIZE * 2.5), int(CELL_SIZE * 0.7)
            
            # Creamos el rectángulo virtual del botón PLAY ajustando su posición en la mitad inferior
            play_rect = pygame.Rect(center_x - btn_w // 2, screen.get_height() // 2 + 210, btn_w, btn_h)
            # Creamos el rectángulo virtual del botón LEAVE un bloque más abajo en vertical
            exit_rect = pygame.Rect(center_x - btn_leave_w // 2, screen.get_height() // 2 + 295, btn_leave_w, btn_leave_h)
            
            # Comprobamos si las coordenadas del ratón colisionan dentro de los márgenes del botón Jugar
            is_play_hovered = play_rect.collidepoint(mouse_pos)
            # Trazamos la ruta del archivo de imagen para el aspecto estético del botón PLAY
            img_play_path = os.path.join(ASSETS_DIR, "btn_play.png")
            
            # Si el archivo del sprite del botón Jugar se localiza con éxito dentro del disco duro
            if os.path.exists(img_play_path):
                # Cargamos y redimensionamos el botón a las proporciones en píxeles requeridas de juego
                img_play = pygame.transform.scale(pygame.image.load(img_play_path).convert_alpha(), (btn_w, btn_h))
                # Dibujamos la textura del botón PLAY directamente en la pantalla sobre su rectángulo virtual
                screen.blit(img_play, play_rect)
                # Si el ratón del usuario se encuentra flotando activamente encima del botón Jugar
                if is_play_hovered:
                    # Creamos una capa del mismo tamaño con soporte para transparencias semitranslúcidas
                    glow_overlay = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                    # Rellenamos esta capa con un color naranja y un valor alfa muy tenue (35) para hacer un destello
                    glow_overlay.fill((255, 95, 0, 35))  
                    # Superponemos la capa de brillo encima de la textura del botón para denotar interacción
                    screen.blit(glow_overlay, play_rect)
            # Si falta la imagen de fábrica del botón, recurrimos a dibujar un bloque genérico de texto
            else:
                # Dibujamos un rectángulo gris oscuro plano con bordes ligeramente redondeados
                pygame.draw.rect(screen, (20, 20, 20), play_rect, border_radius=4)
                # Volcamos un rótulo tipográfico dorado centrado en el medio geométrico del rectángulo
                screen.blit(font_ui.render("PLAY", True, (212, 175, 55)), font_ui.render("PLAY", True, (212, 175, 55)).get_rect(center=play_rect.center))

            # Comprobamos si las coordenadas de apuntado del ratón colisionan en los márgenes del botón Salir
            is_exit_hovered = exit_rect.collidepoint(mouse_pos)
            # Trazamos la ruta de acceso al sprite para el acabado estético del botón LEAVE
            img_exit_path = os.path.join(ASSETS_DIR, "btn_leave.png")
            
            # Si la imagen correspondiente al botón de abandono existe en el almacenamiento del PC
            if os.path.exists(img_exit_path):
                # Cargamos la textura y la adaptamos de forma exacta al tamaño en píxeles del botón Salir
                img_exit = pygame.transform.scale(pygame.image.load(img_exit_path).convert_alpha(), (btn_leave_w, btn_leave_h))
                # Dibujamos la textura del botón Salir sobre su respectivo rectángulo en la pantalla
                screen.blit(img_exit, exit_rect)
                # Si el ratón del jugador se localiza posicionado encima de la zona del botón Salir
                if is_exit_hovered:
                    # Inicializamos una superficie semitransparente vacía adaptada al tamaño del botón
                    glow_overlay = pygame.Surface((btn_leave_w, btn_leave_h), pygame.SRCALPHA)
                    # Rellenamos el cuadro con la tonalidad de destello naranja translúcido de valor 35
                    glow_overlay.fill((255, 95, 0, 35))
                    # Superponemos el destello encima del botón Salir para retroalimentar al usuario
                    screen.blit(glow_overlay, exit_rect)
            # Si el sprite de abandono no está disponible, dibujamos el botón de auxilio de texto plano
            else:
                # Pintamos un bloque rectangular gris oscuro plano respetando las medidas virtuales del botón
                pygame.draw.rect(screen, (20, 20, 20), exit_rect, border_radius=4)
                # Volcamos la tipografía en color oro viejo alineada al centro del rectángulo del botón Salir
                screen.blit(font_ui.render("LEAVE", True, (212, 175, 55)), font_ui.render("LEAVE", True, (212, 175, 55)).get_rect(center=exit_rect.center))

            # --- CAPTURA DE EVENTOS DENTRO DEL MENÚ ---
            # Iniciamos un bucle para revisar cada evento o acción que detecte la ventana de Pygame
            for event in pygame.event.get():
                # Si el usuario pulsa la cruz de cerrar o la tecla de Escape (K_ESCAPE) en su teclado
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # Apagamos los módulos internos de Pygame y salimos de la ejecución del sistema
                    pygame.quit(); sys.exit()
                # Si el jugador realiza un clic con el botón del ratón dentro de la pantalla
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Si las coordenadas del clic colisionan dentro del botón virtual PLAY
                    if play_rect.collidepoint(event.pos): 
                        # Cambiamos el estado de flujo a GAME para saltar a la pantalla de la batalla
                        game_state = "GAME"
                    # Si las coordenadas del clic colisionan dentro del botón virtual LEAVE
                    elif exit_rect.collidepoint(event.pos): 
                        # Cerramos los procesos de Pygame y liberamos toda la memoria del ordenador
                        pygame.quit(); sys.exit()
                        
        elif game_state == "GAME":
            # --- INTERFAZ SUPERIOR CENTRADA Y GIGANTE (PLAYER E IA) ---
            # Renderizamos el texto "PLAYER" usando la fuente grande y el color blanco de la interfaz
            player_label = font_game_ui.render("PLAYER", True, v.COLOR_TEXT)
            # Renderizamos el texto "IA" usando la misma fuente grande y tipografía clara de juego
            ai_label = font_game_ui.render("IA", True, v.COLOR_TEXT)
            
            # Calculamos el punto central horizontal del tablero izquierdo (Jugador humano)
            center_player_x = START_X + (BOARD_WIDTH // 2)
            # Calculamos el punto central horizontal del tablero derecho (Inteligencia artificial)
            center_ai_x = (START_X + BOARD_WIDTH + TACTICAL_GAP) + (BOARD_WIDTH // 2)
            # Establecemos la altura vertical para colocar las etiquetas dividiendo el espacio superior
            center_vertical_y = START_Y // 2
            
            # Obtenemos los rectángulos contenedores de los textos para poder alinearlos por su centro
            rect_player = player_label.get_rect(center=(center_player_x, center_vertical_y))
            rect_ai = ai_label.get_rect(center=(center_ai_x, center_vertical_y))
            
            # Dibujamos el texto PLAYER centrado encima de la cuadrícula izquierda en la pantalla
            screen.blit(player_label, rect_player)
            # Dibujamos el texto IA centrado encima de la cuadrícula derecha en la pantalla
            screen.blit(ai_label, rect_ai)
            
            # --- RENDERIZADO DE LAS REJILLAS ---
            # Dibujamos el mapa del jugador aplicando los trucos (cheat_mode) e indicando que es el humano
            draw_grid(screen, START_X, START_Y, player_board, reveal_ships=cheat_mode, is_player=True)
            # Dibujamos el mapa de la IA aplicando los trucos para ocultar o desvelar sus barcos
            draw_grid(screen, START_X + BOARD_WIDTH + TACTICAL_GAP, START_Y, ai_board, reveal_ships=cheat_mode, is_player=False)

            # --- NUEVO CONTROLLER: GESTIÓN DE AUDIO DE BARCOS ARDIENDO EN TIEMPO REAL ---
            global sound_burning
            # Si el archivo de audio para los incendios está correctamente cargado en memoria
            if sound_burning:
                # Comprobamos frame a frame si hay alguna galera en llamas en cualquiera de los dos mapas
                if check_any_ship_burning(player_board, ai_board):
                    # Fijamos el volumen del canal número 6 (fuegos activos) al máximo (1.0)
                    pygame.mixer.Channel(6).set_volume(1.0)
                    # Si hay barcos ardiendo y el canal está libre, disparamos en bucle continuo (loops=-1)
                    if not pygame.mixer.Channel(6).get_busy():
                        pygame.mixer.Channel(6).play(sound_burning, loops=-1)
                else:
                    # En el frame exacto en que ya no quede ningún TILE_HIT activo, apagamos el fuego de inmediato
                    pygame.mixer.Channel(6).stop()

            # Si la partida ha terminado y no queda ninguna animación de dragón cruzando el cielo
            if game_over and not dragon_cinema.is_active:
                # 1. Calculamos el centro vertical exacto de la rejilla de combate
                center_board_y = START_Y + (BOARD_WIDTH // 2)
                
                # REPARADO: Fuente Garamond colosal un 45% más grande para que ocupe media celda más por cada lado
                font_epic = pygame.font.SysFont("garamond", int(CELL_SIZE * 3.2), bold=True)
                
                # Renderizado premium de textos con doble capa de relieve 3D gótico
                text_win = font_epic.render("WIN", True, (255, 215, 0))       # Oro Targaryen
                text_win_shadow = font_epic.render("WIN", True, (30, 20, 0))  # Sombra oro viejo
                text_lose = font_epic.render("LOSE", True, (220, 20, 60))     # Rojo Lannister
                text_lose_shadow = font_epic.render("LOSE", True, (40, 5, 10)) # Sombra sangre oscura
                
                # Si el ganador absoluto es el jugador humano
                if winner_text == "PLAYER":
                    # Gana el jugador: WIN en el tablero izquierdo (Human) y LOSE en el derecho (IA)
                    p_text, p_shadow, p_rect = text_win, text_win_shadow, center_player_x
                    a_text, a_shadow, a_rect = text_lose, text_lose_shadow, center_ai_x
                # Si el ganador de la partida ha sido la inteligencia artificial
                else:
                    # Gana la IA: LOSE en el tablero izquierdo (Human) y WIN en el derecho (IA)
                    p_text, p_shadow, p_rect = text_lose, text_lose_shadow, center_player_x
                    a_text, a_shadow, a_rect = text_win, text_win_shadow, center_ai_x
                
                # Volcamos las sombras y los textos con un desfase de +4 píxeles para generar relieve real
                screen.blit(p_shadow, p_shadow.get_rect(center=(p_rect + 4, center_board_y + 4)))
                screen.blit(p_text, p_text.get_rect(center=(p_rect, center_board_y)))
                screen.blit(a_shadow, a_shadow.get_rect(center=(a_rect + 4, center_board_y + 4)))
                screen.blit(a_text, a_text.get_rect(center=(a_rect, center_board_y)))

            # Iniciamos el bucle de lectura de eventos para controlar las acciones de combate en la pantalla
            for event in pygame.event.get():
                # Si se cierra la ventana o el jugador presiona la tecla de Escape (ESCAPE)
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # Interrumpimos los procesos del motor de juego y cerramos la ventana por completo
                    pygame.quit(); sys.exit()
                # Si el jugador pulsa la tecla K en el teclado, cambia el estado del modo trucos
                if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                    # Alternamos el valor booleano de cheat_mode para desvelar u ocultar los barcos rivales
                    cheat_mode = not cheat_mode
                    
                # CONTROL DE CLICS DEL JUGADOR HUMAN
                # Si hay un clic del ratón, es el turno del jugador y no hay ninguna cinemática o proyectil volando
                if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over and not dragon_cinema.is_active and not fireball_cinema.is_active:
                    # Capturamos las posiciones X e Y en píxeles del punto exacto donde se pulsó con el ratón
                    mx, my = event.pos
                    # Calculamos el punto horizontal de inicio del tablero enemigo de la inteligencia artificial
                    ai_x_offset = START_X + BOARD_WIDTH + TACTICAL_GAP
                    # Verificamos si el clic ha caído exactamente dentro de los límites del mapa de la IA
                    if ai_x_offset <= mx < ai_x_offset + BOARD_WIDTH and START_Y <= my < START_Y + BOARD_WIDTH:
                        # Convertimos los píxeles horizontales mx a la columna de matriz correspondiente (0 a 9)
                        target_x = int((mx - ai_x_offset) // CELL_SIZE)
                        # Convertimos los píxeles verticales my a la fila de matriz correspondiente (0 a 9)
                        target_y = int((my - START_Y) // CELL_SIZE)
                        
                        # Pasamos las coordenadas al tablero de la IA para procesar el impacto y obtener el resultado
                        shot_result, repeat_turn = ai_board.receive_shot(target_x, target_y)
                        
                        # Si el disparo no se ha realizado sobre una casilla previamente atacada
                        if shot_result != "ALREADY_SHOT":
                            # Registramos el impacto en nuestra matriz de seguimiento para pintar la niebla de guerra
                            player_board.register_own_shot(target_x, target_y, shot_result)

                            # --- CORRECCIÓN UNIVERSAL: REPRODUCCIÓN EN CANALES SIMULTÁNEOS (JUGADOR) ---
                            # Si el tiro falló y cayó al agua, y el sonido de salpicadura está cargado
                            if shot_result == "MISS" and sound_splash:
                                # Reproducimos el efecto de salpicadura de forma directa sin ocupar canales rígidos
                                sound_splash.play()  # <-- Usa play() directo para mezclar los sonidos
                            # --------------------------------------------------------------------------

                            # --- CAPTURA DE GATILLOS CINEMÁTICOS DEL JUGADOR ---
                            # Si el disparo del jugador ha conseguido hundir el último fragmento de un barco
                            if shot_result == "SUNK":
                                # --- MOTOR CINEMÁTICO DE CENTRADO FLOTANTE DE PÍXELES (JUGADOR) ---
                                # Inicializamos una variable vacía para buscar el objeto barco afectado
                                target_ship = None
                                # Recorremos la lista de barcos que posee la inteligencia artificial
                                for ship in ai_board.ships_list:
                                    # Si las coordenadas atacadas pertenecen a la estructura de este barco
                                    if (target_x, target_y) in ship.coordinates:
                                        # Guardamos el objeto barco encontrado y rompemos el bucle de búsqueda
                                        target_ship = ship
                                        break
                                
                                # Si hemos localizado con éxito el barco hundido en la lista de la IA
                                if target_ship:
                                    # Extraemos en listas todas las coordenadas X e Y reales de sus casillas
                                    xs = [x for (x, y) in target_ship.coordinates]
                                    ys = [y for (x, y) in target_ship.coordinates]
                                    
                                    # CÁLCULO FLOTANTE PURO: Hallamos el punto medio exacto de la eslora (ej: 1.5)
                                    center_col = (min(xs) + max(xs)) / 2.0
                                    center_row = (min(ys) + max(ys)) / 2.0
                                    
                                    # Guardamos la casilla de impacto en el controlador del dragón
                                    dragon_cinema.burn_col = target_x
                                    dragon_cinema.burn_row = target_y
                                    # Desatamos el ataque cinemático del dragón apuntando al centro matemático del barco
                                    trigger_dragon_strike(center_col, center_row, True, ai_board)
                                # Si por un fallo no se localiza el barco, lanzamos el dragón sobre la casilla clicada
                                else:
                                    trigger_dragon_strike(target_x, target_y, True, ai_board)
                            
                            # CONECTADO: Desata la bola de fuego en hipérbole al hacer un tocado común
                            elif shot_result == "HIT":
                                # Invocamos el disparo parabólico del proyectil sobre la casilla objetivo de la IA
                                trigger_fireball_strike(target_x, target_y, True, ai_board)
                                
                            # Si tras el tiro la IA ya no posee barcos con vida en el mapa, el jugador gana la partida
                            if not ai_board.has_ships_alive(): game_over, winner_text = True, "PLAYER"
                            # Asignamos el turno basándonos en si el disparo permite repetir por haber acertado
                            player_turn = repeat_turn

            # --- LÓGICA DEL TURNO DE LA INTELIGENCIA ARTIFICIAL (REPARADO Y SINCRONIZADO) ---
            # Si es el turno de la máquina, no es fin de juego y no hay animaciones activas en la pantalla
            if not player_turn and not game_over and not dragon_cinema.is_active and not fireball_cinema.is_active:
                # Si no hay ningún disparo planificado aún, programamos uno añadiendo un retraso de 600 milisegundos
                if ai_scheduled_shot is None:
                    ai_scheduled_shot = pygame.time.get_ticks() + 600
                
                # En el instante en que el tiempo actual supere la marca de disparo programada para la IA
                if pygame.time.get_ticks() >= ai_scheduled_shot:
                    # Invocamos al algoritmo inteligente en cruz para obtener las coordenadas X e Y de ataque
                    ai_x, ai_y = get_lannister_ai_coordinates(player_board)
                    # Pasamos las coordenadas al tablero del jugador humano para computar el impacto del proyectil
                    shot_result, repeat_turn = player_board.receive_shot(ai_x, ai_y)
                    # Registramos el impacto en la matriz de tiros efectuados por la inteligencia artificial
                    ai_board.register_own_shot(ai_x, ai_y, shot_result)

                    # --- CORRECCIÓN UNIVERSAL: REPRODUCCIÓN EN CANALES SIMULTÁNEOS (IA) ---
                    # Si el disparo de la máquina falla y cae al agua, y el sonido existe
                    if shot_result == "MISS" and sound_splash:
                        # Hacemos sonar de forma libre la salpicadura en el océano del mar turquesa
                        sound_splash.play()  # <-- Usa play() directo para mezclar los sonidos
                    # ----------------------------------------------------------------------

                    # --- CAPTURA DE GATILLOS CINEMÁTICOS DE LA IA ---
                    # Si el impacto provocado por el oponente electrónico hunde un barco del humano por completo
                    if shot_result == "SUNK":
                        # --- MOTOR CINEMÁTICO DE CENTRADO FLOTANTE DE PÍXELES (IA) ---
                        # Inicializamos a None el puntero de búsqueda para localizar la galera del jugador
                        target_ship = None
                        # Recorremos la lista de barcos que posee el jugador humano en su tablero
                        for ship in player_board.ships_list:
                            # Si las coordenadas atacadas por la IA corresponden a la estructura de este barco
                            if (ai_x, ai_y) in ship.coordinates:
                                # Guardamos el objeto barco correspondiente y rompemos la ejecución del bucle
                                target_ship = ship
                                break
                        
                        # Si hemos localizado con éxito el barco carbonizado del jugador en el mapa
                        if target_ship:
                            # Extraemos en listas independientes todas las posiciones X e Y de sus casillas
                            xs = [x for (x, y) in target_ship.coordinates]
                            ys = [y for (x, y) in target_ship.coordinates]
                            
                            # CÁLCULO FLOTANTE PURO: Hallamos el punto medio exacto de la eslora (ej: 1.5)
                            center_col = (min(xs) + max(xs)) / 2.0
                            center_row = (min(ys) + max(ys)) / 2.0
                            
                            # Registramos la casilla exacta dentro de la memoria de la animación de Drogon
                            dragon_cinema.burn_col = ai_x
                            dragon_cinema.burn_row = ai_y
                            # Desatamos el vuelo del dragón de derecha a izquierda sobre el centro del barco humano
                            trigger_dragon_strike(center_col, center_row, False, player_board)
                        # Si por un fallo no se localiza, lanzamos el dragón sobre la coordenada base del disparo
                        else:
                            trigger_dragon_strike(ai_x, ai_y, False, player_board)

                    # CONECTADO: La IA te lanza una bola de fuego compacta a tus galeras
                    elif shot_result == "HIT":
                        # Invocamos el proyectil balístico en parábola para que impacte la cuadrícula del humano
                        trigger_fireball_strike(ai_x, ai_y, False, player_board)
                        
                    # Si tras el ataque de la IA el humano se queda sin barcos operativos, la máquina gana
                    if not player_board.has_ships_alive(): game_over, winner_text = True, "LANNISTER"
                    # Cedemos de forma limpia el turno de juego invirtiendo la bandera de repetición
                    player_turn = not repeat_turn
                    # Restablecemos a None la planificación del disparo para permitir futuros turnos de la IA
                    ai_scheduled_shot = None

            # --- RENDERIZADO EN CAPAS DE LAS CINEMÁTICAS ACTIVAS ---
            # Si el controlador registra que el dragón está activo cruzando el lienzo gráfico
            if dragon_cinema.is_active:
                # Actualizamos las matemáticas de vuelo e imprimimos la criatura en pantalla
                update_and_draw_dragon_cinematic(screen)
                
            # Si el controlador registra que hay un proyectil común volando en hipérbole
            if fireball_cinema.is_active:
                # Actualizamos la parábola e imprimimos los sprites de fuego de artillería en pantalla
                update_and_draw_fireball_cinematic(screen)

            # --- MOTOR DE EXPRESIÓN DE PARTÍCULAS EXPANSIVAS DE ARTILLERÍA ---
            # Recorremos la lista completa de partículas utilizando un filtro de seguridad de copia [:]
            for p in LIST_ACTIVE_EXPLOSIONS[:]:
                # Avanzamos la posición horizontal de la partícula sumándole su velocidad vx
                p["x"] += p["vx"]
                # Avanzamos la posición vertical de la partícula sumándole su velocidad vy
                p["y"] += p["vy"]
                # Atenuamos la opacidad de la partícula restándole 8 puntos en cada ciclo de reloj
                p["alpha"] -= 8       
                # Incrementamos ligeramente el tamaño del radio para simular una expansión de humo realista
                p["radius"] += 0.2    
                
                # Si la opacidad de la partícula llega a cero o menos (se vuelve invisible por completo)
                if p["alpha"] <= 0:
                    # Eliminamos de forma definitiva la partícula de la lista para liberar recursos del procesador
                    LIST_ACTIVE_EXPLOSIONS.remove(p)
                # Si la partícula sigue teniendo visibilidad activa en el lienzo de juego
                else:
                    # Creamos una superficie cuadrada vacía adaptada a las dimensiones de la partícula con canal alfa
                    p_surface = pygame.Surface((int(p["radius"] * 2), int(p["radius"] * 2)), pygame.SRCALPHA)
                    # Extraemos los componentes de color Rojo, Verde y Azul almacenados en la estructura de la partícula
                    r, g, b = p["color"]
                    # Dibujamos un círculo relleno aplicando la opacidad alpha en el centro de la superficie creada
                    pygame.draw.circle(p_surface, (r, g, b, p["alpha"]), (int(p["radius"]), int(p["radius"])), int(p["radius"]))
                    # Volcamos la partícula sobre la pantalla centrándola con sus coordenadas de dispersión reales
                    screen.blit(p_surface, (int(p["x"] - p["radius"]), int(p["y"] - p["radius"])))

        # --- REFRESO Y RELOJ DEL SISTEMA CONSTANTE ---
        # Volcamos de golpe todo el lienzo dibujado en memoria oculta directamente sobre el monitor del usuario
        pygame.display.flip()
        # Clavamos de forma rígida la tasa de refresco a un máximo de 60 fotogramas por segundo
        clock.tick(60)

# --- EL GANCHO DE ARRANQUE MAESTRO DEL PROYECTO ---
# Verificación estándar de Python para iniciar la función principal si el script se arranca de forma directa
if __name__ == "__main__":
    main()


