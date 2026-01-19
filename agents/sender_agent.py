import time
import smtplib
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message 
import common
import config
import utils 

class SenderAgent(Agent):
    def set_notification_agent(self, notification_jid):
        self.notification_jid = notification_jid

    class SendMailBehaviour(PeriodicBehaviour):
        async def on_start(self):
            print("[Sender] 📤 Agente de Envíos iniciado.")
            agentes_dir = os.path.dirname(os.path.abspath(__file__))
            proyecto_dir = os.path.dirname(agentes_dir)
            self.storage_folder = os.path.join(proyecto_dir, "almacenamiento_servidor")
            self.history_file = os.path.join(self.storage_folder, "historial_enviados.csv")
            if not os.path.exists(self.storage_folder): os.makedirs(self.storage_folder)

        def save_to_history(self, recipient, subject):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                clean_subj = str(subject).replace("|", "-").replace("\n", " ")
                linea = f"{now}|{recipient}|{clean_subj}\n"
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(linea)
            except Exception as e:
                print(f"[Sender] ❌ Error historial: {e}")

        async def run(self):
            if common.email_outbox:
                # 1. Sacamos el paquete
                email_data = common.email_outbox.pop(0)
                
                # Detectar simulación
                es_simulacion = 'timestamp_in' in email_data
                t_salida = time.time()

                if es_simulacion:
                    ts_in = email_data['timestamp_in']
                    latencia = t_salida - ts_in
                    common.metrics_results["latencies"].append(latencia)
                    common.metrics_results["total_processed"] += 1

                # Compatibilidad de llaves (Soporta 'to' y 'destinatario')
                destinatario = email_data.get('to') or email_data.get('destinatario')
                asunto = email_data.get('subj') or email_data.get('asunto')
                
                # Obtener cuerpo
                cuerpo_mensaje = email_data.get('body') or email_data.get('cuerpo')
                if not cuerpo_mensaje:
                    cuerpo_mensaje = "Mensaje automático del sistema MAS (Sin contenido específico)."

                try:
                    # 2. ENVÍO REAL CON CONTENIDO DINÁMICO
                    msg = MIMEMultipart()
                    msg['From'] = config.EMAIL_USER
                    msg['To'] = destinatario
                    msg['Subject'] = asunto
                    msg.attach(MIMEText(cuerpo_mensaje, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(config.EMAIL_USER, config.EMAIL_PASS)
                    server.sendmail(config.EMAIL_USER, destinatario, msg.as_string())
                    server.quit()

                    print(f"[Sender] ✅ Enviado a {destinatario}")
                    
                    # Generar carga de disco (10MB) - LÓGICA CONSERVADA
                    exito, nombre = utils.generar_carga_disco(self.storage_folder, "sent_mail")
                    if exito: print(f"[Sender] 💾 Log generado: {nombre}")

                    self.save_to_history(destinatario, asunto)
                    
                    log_msg = f"Correo enviado a {destinatario}"
                    
                    common.log_buffer.append({
                        "sender": "SenderAgent",
                        "body": log_msg
                    })

                    # Notificación SMS (Notificador) - LÓGICA CONSERVADA
                    if hasattr(self.agent, 'notification_jid'):
                        msg_sms = Message(to=self.agent.notification_jid)
                        msg_sms.set_metadata("performative", "inform")
                        msg_sms.body = log_msg
                        await self.send(msg_sms)

                    # --- [NUEVO] REPORTE AL AUDITOR (COORDINADOR) ---
                    try:
                        if hasattr(config, 'COORDINATOR_USER'):
                            msg_audit = Message(to=config.COORDINATOR_USER)
                            msg_audit.set_metadata("performative", "inform")
                            msg_audit.body = f"Transacción SMTP exitosa: {destinatario}"
                            await self.send(msg_audit)
                            # print(f"[Sender] ➔ Reportado al Auditor") 
                    except Exception as e:
                        # Si falla el auditor, no detenemos el agente
                        print(f"[Sender] ⚠️ No se pudo reportar al auditor: {e}")
                    # ------------------------------------------------

                    # 3. CÁLCULO DE MÉTRICAS (SOLO SI ES SIMULACIÓN) - LÓGICA CONSERVADA
                    if es_simulacion and not common.email_outbox and common.metrics_results["total_processed"] > 0:
                         start_time = common.metrics_results.get("batch_start_time")
                         if start_time is not None:
                             t_final = time.time()
                             t_total = t_final - start_time
                             if t_total == 0: t_total = 0.001 
                             cantidad = common.metrics_results["total_processed"]
                             throughput = (cantidad / t_total) * 60 
                             if common.metrics_results["latencies"]:
                                 avg_lat = sum(common.metrics_results["latencies"]) / len(common.metrics_results["latencies"])
                             else: avg_lat = 0.0
                             common.metrics_results["last_throughput"] = throughput
                             common.metrics_results["avg_latency"] = avg_lat
                             common.metrics_results["is_compliant"] = (throughput >= 0.83)
                             common.log_buffer.append({
                                 "sender": "Analista",
                                 "body": f"📊 Lote finalizado. Throughput: {throughput:.2f} msj/min."
                             })

                except Exception as e:
                    error_msg = f"❌ Error SMTP: {e}"
                    print(f"[Sender] {error_msg}")
                    common.log_buffer.append({"sender": "SenderAgent", "body": error_msg})

    async def setup(self):
        print("[Sender] 🟢 Agente de Salida ONLINE.")
        common.log_buffer.append({"sender": "SenderAgent", "body": "🟢 Agente Iniciado."})
        
        # --- [NUEVO] Mensaje de inicio al Auditor ---
        try:
            msg_boot = Message(to=config.COORDINATOR_USER)
            msg_boot.set_metadata("performative", "inform")
            msg_boot.body = "🟢 Agente Sender SMTP Iniciado."
            await self.send(msg_boot)
        except:
            pass
        # -------------------------------------------

        b = self.SendMailBehaviour(period=2)
        self.add_behaviour(b)