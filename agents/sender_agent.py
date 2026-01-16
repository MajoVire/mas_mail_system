import time
import smtplib
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import common
import config

class SenderAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class SendMailBehaviour(PeriodicBehaviour):
        async def on_start(self):
            print("[Sender] 📤 Agente de Envíos iniciado.")
            
            # CONFIGURACIÓN RUTA HISTORIAL (Dinámica)
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.storage_folder = os.path.join(proyecto_dir, "almacenamiento_servidor")
            self.history_file = os.path.join(self.storage_folder, "historial_enviados.csv")
            
            if not os.path.exists(self.storage_folder):
                os.makedirs(self.storage_folder)

        def save_to_history(self, recipient, subject):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                clean_subj = str(subject).replace("|", "-").replace("\n", " ")
                # Formato: FECHA | DESTINATARIO | ASUNTO
                linea = f"{now}|{recipient}|{clean_subj}\n"
                
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(linea)
            except Exception as e:
                print(f"[Sender] ❌ Error guardando historial: {e}")

        async def run(self):
            # Revisamos si hay correos pendientes en la bandeja de salida compartida
            if common.email_outbox:
                print(f"[Sender] 📬 Procesando {len(common.email_outbox)} correos pendientes...")
                
                # Tomamos uno y lo sacamos de la lista (pop)
                email_data = common.email_outbox.pop(0)
                destinatario = email_data['to']
                asunto = email_data['subj']
                cuerpo = "Este es un mensaje enviado automáticamente por el Agente Sender del Sistema Multiagente."

                try:
                    # 1. CONEXIÓN SMTP (GMAIL)
                    msg = MIMEMultipart()
                    msg['From'] = config.EMAIL_USER
                    msg['To'] = destinatario
                    msg['Subject'] = asunto
                    msg.attach(MIMEText(cuerpo, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(config.EMAIL_USER, config.EMAIL_PASS)
                    text = msg.as_string()
                    server.sendmail(config.EMAIL_USER, destinatario, text)
                    server.quit()

                    print(f"[Sender] ✅ Correo enviado a {destinatario}")

                    # 2. GUARDAR EN HISTORIAL
                    self.save_to_history(destinatario, asunto)

                    # 3. ACTUALIZAR BITÁCORA WEB
                    if hasattr(common, 'log_buffer'):
                        common.log_buffer.append({
                            "sender": "SenderAgent",
                            "body": f"Correo enviado exitosamente a {destinatario}"
                        })

                except Exception as e:
                    print(f"[Sender] ❌ Error SMTP: {e}")
                    # Si falla, podríamos devolverlo a la cola, pero por ahora solo logueamos
                    if hasattr(common, 'log_buffer'):
                        common.log_buffer.append({
                            "sender": "SenderAgent",
                            "body": f"FALLO envío a {destinatario}: {e}"
                        })

    async def setup(self):
        print("[Sender] 🟢 Agente de Salida ONLINE.")
        # Revisa la cola cada 2 segundos
        b = self.SendMailBehaviour(period=2)
        self.add_behaviour(b)