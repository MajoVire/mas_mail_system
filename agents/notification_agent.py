from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from twilio.rest import Client
import common
import config

class NotificationAgent(Agent):
    class RecvMsgBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            
            if msg:
                sender_name = str(msg.sender).split("@")[0]
                cuerpo = msg.body
                print(f"[🔔 Notificador] Mensaje de {sender_name}: {cuerpo}")

                # --- 1. REPORTE A BITÁCORA (RESTITUIDO) ---
                # Esto es lo que permite ver el log en la web
                common.log_buffer.append({
                    "sender": "Notificador",
                    "body": f"SMS ENVIADO A {config.MY_CELLPHONE}: {cuerpo}"
                })

                # --- 2. ENVÍO SMS REAL (TWILIO) ---
                try:
                    client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)
                    message = client.messages.create(
                        body=f"🤖 {sender_name}: {cuerpo}",
                        from_=config.TWILIO_FROM,
                        to=config.MY_CELLPHONE
                    )
                    print(f"[Twilio] ✅ SMS Enviado! SID: {message.sid}")
                except Exception as e:
                    err_msg = f"Error enviando SMS: {e}"
                    print(f"[Twilio] ❌ {err_msg}")
                    common.log_buffer.append({
                        "sender": "Notificador",
                        "body": f"❌ {err_msg}"
                    })

    async def setup(self):
        print("[Notificador] 🟢 Listo y esperando alertas...")
        common.log_buffer.append({
            "sender": "Notificador",
            "body": "🟢 Agente Iniciado."
        })
        b = self.RecvMsgBehaviour()
        self.add_behaviour(b)