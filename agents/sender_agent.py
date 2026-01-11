import time
import asyncio
import random
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

# Importamos la memoria compartida para leer la "Bandeja de Salida" de la Web
import common

class SenderAgent(Agent):
    def set_notification_agent(self, agent_jid):
        """Define a quién avisar cuando se envía un correo (el Notificador)"""
        self.notification_jid = agent_jid

    class SimulateSendingBehaviour(PeriodicBehaviour):
        async def run(self):
            destinatario = ""
            asunto = ""
            es_manual = False

            # ----------------------------------------------------------------
            # 1. REVISAR SI EL USUARIO ORDENÓ ENVIAR UN CORREO (Desde la Web)
            # ----------------------------------------------------------------
            if len(common.email_outbox) > 0:
                print("[Enviador] 👨‍💻 Solicitud manual detectada en la Web.")
                
                # Sacamos el primer correo de la fila (FIFO)
                email_data = common.email_outbox.pop(0)
                
                destinatario = email_data['to']
                asunto = email_data['subj']
                es_manual = True
            
            # ----------------------------------------------------------------
            # 2. SI NO HAY ÓRDENES, SIMULAR TRÁFICO AUTOMÁTICO
            # ----------------------------------------------------------------
            else:
                # Generamos un número aleatorio para no enviar spam todo el tiempo
                # Solo el 30% de las veces que despierta enviará un correo automático
                if random.random() > 0.7:
                    destinatario = "cliente_automatico@empresa.com"
                    asunto = f"Reporte automático #{random.randint(1000, 9999)}"
                    es_manual = False
                else:
                    # El 70% de las veces no hace nada, para no saturar tu celular
                    return 

            print(f"[Enviador] 📤 Procesando envío a: {destinatario}")
            
            # ----------------------------------------------------------------
            # 3. VALIDACIÓN Y ENVÍO (Lógica de Negocio)
            # ----------------------------------------------------------------
            # Requisito de la Rúbrica: Validar destinatario
            if "@" in destinatario and "." in destinatario:
                # Simulamos el tiempo que tarda un servidor SMTP real
                await asyncio.sleep(1) 
                
                # Preparamos el mensaje para el Notificador
                if self.agent.notification_jid:
                    msg = Message(to=self.agent.notification_jid)
                    msg.set_metadata("performative", "inform")
                    
                    # Diferenciamos en el SMS si fue MANUAL (tuyo) o AUTO
                    tipo = "MANUAL" if es_manual else "AUTO"
                    msg.body = f"ENVIADO ({tipo}): A {destinatario} - {asunto}"
                    
                    await self.send(msg)
                    print(f"[Enviador] ✅ Correo enviado. Notificación despachada ({tipo}).")
            else:
                print(f"[Enviador] ❌ Error: Dirección '{destinatario}' inválida. Se descarta.")

    async def setup(self):
        print("[Enviador] Agente de envíos listo. Esperando órdenes...")
        # Revisa la cola de envíos cada 5 segundos
        b = self.SimulateSendingBehaviour(period=5)
        self.add_behaviour(b)