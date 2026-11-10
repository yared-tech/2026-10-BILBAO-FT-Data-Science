import os
import shutil
from variables import DOC_TYPES, IMG_TYPES, SOFTWARE_TYPES

def crear_carpetas(ruta_descargas):
    carpetas = ['Imagenes', 'Documentos', 'Software', 'Otros']
    for carpeta in carpetas:
        ruta_carpeta = os.path.join(ruta_descargas, carpeta)
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

def organizar_descargas(ruta_descargas):
    crear_carpetas(ruta_descargas)
    
    for archivo in os.listdir(ruta_descargas):
        ruta_archivo = os.path.join(ruta_descargas, archivo)
        
        if os.path.isdir(ruta_archivo):
            continue
            
        _, extension = os.path.splitext(archivo)
        extension = extension.lower()
        
        if extension in IMG_TYPES:
            carpeta_destino = 'Imagenes'
        elif extension in DOC_TYPES:
            carpeta_destino = 'Documentos'
        elif extension in SOFTWARE_TYPES:
            carpeta_destino = 'Software'
        else:
            carpeta_destino = 'Otros'
            
        ruta_destino = os.path.join(ruta_descargas, carpeta_destino, archivo)
        
        try:
            shutil.move(ruta_archivo, ruta_destino)
            print(f"Movido: {archivo} -> {carpeta_destino}/")
        except Exception as e:
            print(f"Error al mover {archivo}: {e}")