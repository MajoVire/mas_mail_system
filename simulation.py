import threading
import time
import random
import uuid
import common

ACCIONES = ["Solicitud", "Informe", "Reclamo", "Pregunta", "Urgente", "Justificativo"]
TEMAS = ["Notas Finales", "Acceso a Laboratorio", "Horario de Clases", "Tesis de Grado", "Matrícula Extemporánea", "Falta de Asistencia", "Reserva Auditorio"]
DESTINATARIOS_POSIBLES = [
   "mariavirecar@gmail.com",
   "majo.virecar@gmail.com"
]

def user_bot_activity(user_id):
    time.sleep(random.uniform(0.1, 1.5))
    
    destinatario = random.choice(DESTINATARIOS_POSIBLES)
    accion = random.choice(ACCIONES)
    tema = random.choice(TEMAS)
    codigo_unico = str(uuid.uuid4())[:4].upper()
    
    asunto = f"[{accion}] {tema} - Ref:{codigo_unico} (Usuario:{user_id})"
    
    # --- NUEVO: Generación de contenido del correo ---
    cuerpo = (f"Estimado/a,\n\n"
              f"Por medio de la presente hago llegar mi {accion.lower()} referente a: {tema}.\n"
              f"Quedo atento a su respuesta.\n\n"
              f"Atentamente,\n"
              f"Usuario Simulado {user_id}\n"
              f"ID Referencia: {codigo_unico}")
    
    email_data = {
        'to': destinatario, 
        'subj': asunto,
        'body': cuerpo,       # <--- Se envía el cuerpo generado
        'timestamp_in': time.time() # Importante para métricas
    }
    
    common.email_outbox.append(email_data)
    print(f"[Simulación] 👤 Usuario {user_id} generó solicitud: '{tema}'")

def run_mass_simulation():
    print("\n--- 🚀 INICIANDO EXPERIMENTO DE ESCALABILIDAD (10 USUARIOS) ---")
    
    # Reset de métricas (IMPORTANTE NO BORRAR)
    common.metrics_results["batch_start_time"] = time.time()
    common.metrics_results["total_processed"] = 0
    common.metrics_results["latencies"] = []
    
    threads = []
    for i in range(1, 11):
        t = threading.Thread(target=user_bot_activity, args=(i,))
        threads.append(t)
        t.start()
    
    print(f"--- ✅ 10 Hilos lanzados. ---")