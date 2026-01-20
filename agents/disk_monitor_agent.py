import time
import shutil
import os
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common 
import utils
import config  # Necesario para saber a quién reportar

class DiskMonitorAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class MonitorBehaviour(PeriodicBehaviour):
        async def on_start(self):
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.folder_path = os.path.join(proyecto_dir, "almacenamiento_servidor")
            if not os.path.exists(self.folder_path): os.makedirs(self.folder_path)
            
            self.limit_bytes = 500 * 1024 * 1024 
            self.alert_sent = False
            self.in_critical_state = False 

        def get_size(self, folder):
            total = 0
            for dirpath, _, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp): total += os.path.getsize(fp)
            return total

        # --- NUEVO: Función auxiliar de reporte ---
        async def report_to_auditor(self, message_body):
            try:
                if hasattr(config, 'COORDINATOR_USER'):
                    msg = Message(to=config.COORDINATOR_USER)
                    msg.set_metadata("performative", "inform")
                    msg.body = message_body
                    await self.send(msg)
            except: pass # No bloqueamos si falla el reporte
        # ------------------------------------------

        async def clean_disk(self): # Nota: Cambiado a async para poder enviar mensajes
            success = False
            try:
                chaos_file = os.path.join(self.folder_path, "chaos_blob.bin")
                
                if os.path.exists(chaos_file):
                    os.remove(chaos_file)
                    msg = "🧹 RECUPERACIÓN: Archivo de Caos eliminado."
                else:
                    files = os.listdir(self.folder_path)
                    for f in files:
                        try: os.remove(os.path.join(self.folder_path, f))
                        except: pass
                    msg = f"🧹 Limpieza total. {len(files)} archivos borrados."
                
                print(f"[Monitor] {msg}")
                common.log_buffer.append({"sender": "DiskMonitor", "body": msg})
                
                # Reportar la acción de limpieza al Auditor
                await self.report_to_auditor(msg)
                
                success = True
                
            except Exception as e:
                err_msg = f"❌ Error limpieza: {e}"
                print(f"[Monitor] {err_msg}")
                common.log_buffer.append({"sender": "DiskMonitor", "body": err_msg})
            
            finally:
                # LÓGICA HCI (Métricas de Recuperación) - SE MANTIENE
                if success and self.in_critical_state:
                    self.in_critical_state = False
                    common.hci_successful_recoveries += 1
                    print(f"[HCI] 🩹 Recuperación Inmediata registrada.")

                common.cleaning_requested = False
                self.alert_sent = False
                common.critical_event_timestamp = None

        async def run(self):
            try:
                current_bytes = self.get_size(self.folder_path)
                percent = (current_bytes / self.limit_bytes) * 100
                common.current_disk_usage = round(percent, 2)

                # LÓGICA HCI (Visibilidad y Métricas) - SE MANTIENE
                if percent > 90 and common.critical_event_timestamp is None:
                    common.critical_event_timestamp = time.time()
                elif percent <= 90:
                    common.critical_event_timestamp = None

                if percent >= 100 and not self.in_critical_state:
                    self.in_critical_state = True
                    common.hci_total_incidents += 1
                    print(f"[HCI] 💥 Incidente Crítico #{common.hci_total_incidents} provocado.")

                if percent < 90 and self.in_critical_state:
                    self.in_critical_state = False
                    common.hci_successful_recoveries += 1
                    print(f"[HCI] 🩹 Recuperación Natural registrada.")
                
                # Acciones de Limpieza
                if percent >= 100 or common.cleaning_requested:
                    if percent >= 100:
                        aviso = "🚨 EMERGENCIA: Disco lleno. Iniciando limpieza..."
                        common.log_buffer.append({"sender": "DiskMonitor", "body": aviso})
                        # Avisar al auditor ANTES de limpiar
                        await self.report_to_auditor(aviso)
                    
                    await self.clean_disk()
                    return

                # Alertas (90%)
                if percent > 90 and not self.alert_sent:
                    alert_msg = f"⚠️ ALERTA: Uso al {percent:.1f}%"
                    common.log_buffer.append({"sender": "DiskMonitor", "body": alert_msg})
                    
                    # 1. Notificador SMS (Original)
                    if hasattr(self.agent, 'notification_jid'):
                        msg = Message(to=self.agent.notification_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = alert_msg
                        await self.send(msg)
                    
                    # 2. Auditor Central (Nuevo)
                    await self.report_to_auditor(f"INCIDENTE: {alert_msg}")

                    self.alert_sent = True
                
                # Reportar normalización
                elif percent < 90 and self.alert_sent:
                    self.alert_sent = False
                    await self.report_to_auditor("✅ Niveles de disco normalizados.")
                
                print(f"[Monitor] Uso: {percent:.2f}%")

            except Exception as e:
                print(f"[Monitor] Error: {e}")

    async def setup(self):
        print("[Monitor] 🟢 Agente ONLINE.")
        common.log_buffer.append({"sender": "DiskMonitor", "body": "🟢 Monitor activo."})
        
        # Reporte de inicio al Auditor
        try:
            msg = Message(to=config.COORDINATOR_USER)
            msg.set_metadata("performative", "inform")
            msg.body = "🟢 Agente Monitor Iniciado."
            await self.send(msg)
        except: pass

        b = self.MonitorBehaviour(period=2)
        self.add_behaviour(b)