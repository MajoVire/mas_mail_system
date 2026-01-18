from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import common
import math
import os
import simulation 
import time

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
        
        /* --- ESTILOS DE ESTRUCTURA FIJA (HCI: CONSISTENCIA) --- */
        
        /* 1. Tarjeta de Bitácora (Se adapta a la altura de la columna izquierda) */
        .full-height-card {
            height: 100%; 
            display: flex; 
            flex-direction: column; 
            min-height: 600px;
        }

        /* 2. Tarjetas de Historial (Altura mínima garantizada) */
        .history-card {
            min-height: 600px; 
            display: flex;
            flex-direction: column;
            padding: 0 !important;
        }

        /* Área flexible para la tabla (ocupa el espacio sobrante) */
        .table-flex-area {
            flex-grow: 1;
            overflow-y: auto; /* Scroll interno si es necesario */
        }

        /* Encabezados y Pies de tarjeta personalizados */
        .card-header-custom { padding: 1.5rem; border-bottom: 1px solid #dee2e6; background-color: #fff; border-radius: 12px 12px 0 0; }
        .card-footer-custom { padding: 1rem; border-top: 1px solid #dee2e6; background-color: #fff; border-radius: 0 0 12px 12px; margin-top: auto; }

        /* Estilos de Texto y Celdas */
        .msg-cell { word-break: break-word; white-space: normal; }
        .nav-pills .nav-link.active { background-color: #0d6efd; }
        .metric-card { text-align: center; padding: 20px; }
        .metric-value { font-size: 2.5rem; font-weight: bold; color: #0d6efd; }
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
                            <div id="system-ok-msg" class="text-center text-muted"><small>✅ Sistema Optimizado</small></div>
                        </div>

                        <div class="card p-3">
                            <h4>✉️ Redactar Nuevo Correo</h4>
                            <form action="/send_email" method="post">
                                <div class="mb-2"><input type="email" name="to" class="form-control" placeholder="Para" required></div>
                                <div class="mb-2"><input type="text" name="subject" class="form-control" placeholder="Asunto" required></div>
                                <div class="mb-2"><textarea name="body" class="form-control" rows="3" placeholder="Mensaje..."></textarea></div>
                                <button type="submit" class="btn btn-primary w-100">Enviar</button>
                            </form>
                        </div>

                        <div class="card p-3 border-danger mb-0">
                            <h4 class="text-danger">🔥 Simulación</h4>
                            <form action="/simulate" method="post"><button type="submit" class="btn btn-outline-danger w-100 fw-bold">🚀 Lanzar 10 Usuarios</button></form>
                        </div>
                    </div>

                    <div class="col-md-7">
                        <div class="card full-height-card p-0">
                            <div class="card-header-custom">
                                <h4 class="m-0">📜 Bitácora del Sistema</h4>
                            </div>
                            
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
                <div class="row">
                    <div class="col-md-4"><div class="card metric-card"><h5>Throughput</h5><div class="metric-value" id="m-throughput">0.0</div><p>msj / minuto</p></div></div>
                    <div class="col-md-4"><div class="card metric-card"><h5>Latencia Media</h5><div class="metric-value" id="m-latency">0.0</div><p>segundos</p></div></div>
                    <div class="col-md-4"><div class="card metric-card"><h5>Estado Requisito</h5><div class="mt-3" id="m-status"><span class="badge bg-secondary">Sin Datos</span></div></div></div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-history">
                <div class="card history-card">
                    <div class="card-header-custom">
                        <h4 class="m-0">📥 Historial de Correos Recibidos</h4>
                    </div>

                    <div class="table-flex-area">
                        <table class="table table-hover mb-0">
                            <thead class="bg-light sticky-top"><tr><th>Fecha</th><th>Remitente</th><th>Asunto</th></tr></thead>
                            <tbody id="received-table-body"></tbody>
                        </table>
                    </div>

                    <div class="card-footer-custom d-flex justify-content-center gap-3 align-items-center">
                        <button class="btn btn-outline-primary btn-sm" onclick="recvPaginator.prevPage()">◀ Anterior</button>
                        <span id="info-recv" class="page-info">Pág 1</span>
                        <button class="btn btn-outline-primary btn-sm" onclick="recvPaginator.nextPage()">Siguiente ▶</button>
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-sent">
                <div class="card history-card">
                    <div class="card-header-custom">
                        <h4 class="m-0">📤 Historial de Correos Enviados</h4>
                    </div>

                    <div class="table-flex-area">
                        <table class="table table-hover mb-0">
                            <thead class="bg-light sticky-top"><tr><th>Fecha</th><th>Destinatario</th><th>Asunto</th></tr></thead>
                            <tbody id="sent-table-body"></tbody>
                        </table>
                    </div>

                    <div class="card-footer-custom d-flex justify-content-center gap-3 align-items-center">
                        <button class="btn btn-outline-primary btn-sm" onclick="sentPaginator.prevPage()">◀ Anterior</button>
                        <span id="info-sent" class="page-info">Pág 1</span>
                        <button class="btn btn-outline-primary btn-sm" onclick="sentPaginator.nextPage()">Siguiente ▶</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // --- COMPONENTE DE PAGINACIÓN SIMPLIFICADO (FIXED 5 ROWS) ---
        class TablePaginator {
            constructor(tableBodyId, infoId, renderRowCallback) {
                this.tableBody = document.getElementById(tableBodyId);
                this.infoLabel = document.getElementById(infoId);
                this.renderRow = renderRowCallback;
                this.limit = 5; // --- LÍMITE FIJO ESTABLECIDO AQUÍ ---
                this.currentPage = 1;
                this.data = [];
            }

            setData(newData) {
                this.data = newData;
                this.render();
            }

            nextPage() {
                const maxPage = Math.ceil(this.data.length / this.limit);
                if (this.currentPage < maxPage) {
                    this.currentPage++;
                    this.render();
                }
            }

            prevPage() {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.render();
                }
            }

            render() {
                if (!this.data || this.data.length === 0) {
                    this.tableBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted p-5">Sin registros disponibles aún.</td></tr>';
                    this.infoLabel.innerText = "0/0";
                    return;
                }
                
                const maxPage = Math.ceil(this.data.length / this.limit);
                if (this.currentPage > maxPage) this.currentPage = maxPage;

                const startIndex = (this.currentPage - 1) * this.limit;
                const endIndex = startIndex + this.limit;
                const pageData = this.data.slice(startIndex, endIndex);

                this.tableBody.innerHTML = '';
                pageData.forEach(item => {
                    this.tableBody.innerHTML += this.renderRow(item);
                });

                this.infoLabel.innerText = `Pág ${this.currentPage} de ${maxPage} (${this.data.length})`;
            }
        }

        const renderLog = (log) => {
            const agente = log.sender || "Sistema";
            const mensaje = log.body || "Info";
            return `<tr><td class="align-middle"><span class="badge bg-secondary">${agente}</span></td><td class="msg-cell align-middle">${mensaje}</td></tr>`;
        };

        const renderReceived = (item) => {
            return `<tr>
                <td style="width:20%"><small>${item.date}</small></td>
                <td style="width:30%"><span class="badge-sender px-2 py-1 rounded">${item.person}</span></td>
                <td class="fw-bold msg-cell">${item.subject}</td>
            </tr>`;
        };

        const renderSent = (item) => {
            return `<tr>
                <td style="width:20%"><small>${item.date}</small></td>
                <td style="width:30%"><span class="badge-sent px-2 py-1 rounded">${item.person}</span></td>
                <td class="fw-bold msg-cell">${item.subject}</td>
            </tr>`;
        };

        const logsPaginator = new TablePaginator('log-table-body', 'info-logs', renderLog);
        const recvPaginator = new TablePaginator('received-table-body', 'info-recv', renderReceived);
        const sentPaginator = new TablePaginator('sent-table-body', 'info-sent', renderSent);

        function updateDashboard() {
            fetch('/api/data?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    const usage = data.disk_usage;
                    document.getElementById('disk-text').innerText = usage + '%';
                    const bar = document.getElementById('disk-bar');
                    bar.style.width = usage + '%';
                    
                    if (usage > 90) {
                        bar.className = 'progress-bar bg-danger';
                        document.getElementById('clean-btn-container').style.display = 'block';
                        document.getElementById('system-ok-msg').style.display = 'none';
                    } else {
                        bar.className = 'progress-bar bg-success';
                        document.getElementById('clean-btn-container').style.display = 'none';
                        document.getElementById('system-ok-msg').style.display = 'block';
                    }

                    document.getElementById('m-throughput').innerText = data.metrics.last_throughput.toFixed(2);
                    document.getElementById('m-latency').innerText = data.metrics.avg_latency.toFixed(2);
                    const statusDiv = document.getElementById('m-status');
                    if (data.metrics.total_processed > 0) {
                        statusDiv.innerHTML = data.metrics.is_compliant ? 
                            '<span class="badge bg-success">✅ REQUISITO CUMPLIDO</span>' : 
                            '<span class="badge bg-warning text-dark">⚠️ BAJO RENDIMIENTO</span>';
                    }

                    logsPaginator.setData(data.logs);
                });
        }

        function loadHistory(type) {
            const endpoint = (type === 'sent') ? '/api/history_sent' : '/api/history_received';
            fetch(endpoint + '?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    if (type === 'received') recvPaginator.setData(data);
                    else sentPaginator.setData(data);
                });
        }

        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

# --- RUTAS DE LA API (Sin cambios) ---
@app.route("/")
def index(): return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    logs = list(common.system_logs)
    logs.reverse()
    return jsonify({ 'disk_usage': common.current_disk_usage, 'logs': logs, 'metrics': common.metrics_results })

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
                    if len(parts) >= 3:
                        history_data.append({ "date": parts[0], "person": parts[1], "subject": parts[2] })
    except Exception: pass
    return jsonify(history_data)

@app.route("/clean_disk", methods=['POST'])
def clean_disk():
    common.cleaning_requested = True
    return redirect(url_for('index'))

@app.route("/send_email", methods=['POST'])
def send_email():
    destinatario = request.form.get('to')
    asunto = request.form.get('subject')
    cuerpo = request.form.get('body')
    if destinatario and asunto:
        common.email_outbox.append({'to': destinatario, 'subj': asunto, 'body': cuerpo})
    return redirect(url_for('index'))

@app.route("/simulate", methods=['POST'])
def simulate():
    start_ui = time.time()
    # Lanzamos el trabajo pesado en hilo (Background)
    simulation.run_mass_simulation()
    end_ui = time.time()
    ui_latency_ms = (end_ui - start_ui) * 1000
    # EVIDENCIA PROGRAMABLE
    print(f"[HCI Metrica] UI liberada en {ui_latency_ms:.2f} ms (Estándar de oro: < 100ms)")
    return redirect(url_for('index'))

def start_web_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_web_server()