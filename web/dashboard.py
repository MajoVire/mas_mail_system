from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import common
import math
import os
import simulation 
import time
import utils 

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Multiagente - Panel de Control</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #f0f2f5; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .full-height-card { height: 100%; display: flex; flex-direction: column; min-height: 600px; }
        .history-card { min-height: 600px; display: flex; flex-direction: column; padding: 0 !important; }
        .table-flex-area { flex-grow: 1; overflow-y: auto; }
        .card-header-custom { padding: 1.5rem; border-bottom: 1px solid #dee2e6; background-color: #fff; border-radius: 12px 12px 0 0; }
        .card-footer-custom { padding: 1rem; border-top: 1px solid #dee2e6; background-color: #fff; border-radius: 0 0 12px 12px; margin-top: auto; }
        .msg-cell { word-break: break-word; white-space: normal; }
        .nav-pills .nav-link.active { background-color: #0d6efd; }
        
        /* ESTILOS DE MÉTRICAS */
        .metric-section-title { color: #6c757d; font-weight: bold; margin-bottom: 15px; margin-top: 10px; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; }
        .metric-card { text-align: center; padding: 25px; height: 100%; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-value { font-size: 2.2rem; font-weight: bold; color: #0d6efd; margin-bottom: 5px; }
        .metric-label { color: #495057; font-weight: 600; }
        .metric-unit { color: #adb5bd; font-size: 0.9rem; }
        
        /* Colores específicos para HCI */
        .hci-value { color: #6610f2; }      /* Morado: Tiempos/Latencia */
        .hci-recovery { color: #198754; }   /* Verde: Recuperación */
        .hci-density { color: #fd7e14; }    /* Naranja: Carga Cognitiva */

        .badge-sender { font-size: 0.9em; background-color: #e7f1ff; color: #0d6efd; border: 1px solid #0d6efd; }
        .badge-sent { font-size: 0.9em; background-color: #d1e7dd; color: #0f5132; border: 1px solid #0f5132; }
        .page-info { font-weight: bold; margin: 0 15px; color: #6c757d; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>🤖 Sistema Multiagente</h1>
            <ul class="nav nav-pills" id="pills-tab" role="tablist">
                <li class="nav-item"><a class="nav-link active" data-bs-toggle="pill" href="#pills-dash">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="pill" href="#pills-metrics">📊 Métricas</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="pill" href="#pills-history" onclick="loadHistory('received')">📥 Recibidos</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="pill" href="#pills-sent" onclick="loadHistory('sent')">📤 Enviados</a></li>
            </ul>
        </div>
        
        <div class="tab-content">
            <div class="tab-pane fade show active" id="pills-dash">
                <div class="row align-items-stretch">
                    <div class="col-md-5 d-flex flex-column">
                        
                        <div class="card p-4">
                            <h4>💾 Monitor de Disco</h4>
                            <h2 class="text-center my-3" id="disk-text">0%</h2>
                            <div class="progress mb-3" style="height: 25px;"><div id="disk-bar" class="progress-bar bg-success" style="width: 0%"></div></div>
                            <div id="clean-btn-container" style="display: none;">
                                <form action="/clean_disk" method="post"><button class="btn btn-warning w-100 fw-bold">🧹 Liberar Espacio</button></form>
                            </div>
                            <div id="system-status-msg" class="text-center mt-2">
                                <small class="text-muted">✅ Sistema Optimizado</small>
                            </div>
                        </div>

                        <div class="card p-3 border-danger mb-3" style="background-color: #fff5f5;">
                            <h4 class="text-danger">🔥 Prueba de Estrés (HCI)</h4>
                            <p class="small text-muted mb-2">Inyecta un archivo masivo para forzar el error de disco al 100%.</p>
                            <form action="/trigger_chaos" method="post">
                                <button type="submit" class="btn btn-danger w-100 fw-bold">💥 PROVOCAR FALLO CRÍTICO</button>
                            </form>
                        </div>

                        <div class="card p-3 border-primary mb-3">
                             <h4 class="text-primary">🚀 Simulación Carga</h4>
                            <form action="/simulate" method="post"><button type="submit" class="btn btn-outline-primary w-100 fw-bold">Lanzar 10 Usuarios</button></form>
                        </div>

                        <div class="card p-3 mb-0">
                            <h4>✉️ Redactar Nuevo Correo</h4>
                            <form action="/send_email" method="post">
                                <div class="mb-2"><input type="email" name="to" class="form-control" placeholder="Para" required></div>
                                <div class="mb-2"><input type="text" name="subject" class="form-control" placeholder="Asunto" required></div>
                                <div class="mb-2"><textarea name="body" class="form-control" rows="3" placeholder="Mensaje..."></textarea></div>
                                <button type="submit" class="btn btn-primary w-100">Enviar Orden al Agente</button>
                            </form>
                        </div>

                    </div>

                    <div class="col-md-7">
                        <div class="card full-height-card p-0">
                            <div class="card-header-custom"><h4 class="m-0">📜 Bitácora del Sistema</h4></div>
                            <div class="table-flex-area">
                                <table class="table table-striped mb-0">
                                    <thead class="table-dark sticky-top"><tr><th style="width: 20%;">Agente</th><th>Mensaje</th></tr></thead>
                                    <tbody id="log-table-body"></tbody>
                                </table>
                            </div>
                            <div class="card-footer-custom d-flex justify-content-between align-items-center">
                                <button class="btn btn-sm btn-outline-secondary" onclick="logsPaginator.prevPage()">◀ Anterior</button>
                                <span class="page-info" id="info-logs">Cargando...</span>
                                <button class="btn btn-sm btn-outline-secondary" onclick="logsPaginator.nextPage()">Siguiente ▶</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-metrics">
                <h5 class="metric-section-title"><i class="bi bi-graph-up"></i> Rendimiento y Escalabilidad</h5>
                <div class="row mb-4">
                    <div class="col-md-4"><div class="card metric-card"><div class="metric-label">Throughput</div><div class="metric-value" id="m-throughput">0.0</div><div class="metric-unit">msj / min</div></div></div>
                    <div class="col-md-4"><div class="card metric-card"><div class="metric-label">Latencia Proc.</div><div class="metric-value" id="m-latency">0.0</div><div class="metric-unit">segundos</div></div></div>
                    <div class="col-md-4"><div class="card metric-card"><div class="metric-label">Requisito</div><div class="mt-3" id="m-status"><span class="badge bg-secondary">--</span></div><div class="metric-unit mt-2">Meta: > 50 msj/h</div></div></div>
                </div>

                <h5 class="metric-section-title"><i class="bi bi-person-workspace"></i> Usabilidad y HCI</h5>
                <div class="row">
                    <div class="col-md-3"><div class="card metric-card"><div class="metric-label">Respuesta UI</div><div class="metric-value hci-value" id="m-ui-response">0.00</div><div class="metric-unit">ms</div><small class="text-muted mt-2">Target: &lt; 100ms</small></div></div>
                    <div class="col-md-3"><div class="card metric-card"><div class="metric-label">Visibilidad</div><div class="metric-value hci-value" id="m-visibility">0.000</div><div class="metric-unit">s</div><div id="m-visibility-badge" class="mt-2"><span class="badge bg-success">OK</span></div></div></div>
                    <div class="col-md-3"><div class="card metric-card"><div class="metric-label">Recuperación</div><div class="metric-value hci-recovery" id="m-recovery-rate">100%</div><div class="metric-unit">Tasa de Éxito</div><div id="m-recovery-stats" class="mt-2 text-muted small">0 eventos</div></div></div>
                    
                    <div class="col-md-3">
                        <div class="card metric-card">
                            <div class="metric-label">Densidad Visual</div>
                            <div class="metric-value hci-density" id="m-density-val">0</div>
                            <div class="metric-unit">Elementos en Pantalla</div>
                            <div id="m-density-badge" class="mt-2"><span class="badge bg-secondary">Calculando...</span></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-history">
                 <div class="card history-card"><div class="card-header-custom"><h4>📥 Recibidos</h4></div><div class="table-flex-area"><table class="table table-hover mb-0"><thead class="bg-light sticky-top"><tr><th>Fecha</th><th>Remitente</th><th>Asunto</th></tr></thead><tbody id="received-table-body"></tbody></table></div><div class="card-footer-custom d-flex justify-content-center gap-3"><button class="btn btn-outline-primary btn-sm" onclick="recvPaginator.prevPage()">◀</button><span id="info-recv" class="page-info">1</span><button class="btn btn-outline-primary btn-sm" onclick="recvPaginator.nextPage()">▶</button></div></div>
            </div>
            <div class="tab-pane fade" id="pills-sent">
                 <div class="card history-card"><div class="card-header-custom"><h4>📤 Enviados</h4></div><div class="table-flex-area"><table class="table table-hover mb-0"><thead class="bg-light sticky-top"><tr><th>Fecha</th><th>Destinatario</th><th>Asunto</th></tr></thead><tbody id="sent-table-body"></tbody></table></div><div class="card-footer-custom d-flex justify-content-center gap-3"><button class="btn btn-outline-primary btn-sm" onclick="sentPaginator.prevPage()">◀</button><span id="info-sent" class="page-info">1</span><button class="btn btn-outline-primary btn-sm" onclick="sentPaginator.nextPage()">▶</button></div></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        class TablePaginator {
            constructor(tableBodyId, infoId, renderRowCallback) {
                this.tableBody = document.getElementById(tableBodyId);
                this.infoLabel = document.getElementById(infoId);
                this.renderRow = renderRowCallback;
                this.limit = 5; 
                this.currentPage = 1;
                this.data = [];
            }
            setData(newData) { this.data = newData; this.render(); }
            nextPage() { if (this.currentPage < Math.ceil(this.data.length / this.limit)) { this.currentPage++; this.render(); } }
            prevPage() { if (this.currentPage > 1) { this.currentPage--; this.render(); } }
            render() {
                if (!this.data || this.data.length === 0) {
                    this.tableBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted p-5">Sin registros.</td></tr>';
                    this.infoLabel.innerText = "0/0";
                    return;
                }
                const maxPage = Math.ceil(this.data.length / this.limit);
                if (this.currentPage > maxPage) this.currentPage = maxPage;
                const pageData = this.data.slice((this.currentPage - 1) * this.limit, this.currentPage * this.limit);
                this.tableBody.innerHTML = '';
                pageData.forEach(item => { this.tableBody.innerHTML += this.renderRow(item); });
                this.infoLabel.innerText = `Pág ${this.currentPage} de ${maxPage}`;
            }
        }
        const renderLog = (log) => `<tr><td><span class="badge bg-secondary">${log.sender||"Sys"}</span></td><td class="msg-cell">${log.body||""}</td></tr>`;
        const renderReceived = (item) => `<tr><td><small>${item.date}</small></td><td><span class="badge-sender px-2 py-1 rounded">${item.person}</span></td><td class="fw-bold msg-cell">${item.subject}</td></tr>`;
        const renderSent = (item) => `<tr><td><small>${item.date}</small></td><td><span class="badge-sent px-2 py-1 rounded">${item.person}</span></td><td class="fw-bold msg-cell">${item.subject}</td></tr>`;
        const logsPaginator = new TablePaginator('log-table-body', 'info-logs', renderLog);
        const recvPaginator = new TablePaginator('received-table-body', 'info-recv', renderReceived);
        const sentPaginator = new TablePaginator('sent-table-body', 'info-sent', renderSent);

        let currentAlertEventId = null; 

        // --- NUEVA FUNCIÓN: CÁLCULO DE CARGA COGNITIVA (HCI) ---
        function calculateCognitiveLoad() {
            // Medimos la carga del PANEL PRINCIPAL (#pills-dash), que es la vista operativa
            const dashContainer = document.getElementById('pills-dash');
            if (!dashContainer) return;

            // 1. Estructura y Contenedores (Tarjetas)
            const cards = dashContainer.querySelectorAll('.card').length;
            
            // 2. Elementos de Interacción (Botones y Campos)
            const inputs = dashContainer.querySelectorAll('.btn, .form-control').length;
            
            // 3. Elementos de Datos (Filas de tabla visibles actualmente)
            const rows = dashContainer.querySelectorAll('tbody tr').length;
            
            // 4. Elementos de Atención Visual (Badges/Etiquetas de color)
            const badges = dashContainer.querySelectorAll('.badge').length;
            
            // 5. Alertas visuales (Barras)
            const alerts = dashContainer.querySelectorAll('.progress, .alert').length;

            // FÓRMULA DE DENSIDAD
            const totalLoad = cards + inputs + rows + badges + alerts;
            
            // Actualizar UI
            document.getElementById('m-density-val').innerText = totalLoad;
            
            const densityBadge = document.getElementById('m-density-badge');
            if (totalLoad <= 20) {
                densityBadge.innerHTML = '<span class="badge bg-success">🟢 Óptimo (Minimalista)</span>';
            } else if (totalLoad <= 40) {
                densityBadge.innerHTML = '<span class="badge bg-warning text-dark">🟡 Moderado</span>';
            } else {
                densityBadge.innerHTML = '<span class="badge bg-danger">🔴 Sobrecarga</span>';
            }
        }

        function updateDashboard() {
            fetch('/api/data?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    const usage = data.disk_usage;
                    document.getElementById('disk-text').innerText = usage + '%';
                    const bar = document.getElementById('disk-bar');
                    bar.style.width = usage + '%';
                    const statusMsgDiv = document.getElementById('system-status-msg');
                    
                    if (usage > 90) {
                        bar.className = 'progress-bar bg-danger';
                        document.getElementById('clean-btn-container').style.display = 'block';
                        statusMsgDiv.innerHTML = `<span class="text-danger fw-bold">⚠️ ALERTA CRÍTICA</span>`;
                    } else {
                        bar.className = 'progress-bar bg-success';
                        document.getElementById('clean-btn-container').style.display = 'none';
                        statusMsgDiv.innerHTML = '<small class="text-muted">✅ Sistema Optimizado</small>';
                    }

                    document.getElementById('m-throughput').innerText = data.metrics.last_throughput.toFixed(2);
                    document.getElementById('m-latency').innerText = data.metrics.avg_latency.toFixed(2);
                    const statusDiv = document.getElementById('m-status');
                    if (data.metrics.total_processed > 0) {
                        statusDiv.innerHTML = data.metrics.is_compliant ? '<span class="badge bg-success">CUMPLIDO</span>' : '<span class="badge bg-warning text-dark">BAJO</span>';
                    }

                    document.getElementById('m-ui-response').innerText = data.metrics.ui_response_time.toFixed(2);

                    if (data.event_ts !== null) {
                        if (currentAlertEventId !== data.event_ts) {
                            let now = new Date().getTime() / 1000;
                            let latency = (now - data.event_ts).toFixed(3);
                            document.getElementById('m-visibility').innerText = latency;
                            document.getElementById('m-visibility-badge').innerHTML = '<span class="badge bg-danger">⚠️ Alerta Visualizada</span>';
                            console.warn(`[HCI] Latencia: ${latency}s`);
                            currentAlertEventId = data.event_ts;
                        } 
                    } else {
                        currentAlertEventId = null;
                        document.getElementById('m-visibility').innerText = "0.000";
                        document.getElementById('m-visibility-badge').innerHTML = '<span class="badge bg-success">OK</span>';
                    }

                    let incidents = data.hci_metrics.incidents;
                    let recoveries = data.hci_metrics.recoveries;
                    let recoveryRate = 100;
                    if (incidents > 0) recoveryRate = (recoveries / incidents) * 100;
                    document.getElementById('m-recovery-rate').innerText = recoveryRate.toFixed(0) + '%';
                    document.getElementById('m-recovery-stats').innerText = `${recoveries} curados / ${incidents} incidentes`;

                    logsPaginator.setData(data.logs);

                    // --- LLAMADA A LA MÉTRICA DE DENSIDAD ---
                    // Se llama aquí porque logsPaginator acaba de renderizar las filas
                    calculateCognitiveLoad();
                });
        }
        function loadHistory(type) {
            const endpoint = (type === 'sent') ? '/api/history_sent' : '/api/history_received';
            fetch(endpoint + '?t=' + new Date().getTime()).then(r => r.json()).then(d => { (type === 'received') ? recvPaginator.setData(d) : sentPaginator.setData(d); });
        }
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

# --- RUTAS API Y CONTROLADORES ---
@app.route("/")
def index(): return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    logs = list(common.system_logs); logs.reverse()
    return jsonify({ 
        'disk_usage': common.current_disk_usage, 
        'logs': logs, 
        'metrics': common.metrics_results,
        'event_ts': common.critical_event_timestamp,
        'hci_metrics': { 'incidents': common.hci_total_incidents, 'recoveries': common.hci_successful_recoveries }
    })

@app.route("/api/history_received")
def api_history_received(): return read_csv_history("historial_correos.csv")

@app.route("/api/history_sent")
def api_history_sent(): return read_csv_history("historial_enviados.csv")

def read_csv_history(filename):
    history_data = []
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "almacenamiento_servidor", filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    parts = line.strip().split("|")
                    if len(parts) >= 3: history_data.append({ "date": parts[0], "person": parts[1], "subject": parts[2] })
    except Exception: pass
    return jsonify(history_data)

@app.route("/clean_disk", methods=['POST'])
def clean_disk():
    common.cleaning_requested = True
    return redirect(url_for('index'))

@app.route("/send_email", methods=['POST'])
def send_email():
    if request.form.get('to') and request.form.get('subject'):
        common.email_outbox.append({'to': request.form.get('to'), 'subj': request.form.get('subject'), 'body': request.form.get('body')})
    return redirect(url_for('index'))

@app.route("/simulate", methods=['POST'])
def simulate():
    start_ui = time.time()
    simulation.run_mass_simulation()
    end_ui = time.time()
    ui_latency_ms = (end_ui - start_ui) * 1000
    common.metrics_results["ui_response_time"] = ui_latency_ms
    print(f"[HCI Metrica] UI liberada en {ui_latency_ms:.2f} ms")
    return redirect(url_for('index'))

@app.route("/trigger_chaos", methods=['POST'])
def trigger_chaos():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage = os.path.join(base_dir, "almacenamiento_servidor")
    limit = 500 * 1024 * 1024 
    exito, nombre, size = utils.generar_archivo_caos(storage, limit)
    if exito: print(f"[Chaos] 💣 Caos generado: {nombre}")
    else: print(f"[Chaos] ❌ Error o caos activo: {nombre}")
    return redirect(url_for('index'))

def start_web_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_web_server()