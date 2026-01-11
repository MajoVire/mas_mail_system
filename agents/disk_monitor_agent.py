import time
import shutil
import asyncio
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common 

class DiskMonitorAgent(Agent):
    def set_receiver(self, receiver_jid):
        self.receiver_jid = receiver_jid

    class CheckDiskBehaviour(PeriodicBehaviour):
        def on_start(self):
            # Variable para recordar si ya enviamos la alerta
            self.alert_sent = False 

        async def run(self):
            # --- 1. VERIFICAR LIMPIEZA ---
            if common.cleaning_requested:
                print("[Monitor] 🧹 Orden de limpieza recibida...")
                common.current_disk_usage = 45.00 
                common.cleaning_requested = False
                
                # RESETEAMOS LA ALERTA: Al limpiar, permitimos que vuelva a avisar en el futuro
                self.alert_sent = False 
                
                if self.agent.receiver_jid:
                    msg = Message(to=self.agent.receiver_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = "MANTENIMIENTO: Espacio liberado."
                    await self.send(msg)
                return 

            # --- 2. MONITOREO ---
            if common.current_disk_usage == 0.0:
                total, used, free = shutil.disk_usage("/")
                common.current_disk_usage = round((used / total) * 100, 2)
            else:
                if common.current_disk_usage < 100:
                    common.current_disk_usage += 2.5
            
            percent_used = common.current_disk_usage
            common.current_disk_usage = round(percent_used, 2)
            print(f"[Monitor] Uso: {percent_used:.2f}%")

            # --- 3. ALERTA INTELIGENTE (SOLO UNA VEZ) ---
            if percent_used >= 90.0:
                # Solo entramos si NO hemos enviado la alerta todavía
                if not self.alert_sent:
                    print("[Monitor] ⚠️ ALERTA CRÍTICA: Enviando SMS...")
                    
                    if self.agent.receiver_jid:
                        msg = Message(to=self.agent.receiver_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = f"ALERTA: Disco lleno al {percent_used:.2f}%. Limpieza requerida."
                        await self.send(msg)
                        
                        # MARCAMOS QUE YA AVISAMOS
                        self.alert_sent = True 
                        print("[Monitor] ✉️ Alerta enviada (Se pausarán las alertas hasta limpiar).")
                else:
                    # Si ya avisamos, solo imprimimos en consola pero NO mandamos SMS
                    print("[Monitor] ⚠️ Estado Crítico (Alerta ya enviada anteriormente).")

    async def setup(self):
        print("[Monitor] Agente iniciado.")
        b = self.CheckDiskBehaviour(period=5)
        self.add_behaviour(b)