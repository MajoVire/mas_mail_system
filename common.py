# common.py
import collections

# Lista de logs (Bitácora)
system_logs = collections.deque(maxlen=200)

# --- TRUCO CLAVE ---
# Hacemos que log_buffer sea un "alias" de system_logs.
# Así, no importa si el agente usa uno u otro, todo va al mismo sitio.
log_buffer = system_logs 

# Variables globales
current_disk_usage = 0.0
cleaning_requested = False
email_outbox = []