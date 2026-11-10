import os
from funciones import organizar_descargas

def main():
    ruta_usuario = os.path.expanduser("~")
    ruta_descargas = os.path.join(ruta_usuario, "Downloads")
    
    if not os.path.exists(ruta_descargas):
        print(f"La ruta especificada no existe: {ruta_descargas}")
        return

    print(f"Iniciando la organización de la carpeta: {ruta_descargas}\n" + "-"*50)
    organizar_descargas(ruta_descargas)
    print("-"*50 + "\n¡Proceso de organización finalizado con éxito!")

if __name__ == "__main__":
    main()