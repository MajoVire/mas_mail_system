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
        async def on_start(self):
            print("[Monitor] 🏁 Sistema de protección de disco activado...")
            self.alert_sent = False 

        async def run(self):
            # 1. VERIFICAR SI HAY ORDEN DE LIMPIEZA MANUAL (Desde la Web)
            if common.cleaning_requested:
                print("[Monitor] 🧹 Orden manual recibida. Limpiando...")
                common.current_disk_usage = 45.00 
                common.cleaning_requested = False
                self.alert_sent = False 
                
                if self.agent.receiver_jid:
                    msg = Message(to=self.agent.receiver_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = "MANTENIMIENTO MANUAL: Espacio liberado."
                    await self.send(msg)
                return 

            # 2. SIMULACIÓN DE LLENADO (+2.5% cada ciclo)
            if common.current_disk_usage == 0.0:
                common.current_disk_usage = 1.0
            else:
                # Solo subimos si es menor a 100 (para evitar el 101% visual antes del chequeo)
                if common.current_disk_usage < 100:
                    common.current_disk_usage += 2.5
            
            percent_used = round(common.current_disk_usage, 2)
            # Guardamos el estado
            common.current_disk_usage = percent_used 
            
            print(f"[Monitor] Uso de Disco: {percent_used}%")

            # ----------------------------------------------------------------
            # 3. PROTOCOLO DE EMERGENCIA (AUTOPRESERVACIÓN) >= 97%
            #    Se activa ANTES de llegar al 100% para evitar el colapso.
            # ----------------------------------------------------------------
            if percent_used >= 97.0:
                print(f"[Monitor] 🚨 PELIGRO CRÍTICO ({percent_used}%). INICIANDO LIMPIEZA FORZADA.")
                
                # A) Acción Correctiva Inmediata
                common.current_disk_usage = 45.00
                common.cleaning_requested = False 
                self.alert_sent = False # Reseteamos alertas para el nuevo ciclo
                
                # B) GENERAR EMAIL AUTOMÁTICO DE SISTEMA (Lo que pediste)
                # Inyectamos directamente en la bandeja de salida para que el SenderAgent lo procese
                system_email = {
                    'to': 'admin@ucuenca.edu.ec',
                    'subj': '⚠️ REPORTE DE INCIDENTE: Limpieza Preventiva Ejecutada'
                }
                common.email_outbox.append(system_email)
                print("[Monitor] 📤 Correo de reporte generado automáticamente.")

                # C) Notificación SMS al Celular
                if self.agent.receiver_jid:
                    msg = Message(to=self.agent.receiver_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = f"CRÍTICO: Disco alcanzó {percent_used}%. Se ejecutó limpieza preventiva de emergencia."
                    await self.send(msg)
                
                return # Terminamos el ciclo aquí para no ejecutar la alerta de 90%

            # ----------------------------------------------------------------
            # 4. ALERTA ESTÁNDAR (90% - 96%)
            # ----------------------------------------------------------------
            if percent_used >= 90.0:
                if not self.alert_sent:
                    print("[Monitor] ⚠️ Umbral de advertencia superado.")
                    
                    # Recomendación requerida por la rúbrica
                    recommendation = "Elimine publicidad/papelera/spam"
                    
                    if self.agent.receiver_jid:
                        msg = Message(to=self.agent.receiver_jid)
                        msg.set_metadata("performative", "inform")
                        msg.body = f"Espacio disco {percent_used}%. {recommendation}"
                        await self.send(msg)
                        
                        self.alert_sent = True 
                        print(f"[Monitor] ✉️ Aviso enviado: '{recommendation}'")

    async def setup(self):
        print("[Monitor] 🟢 AGENTE ACTIVO. Escaneando integridad del servidor...")
        # Iniciamos en un valor seguro
        common.current_disk_usage = 1.0 
        
        b = self.CheckDiskBehaviour(period=2)
        self.add_behaviour(b)