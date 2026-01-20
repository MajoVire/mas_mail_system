import time
import os
import imaplib
import email
import re
import datetime
from email.header import decode_header
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common
import config 
import utils 

class ReceptorAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class CheckEmailBehaviour(PeriodicBehaviour):
        async def on_start(self):
            print("[Receptor] 📧 Vigilancia IMAP iniciada.")
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.storage_folder = os.path.join(proyecto_dir, "almacenamiento_servidor")
            self.history_file = os.path.join(self.storage_folder, "historial_correos.csv")
            if not os.path.exists(self.storage_folder):
                os.makedirs(self.storage_folder)

        def save_to_history(self, sender, subject):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                clean_subj = str(subject).replace("|", "-").replace("\n", " ")
                linea = f"{now}|{sender}|{clean_subj}\n"
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(linea)
            except Exception as e:
                print(f"[Receptor] ❌ Error historial: {e}")

        async def run(self):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(config.EMAIL_USER, config.EMAIL_PASS)
                mail.select("inbox")

                status, messages = mail.search(None, "(UNSEEN)")
                email_ids = messages[0].split()

                if not email_ids:
                    mail.logout()
                    return

                print(f"[Receptor] 📥 {len(email_ids)} correos nuevos detectados.")

                for e_id in email_ids:
                    res, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject_raw, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject_raw, bytes):
                                subject = subject_raw.decode(encoding if encoding else "utf-8")
                            else: subject = subject_raw
                            sender = msg.get("From")
                            
                            email_regex = r'[\w\.-]+@[\w\.-]+'
                            match = re.search(email_regex, str(sender))
                            clean_sender = match.group(0) if match else "Desconocido"

                            # 1. Simulación de carga (Funcionalidad Original)
                            exito, nombre_archivo = utils.generar_carga_disco(self.storage_folder, "incoming_mail")
                            if exito: print(f"[Receptor] 💾 Archivo generado: {nombre_archivo}")

                            self.save_to_history(clean_sender, subject)

                            log_msg = f"Recibido correo de {clean_sender}: {subject}"
                            common.log_buffer.append({"sender": "ReceptorAgent", "body": log_msg})

                            # 2. Notificación SMS (Original)
                            if hasattr(self.agent, 'notification_jid'):
                                msg_spade = Message(to=self.agent.notification_jid)
                                msg_spade.set_metadata("performative", "inform")
                                msg_spade.body = log_msg
                                await self.send(msg_spade)
                            
                            # 3. [NUEVO] Reporte al Auditor
                            try:
                                if hasattr(config, 'COORDINATOR_USER'):
                                    msg_audit = Message(to=config.COORDINATOR_USER)
                                    msg_audit.set_metadata("performative", "inform")
                                    msg_audit.body = log_msg
                                    await self.send(msg_audit)
                            except: pass

                mail.close()
                mail.logout()

            except Exception as e:
                common.log_buffer.append({"sender": "ReceptorAgent", "body": f"⚠️ Error IMAP: {e}"})

    async def setup(self):
        print("[Receptor] 🟢 Agente ONLINE.")
        common.log_buffer.append({"sender": "ReceptorAgent", "body": "🟢 Vigilancia iniciada."})
        
        # Reporte inicio
        try:
            msg = Message(to=config.COORDINATOR_USER)
            msg.body = "🟢 Agente Receptor IMAP Iniciado."
            await self.send(msg)
        except: pass

        b = self.CheckEmailBehaviour(period=10)
        self.add_behaviour(b)