import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import common # Opcional, si quieres que escriba logs al sistema

class CoordinatorAgent(Agent):
    class ListenAndLogBehaviour(CyclicBehaviour):
        async def run(self):
            print("[Coordinador] Esperando reportes...")
            msg = await self.receive(timeout=10)
            
            if msg:
                # 1. Procesar el mensaje recibido
                contenido = f"[{time.strftime('%H:%M:%S')}] {msg.sender} reportó: {msg.body}"
                
                # 2. Actuar como "Caja Negra" del sistema (Persistencia)
                # Guardamos todo lo que pasa en un archivo de auditoría
                with open("historial_sistema.log", "a", encoding="utf-8") as f:
                    f.write(contenido + "\n")
                
                print(f"[Coordinador] 📝 Evento registrado: {msg.sender}")

                # 3. (Opcional) Podría inyectar datos globales si fuera necesario
                # common.last_log = contenido

    async def setup(self):
        print("[Coordinador] Agente de Coordinación y Auditoría INICIADO.")
        b = self.ListenAndLogBehaviour()
        self.add_behaviour(b)