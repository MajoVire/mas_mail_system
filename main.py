import time
import asyncio
import threading # Necesario para correr la web en paralelo
import common    # Para inicializar datos
import config

# Importar agentes
from agents.disk_monitor_agent import DiskMonitorAgent
from agents.notification_agent import NotificationAgent
from agents.receptor_agent import ReceptorAgent
from agents.sender_agent import SenderAgent

# Importar servidor web
from web.dashboard import start_web_server

async def main():
    print("--- INICIANDO SISTEMA COMPLETO (WEB + AGENTES) ---")

    # 1. Iniciar el Servidor Web en un hilo aparte
    print("🌍 Iniciando interfaz web en http://localhost:5000 ...")
    web_thread = threading.Thread(target=start_web_server)
    web_thread.daemon = True # Se cierra cuando el programa principal se cierra
    web_thread.start()

    # --- CREDENCIALES ---
    notif_user   = config.NOTIF_USER
    notif_pass   = config.NOTIF_PASS

    monitor_user = config.MONITOR_USER
    monitor_pass = config.MONITOR_PASS

    receptor_user = config.RECEPTOR_USER
    receptor_pass = config.RECEPTOR_PASS
    
    sender_user   = config.SENDER_USER
    sender_pass   = config.SENDER_PASS
    # --------------------

    # 2. Iniciar Agentes
    notificador = NotificationAgent(notif_user, notif_pass)
    notificador.verify_security = False
    await notificador.start()
    
    monitor = DiskMonitorAgent(monitor_user, monitor_pass)
    monitor.verify_security = False
    monitor.set_receiver(notif_user)
    await monitor.start()

    receptor = ReceptorAgent(receptor_user, receptor_pass)
    receptor.verify_security = False
    receptor.set_notification_agent(notif_user)
    await receptor.start()

    sender = SenderAgent(sender_user, sender_pass)
    sender.verify_security = False
    sender.set_notification_agent(notif_user)
    await sender.start()

    print(f"✅ Sistema Operativo. Abre tu navegador en http://localhost:5000")

    try:
        while True:
            # Pequeño truco: Actualizamos el uso de disco en 'common' 
            # leyendo una variable interna del monitor (si existiera)
            # O mejor, modificamos el monitor después.
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo sistema...")
        await monitor.stop()
        await notificador.stop()
        await receptor.stop()
        await sender.stop()

if __name__ == "__main__":
    asyncio.run(main())