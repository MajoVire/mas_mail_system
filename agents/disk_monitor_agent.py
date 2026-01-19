import time
import shutil
import os
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common 
import config # <--- IMPORTANTE: Necesario para leer el usuario del coordinador

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

        async def report_to_auditor(self, message_body):
            """Función auxiliar para enviar reporte seguro al Auditor"""
            try:
                if hasattr(config, 'COORDINATOR_USER'):
                    msg = Message(to=config.COORDINATOR_USER)
                    msg.set_metadata("performative", "inform")
                    msg.body = message_body
                    await self.send(msg)
            except Exception as e:
                print(f"[Monitor] ⚠️ No se pudo reportar al auditor: {e}")

        async def clean_disk(self):
            try:
                files = os.listdir(self.folder_path)
                deleted_count = 0
                for f in files:
                    # Opcional: Proteger CSVs si lo deseas (if not f.endswith('.csv'):)
                    try:
                        os.remove(os.path.join(self.folder_path, f))
                        deleted_count += 1
                    except: pass
                
                msg = f"🧹 Limpieza ejecutada. {deleted_count} archivos borrados."
                print(f"[Monitor] {msg}")
                common.log_buffer.append({"sender": "DiskMonitor", "body": msg})
                
                # --- [NUEVO] REPORTE DE LIMPIEZA AL AUDITOR ---
                await self.report_to_auditor(msg)
                # ----------------------------------------------
                
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
                        aviso = "🚨 EMERGENCIA: Disco lleno. Limpiando..."
                        common.log_buffer.append({"sender": "DiskMonitor", "body": aviso})
                        # Reportar emergencia antes de limpiar
                        await self.report_to_auditor(aviso)
                    
                    await self.clean_disk() # Nota: Ahora es async para poder enviar mensajes dentro
                    return

                # 3. Alertas (90%)
                if percent > 90 and not self.alert_sent:
                    alert_msg = f"⚠️ ALERTA CRITICA: Uso al {percent:.1f}%"
                    common.log_buffer.append({"sender": "DiskMonitor", "body": alert_msg})
                    
                    # A. Notificador (SMS)
                    if hasattr(self.agent, 'notification_jid'):
                        msg = Message(to=self.agent.notification_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = alert_msg
                        await self.send(msg)

                    # B. [NUEVO] Auditor (Coordinador)
                    await self.report_to_auditor(f"INCIDENTE: {alert_msg}")

                    self.alert_sent = True
                
                # Resetear alerta si baja el uso
                elif percent < 90 and self.alert_sent:
                    self.alert_sent = False
                    msg_ok = "✅ Niveles de disco normalizados."
                    common.log_buffer.append({"sender": "DiskMonitor", "body": msg_ok})
                    await self.report_to_auditor(msg_ok)

                # 4. Consola (Debug)
                print(f"[Monitor] Uso: {percent:.2f}%")

            except Exception as e:
                print(f"[Monitor] Error: {e}")

    async def setup(self):
        print("[Monitor] 🟢 Agente ONLINE.")
        common.log_buffer.append({
            "sender": "DiskMonitor",
            "body": "🟢 Agente Iniciado."
        })
        
        # Reporte de inicio seguro
        try:
            msg = Message(to=config.COORDINATOR_USER)
            msg.body = "🟢 Agente Monitor Iniciado."
            await self.send(msg)
        except: pass

        b = self.MonitorBehaviour(period=2)
        self.add_behaviour(b)