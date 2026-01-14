# NOMBRE DEL ARCHIVO: simulation.py
import threading
import time
import random
import uuid
import common

# Listas de datos para generar variedad semántica
ACCIONES = ["Solicitud", "Informe", "Reclamo", "Pregunta", "Urgente", "Justificativo"]
TEMAS = ["Notas Finales", "Acceso a Laboratorio", "Horario de Clases", "Tesis de Grado", "Matrícula Extemporánea", "Falta de Asistencia"]
REMITENTES_FICTICIOS = ["estudiante", "profesor", "investigador", "admin", "secretaria"]

def user_bot_activity(user_id):
    """
    Simula a un usuario único redactando y enviando un correo con contenido variado.
    """
    # 1. Retraso aleatorio para simular comportamiento humano no-sincronizado
    time.sleep(random.uniform(0.5, 2.0))
    
    # 2. Generar Destinatario Variado
    destinatarios_posibles = [
        "decano@ucuenca.edu.ec", 
        "director.carrera@ucuenca.edu.ec", 
        "secretaria.general@ucuenca.edu.ec",
        "bienestar.estudiantil@ucuenca.edu.ec",
        "soporte.tecnico@ucuenca.edu.ec"
    ]
    destinatario = random.choice(destinatarios_posibles)

    # 3. Generar Asunto Rico y Diferenciable
    accion = random.choice(ACCIONES)
    tema = random.choice(TEMAS)
    # Usamos los primeros 4 caracteres de un UUID para darle un código único real
    codigo_unico = str(uuid.uuid4())[:4]
    
    asunto = f"[{accion}] {tema} - Ref:{codigo_unico} (Usr:{user_id})"
    
    # 4. Acción: Enviar a la cola compartida
    email_data = {
        'to': destinatario, 
        'subj': asunto
    }
    
    common.email_outbox.append(email_data)
    
    # Feedback en consola para que veas la variedad
    print(f"[Simulación] 👤 Usuario {user_id} generó: '{asunto}' para {destinatario}")

def run_mass_simulation():
    """
    Dispara 10 hilos simultáneos con datos aleatorios.
    """
    print("\n--- 🎲 INICIANDO SIMULACIÓN CON DATOS VARIADOS ---")
    threads = []
    
    # Creamos 10 "usuarios" virtuales
    for i in range(1, 11):
        t = threading.Thread(target=user_bot_activity, args=(i,))
        threads.append(t)
        t.start()
    
    print(f"--- 🚀 Se han lanzado los bots. Observa el Dashboard para ver los nuevos asuntos. ---")