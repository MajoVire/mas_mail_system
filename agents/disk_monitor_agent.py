import os
import time
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common

class DiskMonitorAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class MonitorBehaviour(PeriodicBehaviour):
        async def on_start(self):
            # Configuración
            self.TOTAL_LIMIT_MB = 500
            self.limit_bytes = self.TOTAL_LIMIT_MB * 1024 * 1024
            
            # RUTA DINÁMICA (La que ya te funcionaba)
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.folder_path = os.path.join(proyecto_dir, "almacenamiento_servidor")
            
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            
            self.alert_sent = False

        def get_size(self, folder):
            total = 0
            for dirpath, _, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
            return total

        # --- FUNCIÓN NUEVA: LA ESCOBA 🧹 ---
        def clean_disk(self):
            print("[Monitor] 🧹 EJECUTANDO LIMPIEZA DE DISCO...")
            try:
                files_deleted = 0
                # Buscamos todos los archivos en la carpeta
                for f in os.listdir(self.folder_path):
                    full_path = os.path.join(self.folder_path, f)
                    
                    # Solo borramos archivos (no carpetas) para evitar errores
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                        files_deleted += 1
                
                print(f"[Monitor] 🗑️ Se eliminaron {files_deleted} archivos basura.")
                
                # Reseteamos banderas
                self.alert_sent = False
                common.cleaning_requested = False # Apagamos el botón web
                
                # Avisamos en la bitácora
                if hasattr(common, 'log_buffer'):
                    common.log_buffer.append({
                        "sender": "Monitor",
                        "body": f"✅ LIMPIEZA EXITOSA: Se borraron {files_deleted} archivos. Espacio liberado."
                    })
                    
            except Exception as e:
                print(f"[Monitor] ❌ Error al limpiar: {e}")

        async def run(self):
            try:
                # 1. Medir tamaño
                current_bytes = self.get_size(self.folder_path)
                percent = (current_bytes / self.limit_bytes) * 100
                
                # 2. Actualizar Web
                common.current_disk_usage = round(percent, 2)
                current_mb = current_bytes / (1024*1024)
                print(f"[Monitor] Uso: {current_mb:.2f}MB ({percent:.2f}%)")

                # --- CASO 1: LIMPIEZA AUTOMÁTICA AL 100% ---
                if percent >= 100:
                    print("[Monitor] 💀 PELIGRO: DISCO AL 100%. INICIANDO LIMPIEZA DE EMERGENCIA.")
                    
                    # Avisamos antes de limpiar
                    if hasattr(common, 'log_buffer'):
                         common.log_buffer.append({
                            "sender": "Monitor",
                            "body": "🚨 EMERGENCIA: Disco al 100%. Limpiando automáticamente..."
                        })
                    
                    self.clean_disk() # <--- ¡LIMPIEZA AUTOMÁTICA!
                    return # Salimos del ciclo por esta vez

                # --- CASO 2: LIMPIEZA MANUAL (BOTÓN WEB) ---
                if common.cleaning_requested:
                    print("[Monitor] 👆 Se detectó clic en botón 'Liberar Espacio'.")
                    self.clean_disk() # <--- ¡LIMPIEZA MANUAL!
                    return

                # --- LÓGICA DE ALERTAS (Solo si no estamos limpiando) ---
                if percent > 90:
                    if not self.alert_sent:
                        # Enviar SMS
                        if hasattr(self.agent, 'notification_jid'):
                            msg = Message(to=self.agent.notification_jid)
                            msg.set_metadata("performative", "inform")
                            msg.body = f"ALERTA CRITICA: Disco al {percent:.2f}%."
                            await self.send(msg)
                            
                            # Log Web
                            if hasattr(common, 'log_buffer'):
                                common.log_buffer.append({
                                    "sender": "Monitor",
                                    "body": f"⚠️ ALERTA: Disco al {percent:.2f}%"
                                })
                        
                        self.alert_sent = True
                else:
                    self.alert_sent = False
                    
            except Exception as e:
                print(f"[Monitor] Error ciclo: {e}")

    async def setup(self):
        print("[Monitor] 🟢 Agente ONLINE (Con Limpieza Automática).")
        b = self.MonitorBehaviour(period=2)
        self.add_behaviour(b)