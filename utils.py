import os
import time
import random

def generar_carga_disco(storage_folder, prefijo="data"):
    try:
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)
        timestamp = int(time.time())
        rand_id = random.randint(1000, 9999)
        filename = f"{prefijo}_{timestamp}_{rand_id}.txt"
        filepath = os.path.join(storage_folder, filename)
        with open(filepath, "wb") as f:
            f.write(b"0" * 10 * 1024 * 1024) 
        return True, filename
    except Exception as e:
        return False, str(e)

def generar_archivo_caos(storage_folder, limite_bytes):
    """
    Calcula el espacio libre y crea un archivo que llena el disco al 100% + 1 byte.
    PROTECCIÓN: Si ya existe el archivo de caos, no hace nada (evita doble clic).
    """
    try:
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)
            
        filename = "chaos_blob.bin"
        filepath = os.path.join(storage_folder, filename)

        # --- PROTECCIÓN ANTI-SPAM (DOBLE CLIC) ---
        if os.path.exists(filepath):
            return False, "⚠️ CAOS ACTIVO: Espera a que el agente limpie.", 0
        # -----------------------------------------
            
        # 1. Calcular tamaño actual
        total_usado = 0
        for dirpath, _, filenames in os.walk(storage_folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_usado += os.path.getsize(fp)
        
        # 2. Calcular cuánto falta para el límite
        espacio_necesario = limite_bytes - total_usado
        
        if espacio_necesario <= 0:
            espacio_necesario = 10 * 1024 * 1024 
        else:
            espacio_necesario += 1024 * 1024 
            
        # 3. Crear el archivo masivo
        with open(filepath, "wb") as f:
            f.seek(int(espacio_necesario) - 1)
            f.write(b"\0")
            
        return True, filename, espacio_necesario
    except Exception as e:
        return False, str(e), 0