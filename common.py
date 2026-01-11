# common.py
# Este archivo actúa como una "Base de Datos en Memoria" simple
# para que los agentes escriban y la web lea.

import collections

system_logs = collections.deque(maxlen=20)
current_disk_usage = 0.0

# NUEVO: Órdenes desde la Web hacia los Agentes
cleaning_requested = False   # Bandera para limpiar disco
email_outbox = []            # Lista de espera para correos manuales