from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from twilio.rest import Client
import common
import config

class NotificationAgent(Agent):
    # --- TUS CREDENCIALES DE TWILIO ---
    TWILIO_SID = config.TWILIO_SID          # <--- Pega aquí tu Account SID
    TWILIO_TOKEN = config.TWILIO_TOKEN          # <--- Pega aquí tu Auth Token
    TWILIO_FROM = config.TWILIO_FROM         # <--- Pega aquí el número que te dio Twilio
    
    # --- TU CELULAR REAL (Donde recibirás el SMS) ---
    # Nota: En cuentas de prueba (Trial), SOLO puedes enviar SMS 
    # al número con el que te registraste en Twilio.
    MY_CELLPHONE = config.MY_CELLPHONE # <--- Tu número (Ej: +593998877665)
    # ------------------------------------------------

    class RecvMsgBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            
            if msg:
                # 1. Registro en Consola y Web
                print(f"[🔔 Notificador] Mensaje de: {msg.sender}")
                log_entry = {
                    "sender": str(msg.sender).split("@")[0],
                    "body": msg.body,
                    "time": "Ahora"
                }
                common.system_logs.appendleft(log_entry)

                # 2. ENVIAR SMS REAL A TU CELULAR
                try:
                    # Verificamos que no hayas dejado los datos vacíos
                    if "AC" in self.agent.TWILIO_SID: 
                        client = Client(self.agent.TWILIO_SID, self.agent.TWILIO_TOKEN)
                        
                        message = client.messages.create(
                            body=f"🤖 {str(msg.sender).split('@')[0]}: {msg.body}",
                            from_=self.agent.TWILIO_FROM,
                            to=self.agent.MY_CELLPHONE
                        )
                        print(f"[Twilio] ✅ SMS enviado exitosamente! SID: {message.sid}")
                    else:
                        print("[Twilio] ⚠️ Faltan credenciales, modo simulación.")
                except Exception as e:
                    print(f"[Twilio] ❌ Error enviando SMS: {e}")

    async def setup(self):
        print("[Notificador] Servicio SMS activo y conectado a Twilio.")
        b = self.RecvMsgBehaviour()
        self.add_behaviour(b)