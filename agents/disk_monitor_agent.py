import time
import shutil
import os
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common 

class DiskMonitorAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class MonitorBehaviour(PeriodicBehaviour):
        async def on_start(self):
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.folder_path = os.path.join(proyecto_dir, "almacenamiento_servidor")
            if not os.path.exists(self.folder_path): os.makedirs(self.folder_path)
            self.limit_bytes = 500 * 1024 * 1024 # 500 MB Límite
            self.alert_sent = False

        def get_size(self, folder):
            total = 0
            for dirpath, _, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp): total += os.path.getsize(fp)
            return total

        def clean_disk(self):
            try:
                files = os.listdir(self.folder_path)
                for f in files:
                    os.remove(os.path.join(self.folder_path, f))
                
                msg = f"🧹 Limpieza ejecutada. {len(files)} archivos borrados."
                print(f"[Monitor] {msg}")
                common.log_buffer.append({"sender": "DiskMonitor", "body": msg})
                
                common.cleaning_requested = False
                self.alert_sent = False
            except Exception as e:
                print(f"[Monitor] Error limpieza: {e}")

        async def run(self):
            try:
                # 1. Medir
                current_bytes = self.get_size(self.folder_path)
                percent = (current_bytes / self.limit_bytes) * 100
                common.current_disk_usage = round(percent, 2)

                # 2. Limpieza Manual o Automática (100%)
                if percent >= 100 or common.cleaning_requested:
                    if percent >= 100:
                        common.log_buffer.append({"sender": "DiskMonitor", "body": "🚨 EMERGENCIA: Disco lleno. Limpiando..."})
                    self.clean_disk()
                    return

                # 3. Alertas (90%)
                if percent > 90 and not self.alert_sent:
                    alert_msg = f"⚠️ ALERTA CRITICA: Uso al {percent:.1f}%"
                    common.log_buffer.append({"sender": "DiskMonitor", "body": alert_msg})
                    
                    if hasattr(self.agent, 'notification_jid'):
                        msg = Message(to=self.agent.notification_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = alert_msg
                        await self.send(msg)
                    self.alert_sent = True
                
                # 4. REPORTE HEARTBEAT (Opcional: para ver que está vivo)
                # Solo reporta a la web si cambia significativamente o cada X ciclos
                # Para no saturar, aquí solo imprimimos en consola
                print(f"[Monitor] Uso: {percent:.2f}%")

            except Exception as e:
                print(f"[Monitor] Error: {e}")

    async def setup(self):
        print("[Monitor] 🟢 Agente ONLINE.")
        common.log_buffer.append({
            "sender": "DiskMonitor",
            "body": "🟢 Monitor de almacenamiento activo."
        })
        b = self.MonitorBehaviour(period=2)
        self.add_behaviour(b)