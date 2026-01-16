import time
import os
import imaplib
import email
import re
import datetime # <--- Nuevo
from email.header import decode_header
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import common
import config 

class ReceptorAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class CheckEmailBehaviour(PeriodicBehaviour):
        async def on_start(self):
            print("[Receptor] 📧 Iniciando vigilancia IMAP...")
            self.imap_server = "imap.gmail.com" 
            self.email_user = config.EMAIL_USER 
            self.email_pass = config.EMAIL_PASS
            
            # RUTA DINÁMICA
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.storage_folder = os.path.join(proyecto_dir, "almacenamiento_servidor")
            self.history_file = os.path.join(self.storage_folder, "historial_correos.csv") # <--- Archivo Historial
            
            if not os.path.exists(self.storage_folder):
                os.makedirs(self.storage_folder)

        # Función para guardar en el historial
        def save_to_history(self, sender, subject):
            try:
                # Obtenemos fecha bonita (Ej: 2026-01-15 10:30:00)
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Limpiamos el asunto de posibles caracteres extraños
                clean_subj = str(subject).replace("|", "-").replace("\n", " ")
                
                # Formato: FECHA | REMITENTE | ASUNTO
                linea = f"{now}|{sender}|{clean_subj}\n"
                
                # "a" significa append (agregar al final sin borrar lo anterior)
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(linea)
            except Exception as e:
                print(f"[Receptor] ❌ Error guardando historial: {e}")

        async def run(self):
            try:
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(self.email_user, self.email_pass)
                mail.select("inbox")

                status, messages = mail.search(None, "(UNSEEN)")
                email_ids = messages[0].split()

                if not email_ids:
                    mail.logout()
                    return

                print(f"[Receptor] 📥 Se encontraron {len(email_ids)} correos nuevos.")

                for e_id in email_ids:
                    res, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            subject_raw, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject_raw, bytes):
                                subject = subject_raw.decode(encoding if encoding else "utf-8")
                            else:
                                subject = subject_raw
                            
                            sender = msg.get("From")
                            
                            # Regex
                            email_regex = r'[\w\.-]+@[\w\.-]+'
                            match = re.search(email_regex, str(sender))
                            clean_sender = match.group(0) if match else "Desconocido"

                            # 1. GUARDAR 100 MB (Para el Monitor de Disco)
                            timestamp = int(time.time())
                            filename = f"email_{timestamp}.txt"
                            filepath = os.path.join(self.storage_folder, filename)
                            with open(filepath, "wb") as f:
                                f.write(b"A" * 100 * 1024 * 1024) 
                            
                            print(f"[Receptor] 💾 Guardado 50MB. Remitente: {clean_sender}")

                            # 2. GUARDAR EN HISTORIAL (NUEVO)
                            self.save_to_history(clean_sender, subject)

                            # 3. Log Web
                            log_msg = f"URGENTE: Recibido correo de {clean_sender}. Asunto: {subject}"
                            if hasattr(common, 'log_buffer'):
                                common.log_buffer.append({
                                    "sender": "receptor_majo", 
                                    "body": log_msg
                                })

                            # 4. Notificador (Plyer/Windows)
                            if hasattr(self.agent, 'notification_jid'):
                                msg = Message(to=self.agent.notification_jid)
                                msg.set_metadata("performative", "inform")
                                msg.body = f"Nuevo correo de {clean_sender}: {subject}"
                                await self.send(msg)

                mail.close()
                mail.logout()

            except Exception as e:
                print(f"[Receptor] ⚠️ Error conexión: {e}")

    async def setup(self):
        print("[Receptor] 🟢 Agente ONLINE (Con Historial).")
        b = self.CheckEmailBehaviour(period=5)
        self.add_behaviour(b)