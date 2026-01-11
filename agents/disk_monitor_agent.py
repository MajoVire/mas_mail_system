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
        # --- CORRECCIÓN AQUÍ: Agregamos 'async' ---
        async def on_start(self):
            print("[Monitor] 🏁 Comportamiento de chequeo arrancando...")
            self.alert_sent = False 

        async def run(self):
            # 1. VERIFICAR SI HAY ORDEN DE LIMPIEZA
            if common.cleaning_requested:
                print("[Monitor] 🧹 Limpiando disco...")
                common.current_disk_usage = 45.00 
                common.cleaning_requested = False
                self.alert_sent = False # Reseteamos la alarma
                
                if self.agent.receiver_jid:
                    msg = Message(to=self.agent.receiver_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = "MANTENIMIENTO: Espacio liberado."
                    await self.send(msg)
                return 

            # 2. SIMULACIÓN DE LLENADO DE DISCO
            if common.current_disk_usage == 0.0 or common.current_disk_usage == 1.0:
                # Primera lectura real
                total, used, free = shutil.disk_usage("/")
                common.current_disk_usage = round((used / total) * 100, 2)
            else:
                # Simulación: sube poco a poco si es menor a 100
                if common.current_disk_usage < 100:
                    common.current_disk_usage += 2.5
            
            percent_used = round(common.current_disk_usage, 2)
            common.current_disk_usage = percent_used # Asegurar global
            
            print(f"[Monitor] Uso: {percent_used}%")

            # 3. ALERTA INTELIGENTE (Solo una vez)
            if percent_used >= 90.0:
                if not self.alert_sent:
                    print("[Monitor] ⚠️ UMBRAL CRÍTICO. Enviando aviso...")
                    if self.agent.receiver_jid:
                        msg = Message(to=self.agent.receiver_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = f"ALERTA: Disco lleno al {percent_used}%. Liberar espacio."
                        await self.send(msg)
                        
                        self.alert_sent = True # ¡IMPORTANTE! Evita spam
                        print("[Monitor] ✉️ Alerta enviada (Pausada hasta limpiar).")

    async def setup(self):
        print("[Monitor] 🟢 AGENTE INICIADO. Escaneando sistema...")
        # Valor inicial visual para saber que cargó
        common.current_disk_usage = 1.0 
        
        # Ejecutar cada 2 segundos para que veas el efecto rápido
        b = self.CheckDiskBehaviour(period=2)
        self.add_behaviour(b)