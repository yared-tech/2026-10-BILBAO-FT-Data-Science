import random

# Configuración del juego (Matriz 10x10 y barcos: tamaño: cantidad)
SIZE = 10
BARCOS_CONFIG = {4: 1, 3: 2, 2: 3, 1: 4} 
tablero = [[" " for _ in range(SIZE)] for _ in range(SIZE)]

# 1. Colocación automática y aleatoria de los barcos
total_barcos = 0
for tam, cant in BARCOS_CONFIG.items():
    for _ in range(cant):
        colocado = False
        while not colocado:
            orien = random.choice(["H", "V"])
            f = random.randint(0, SIZE - 1 - (tam - 1 if orien == "V" else 0))
            c = random.randint(0, SIZE - 1 - (tam - 1 if orien == "H" else 0))
            
            # Verificar si el espacio está libre
            if all(tablero[f + (i if orien == "V" else 0)][c + (i if orien == "H" else 0)] == " " for i in range(tam)):
                for i in range(tam):
                    tablero[f + (i if orien == "V" else 0)][c + (i if orien == "H" else 0)] = "B"
                total_barcos += tam
                colocado = True

# 2. Bucle principal del juego
disparos_recibidos = 0
print("¡Bienvenido al Mini Hundir la Flota! (Introduce coordenadas como A5, B10, etc.)")

while disparos_recibidos < total_barcos:
    # Dibujar el tablero visible para el jugador
    print("\n   " + " ".join(f"{i+1:<2}" for i in range(SIZE)))
    for i, fila in enumerate(tablero):
        letra = chr(65 + i)
        # Ocultamos las "B" (barcos) mostrando espacios en su lugar
        vista_fila = [celda if celda != "B" else " " for celda in fila]
        print(f"{letra}  " + "  ".join(vista_fila))

    # Leer y validar la entrada del usuario
    entrada = input("\nIntroduce coordenada (Ej: A5): ").strip().upper()
    if not entrada or not entrada[0].isalpha() or not entrada[1:].isdigit():
        print("Formato inválido. Usa una letra (A-J) seguida de un número (1-10).")
        continue
        
    f = ord(entrada[0]) - 65
    c = int(entrada[1:]) - 1

    if not (0 <= f < SIZE and 0 <= c < SIZE):
        print("Coordenadas fuera del tablero (A-J y 1-10).")
        continue

    # Procesar el disparo en la única matriz
    celda = tablero[f][c]
    if celda == "B":
        print("¡AGUA! No, espera... ¡TOCADO!")
        tablero[f][c] = "X"
        disparos_recibidos += 1
    elif celda == " ":
        print("¡AGUA!")
        tablero[f][c] = "-"
    elif celda in ["X", "-"]:
        print("Ya habías disparado aquí. Intenta otra vez.")

print("\n¡Felicidades! Has hundido toda la flota.")
