# common.py
# Este archivo actúa como una "Base de Datos en Memoria" simple
# para que los agentes escriban y la web lea.

import collections

# AUMENTAMOS el historial a 100 o 200 para que la paginación tenga sentido
system_logs = collections.deque(maxlen=200) 
current_disk_usage = 0.0

cleaning_requested = False
email_outbox = []