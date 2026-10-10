proyecto_x/
│
├── assets/                  # 📂 Carpeta para los recursos visuales y sonoros
│   ├── imagenes/
│   │   ├── barco_targaryen.png
│   │   ├── barco_lannister.png
│   │   └── dragon.png
│   └── fuentes/
│       └── juego_de_tronos.ttf
│
├── variables.py             # 📄 Las constantes (dimensiones, colores, etc.)
├── clases.py                # 📄 El corazón lógico (Clase Tablero y barcos)
├── funciones.py             # 📄 Herramientas auxiliares (colocación, IA de la máquina)
└── main.py                  # 🚀 El archivo principal (el que tú ejecutas para jugar)


---------------

				  ┌──────────────┐
                  │ variables.py │  <--- (No importa a nadie, todos lo importan a él)
                  └──────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │ clases.py │   │funciones.py│  │  main.py  │
   └───────────┘   └─────┬─────┘   └─────┬─────┘
                         │               │
                         └───────┬───────┘
                                 ▼
                           ┌───────────┐
                           │  main.py  │  <--- (Importa a clases y funciones)
                           └───────────┘

----------------------------


