import time
import asyncio
import threading # Necesario para correr la web en paralelo
import common    # Para inicializar datos
import config

# 1. IMPORTAR TODOS LOS AGENTES
from agents.disk_monitor_agent import DiskMonitorAgent
from agents.notification_agent import NotificationAgent
from agents.receptor_agent import ReceptorAgent
from agents.sender_agent import SenderAgent
from agents.coordinator_agent import CoordinatorAgent 

# Importar servidor web
from web.dashboard import start_web_server

async def main():
    print("--- INICIANDO SISTEMA COMPLETO (WEB + AGENTES) ---")

    # 2. Iniciar el Servidor Web en un hilo aparte
    print("🌍 Iniciando interfaz web en http://localhost:5000 ...")
    web_thread = threading.Thread(target=start_web_server)
    web_thread.daemon = True # Se cierra cuando el programa principal se cierra
    web_thread.start()

    # --- 3. LECTURA DE CREDENCIALES DESDE CONFIG ---
    notif_user   = config.NOTIF_USER
    notif_pass   = config.NOTIF_PASS

    monitor_user = config.MONITOR_USER
    monitor_pass = config.MONITOR_PASS

    receptor_user = config.RECEPTOR_USER
    receptor_pass = config.RECEPTOR_PASS
    
    sender_user   = config.SENDER_USER
    sender_pass   = config.SENDER_PASS

    coord_user    = config.COORDINATOR_USER 
    coord_pass    = config.COORDINATOR_PASS
    # -----------------------------------------------

    # 4. INICIALIZAR Y ARRANCAR AGENTES
    
    # Agente 1: Notificador (Salida SMS)
    notificador = NotificationAgent(notif_user, notif_pass)
    notificador.verify_security = False
    await notificador.start()
    
    # Agente 2: Coordinador (Auditoría central)
    coordinador = CoordinatorAgent(coord_user, coord_pass)
    coordinador.verify_security = False
    await coordinador.start()

    # Agente 3: Monitor de Disco (Infraestructura)
    monitor = DiskMonitorAgent(monitor_user, monitor_pass)
    monitor.verify_security = False
    
    # --- CORRECCIÓN AQUÍ ---
    # Cambiado de .set_receiver a .set_notification_agent para coincidir con el agente
    monitor.set_notification_agent(notif_user) 
    # -----------------------
    
    await monitor.start()

    # Agente 4: Receptor (Entrada de Correos)
    receptor = ReceptorAgent(receptor_user, receptor_pass)
    receptor.verify_security = False
    receptor.set_notification_agent(notif_user)
    await receptor.start()

    # Agente 5: Sender (Salida de Correos)
    sender = SenderAgent(sender_user, sender_pass)
    sender.verify_security = False
    sender.set_notification_agent(notif_user)
    await sender.start()

    print(f"✅ Sistema Operativo. Abre tu navegador en http://localhost:5000")
    print(f"📝 Agente Coordinador (Auditor) activo y escuchando.")

    try:
        while True:
            # Mantener el script principal vivo
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema y desconectando agentes...")
        
        # 5. APAGADO GRACIOSO DE TODOS LOS AGENTES
        await monitor.stop()
        await notificador.stop()
        await receptor.stop()
        await sender.stop()
        await coordinador.stop()
        print("--- Sistema Apagado Correctamente ---")

if __name__ == "__main__":
    asyncio.run(main())