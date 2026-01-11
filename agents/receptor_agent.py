import time
import asyncio
import json
import re  # Importante para la Rúbrica (Expresiones Regulares)
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

class ReceptorAgent(Agent):
    def set_notification_agent(self, agent_jid):
        self.notification_jid = agent_jid

    class SimulateIncomingMailBehaviour(PeriodicBehaviour):
        async def run(self):
            print("[Receptor] 📥 Esperando correos nuevos...")
            
            # --- 1. SIMULACIÓN DE CORREO ENTRANTE (JSON) ---
            # En la vida real esto vendría de un servidor POP3/IMAP
            fake_email_json = {
                "id": int(time.time()),
                "subject": "Tarea de Sistemas Multiagentes",
                "body": "Hola, adjunto el avance del proyecto.",
                "sender": "estudiante@ucuenca.edu.ec",
                "raw_to": "Para: Diego Patiño <diego.patino@ucuenca.edu.ec>" 
            }
            
            # --- 2. PARSING Y REGEX (Requisito de Rúbrica) ---
            # Usamos Regex para extraer el email limpio del campo "raw_to"
            # Busca algo que parezca un email entre < > o simplemente un email
            email_pattern = r'[\w\.-]+@[\w\.-]+'
            match = re.search(email_pattern, fake_email_json['raw_to'])
            
            if match:
                destinatario_limpio = match.group(0)
                print(f"[Receptor] Procesando correo para: {destinatario_limpio}")
                
                # --- 3. REGLA DE NEGOCIO ---
                # Ejemplo: Solo aceptamos correos institucionales
                if "ucuenca.edu.ec" in destinatario_limpio:
                    print("[Receptor] ✅ Destinatario validado (Institucional).")
                    
                    # ENVIAR AVISO AL AGENTE DE NOTIFICACIONES
                    msg = Message(to=self.agent.notification_jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = f"NUEVO CORREO: De {fake_email_json['sender']} - Asunto: {fake_email_json['subject']}"
                    
                    await self.send(msg)
                    print("[Receptor] ➔ Notificación enviada al agente SMS.")
                else:
                    print("[Receptor] ❌ Correo externo descartado por reglas.")
            else:
                print("[Receptor] ⚠️ No se encontró destinatario válido.")

    async def setup(self):
        print("[Receptor] Agente de recepción iniciado.")
        # Revisar "correos" cada 20 segundos
        b = self.SimulateIncomingMailBehaviour(period=20)
        self.add_behaviour(b)