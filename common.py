# common.py
import collections

# --- 1. BITÁCORA VISUAL (LOGS) ---
# Usamos deque con límite 200 para que la web muestre el historial reciente
system_logs = collections.deque(maxlen=200)
log_buffer = system_logs  # Alias para compatibilidad

# --- 2. VARIABLES DE ESTADO ---
current_disk_usage = 0.0
cleaning_requested = False
email_outbox = []

# --- 3. MÉTRICAS DE ESCALABILIDAD (NUEVO) ---
metrics_results = {
    "last_throughput": 0.0,
    "avg_latency": 0.0,
    "total_processed": 0,
    "is_compliant": False,
    "batch_start_time": None,
    "latencies": []
}