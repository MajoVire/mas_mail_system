import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import common  # Importante para conectar con el Dashboard Web
import common  # Necesario para escribir en la Bitácora Web

class CoordinatorAgent(Agent):
    class AuditBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("[Auditor] 👀 Escucha de auditoría activada.")

    class AuditBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("[Auditor] 👀 Escucha de auditoría activada.")

        async def run(self):
            # Escucha mensajes sin bloquear indefinidamente
            msg = await self.receive(timeout=1) 
            # Escucha mensajes sin bloquear indefinidamente (timeout 1s)
            msg = await self.receive(timeout=1) 
            
            if msg:
                # 1. Identificar remitente
                sender = str(msg.sender).split("@")[0]
                body = msg.body
                
                # 2. Salida A: CONSOLA (Debug)
                print(f"[{sender.upper()}] ➔ [AUDITOR]: {body}")

                # 3. Salida B: DASHBOARD WEB (Visualización en tiempo real)
                # Inyectamos el reporte en la memoria compartida 'log_buffer'
                log_entry = {
                    "sender": "Auditor",
                    "body": f"Reporte de {sender}: {body}"
                }
                if hasattr(common, 'log_buffer'):
                    common.log_buffer.append(log_entry)
                
                # 4. Salida C: ARCHIVO FÍSICO (Persistencia)
                try:
                    with open("historial_sistema.log", "a", encoding="utf-8") as f:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"[{timestamp}] {sender}: {body}\n")
                except Exception as e:
                    print(f"Error escribiendo log físico: {e}")
                # 1. Decodificar quién envía
                sender = str(msg.sender).split("@")[0]
                body = msg.body
                
                # 2. Imprimir en CONSOLA (Para que tú lo veas al ejecutar)
                print(f"[{sender.upper()}] ➔ [AUDITOR]: {body}")

                # 3. Guardar en BITÁCORA WEB (Para el Dashboard)
                # Esto hace que aparezca en la página http://localhost:5000
                log_entry = {
                    "sender": "Auditor",
                    "body": f"Reporte de {sender}"
                }
                if hasattr(common, 'log_buffer'):
                    common.log_buffer.append(log_entry)
                
                # 4. Guardar en ARCHIVO DE TEXTO (Persistencia física)
                try:
                    with open("historial_sistema.log", "a", encoding="utf-8") as f:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"[{timestamp}] {sender}: {body}\n")
                except Exception as e:
                    print(f"Error escribiendo archivo log: {e}")

    async def setup(self):
        print("--- [Auditor] Agente INICIADO y listo para centralizar reportes ---")
        
        # Aviso inicial en la web
        if hasattr(common, 'log_buffer'):
            common.log_buffer.append({
                "sender": "Auditor",
                "body": "🟢 Sistema de Auditoría Centralizada ACTIVO."
            })
            
        b = self.AuditBehaviour()
        print("--- [Auditor] Agente INICIADO y listo para recibir reportes ---")
        
        # Mensaje inicial en la web para confirmar que está vivo
        if hasattr(common, 'log_buffer'):
            common.log_buffer.append({
                "sender": "Auditor",
                "body": "🟢 Agente Iniciado."
            })
            
        b = self.AuditBehaviour()
        self.add_behaviour(b)