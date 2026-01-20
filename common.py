import collections

# --- 1. BITÁCORA VISUAL (LOGS) ---
system_logs = collections.deque(maxlen=200)
log_buffer = system_logs

# --- 2. VARIABLES DE ESTADO ---
current_disk_usage = 0.0
cleaning_requested = False
email_outbox = []

# --- 3. MÉTRICAS ESCALABILIDAD ---
metrics_results = {
    "last_throughput": 0.0,
    "avg_latency": 0.0,
    "total_processed": 0,
    "is_compliant": False,
    "batch_start_time": None,
    "latencies": [],
    "ui_response_time": 0.0 
}

# --- 4. MÉTRICAS HCI ---
# Visibilidad
critical_event_timestamp = None 

# Recuperación de Errores (NUEVO)
hci_total_incidents = 0       # Cuántas veces llegamos al 100%
hci_successful_recoveries = 0 # Cuántas veces bajamos del 100% automáticamente