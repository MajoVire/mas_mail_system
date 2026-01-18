# NOMBRE DEL ARCHIVO: utils.py
import os
import time
import random

def generar_carga_disco(storage_folder, prefijo="data"):
    """
    Genera un archivo artificial de 10MB en la carpeta indicada
    para simular el consumo de espacio en disco.
    
    Retorna: (Exito: bool, Mensaje: str)
    """
    try:
        # Aseguramos que la carpeta exista
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)

        # Generamos un nombre único para evitar colisiones en el mismo segundo
        # Formato: prefijo_TIMESTAMP_RANDOM.txt
        timestamp = int(time.time())
        rand_id = random.randint(1000, 9999)
        filename = f"{prefijo}_{timestamp}_{rand_id}.txt"
        filepath = os.path.join(storage_folder, filename)

        # Crear archivo de 10 MB (10 * 1024 * 1024 bytes)
        # Escribimos bytes ('wb') para que sea rápido
        with open(filepath, "wb") as f:
            f.write(b"0" * 10 * 1024 * 1024) 
            
        return True, filename
        
    except Exception as e:
        return False, str(e)