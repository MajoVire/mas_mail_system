# agents/notification_agent.py
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from twilio.rest import Client
import common
import config

class NotificationAgent(Agent):
    class RecvMsgBehaviour(CyclicBehaviour):
        async def run(self):
            # Esperamos mensaje
            msg = await self.receive(timeout=1)
            
            if msg:
                # 1. Limpieza de datos
                sender_name = str(msg.sender).split("@")[0]
                cuerpo = msg.body
                print(f"[🔔 Notificador] Recibido de {sender_name}: {cuerpo}")

                # 2. ACTUALIZAR DASHBOARD (Claves correctas: sender y body)
                entry = {
                    "sender": "Notificador",
                    "body": f"SMS ENVIADO A {config.MY_CELLPHONE}: {cuerpo}"
                }
                
                if hasattr(common, 'log_buffer'):
                    common.log_buffer.append(entry)

                # 3. ENVIAR SMS REAL (TWILIO)
                try:
                    client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)
                    message = client.messages.create(
                        body=f"🤖 ALERTA: {cuerpo}",
                        from_=config.TWILIO_FROM,
                        to=config.MY_CELLPHONE
                    )
                    print(f"[Twilio] ✅ SMS Enviado! SID: {message.sid}")
                except Exception as e:
                    print(f"[Twilio] ❌ Error: {e}")

    async def setup(self):
        print("[Notificador] 🟢 Listo y esperando alertas...")
        b = self.RecvMsgBehaviour()
        self.add_behaviour(b)