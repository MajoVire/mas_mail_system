from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import common
import math
import os
import simulation 

app = Flask(__name__)

# --- PLANTILLA HTML (AHORA CON 3 PESTAÑAS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Multiagente - Majo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f0f2f5; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .nav-pills .nav-link.active { background-color: #0d6efd; }
        .table-hover tbody tr:hover { background-color: #f1f1f1; }
        .badge-sender { font-size: 0.9em; background-color: #e7f1ff; color: #0d6efd; border: 1px solid #0d6efd; }
        .badge-sent { font-size: 0.9em; background-color: #d1e7dd; color: #0f5132; border: 1px solid #0f5132; }
    </style>
</head>
<body>
    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>🤖 Sistema Multiagente</h1>
            <ul class="nav nav-pills" id="pills-tab" role="tablist">
                <li class="nav-item">
                    <a class="nav-link active" id="pills-dash-tab" data-bs-toggle="pill" href="#pills-dash" role="tab">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="pills-history-tab" data-bs-toggle="pill" href="#pills-history" role="tab" onclick="loadHistory('received')">📥 Recibidos</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="pills-sent-tab" data-bs-toggle="pill" href="#pills-sent" role="tab" onclick="loadHistory('sent')">📤 Enviados</a>
                </li>
            </ul>
        </div>
        
        <div class="tab-content" id="pills-tabContent">
            
            <div class="tab-pane fade show active" id="pills-dash" role="tabpanel">
                <div class="row">
                    <div class="col-md-5">
                        <div class="card p-4">
                            <h4>💾 Monitor de Disco</h4>
                            <h2 class="text-center my-3" id="disk-text">0%</h2>
                            <div class="progress mb-3" style="height: 25px;">
                                <div id="disk-bar" class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
                            </div>
                            <div id="clean-btn-container" style="display: none;">
                                <form action="/clean_disk" method="post">
                                    <button type="submit" class="btn btn-warning w-100 fw-bold">🧹 Liberar Espacio</button>
                                </form>
                            </div>
                            <div id="system-ok-msg" class="text-center text-muted"><small>✅ Sistema Optimizado</small></div>
                        </div>

                        <div class="card p-3">
                            <h4>✉️ Redactar Nuevo Correo</h4>
                            <form action="/send_email" method="post">
                                <div class="mb-2">
                                    <input type="email" name="to" class="form-control" placeholder="Para: ejemplo@gmail.com" required>
                                </div>
                                <div class="mb-2">
                                    <input type="text" name="subject" class="form-control" placeholder="Asunto" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Enviar Orden al Agente</button>
                            </form>
                        </div>
                    </div>

                    <div class="col-md-7">
                        <div class="card p-3" style="min-height: 500px;">
                            <h4>📜 Bitácora en Tiempo Real</h4>
                            <table class="table table-striped mt-3">
                                <thead class="table-dark"><tr><th>Agente</th><th>Mensaje</th></tr></thead>
                                <tbody id="log-table-body"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-history" role="tabpanel">
                <div class="card p-4">
                    <div class="d-flex justify-content-between">
                        <h4>📥 Historial de Correos Recibidos</h4>
                        <button class="btn btn-sm btn-primary" onclick="loadHistory('received')">🔄 Actualizar</button>
                    </div>
                    <div class="table-responsive mt-3">
                        <table class="table table-hover">
                            <thead class="bg-light"><tr><th>Fecha</th><th>Remitente</th><th>Asunto</th></tr></thead>
                            <tbody id="received-table-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="tab-pane fade" id="pills-sent" role="tabpanel">
                <div class="card p-4">
                    <div class="d-flex justify-content-between">
                        <h4>📤 Historial de Correos Enviados</h4>
                        <button class="btn btn-sm btn-success" onclick="loadHistory('sent')">🔄 Actualizar</button>
                    </div>
                    <p class="text-muted">Leído de <code>historial_enviados.csv</code></p>
                    <div class="table-responsive mt-3">
                        <table class="table table-hover">
                            <thead class="bg-light"><tr><th>Fecha</th><th>Destinatario</th><th>Asunto</th></tr></thead>
                            <tbody id="sent-table-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateDashboard() {
            fetch('/api/data?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    // Disco
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

                    // Logs
                    const tbody = document.getElementById('log-table-body');
                    tbody.innerHTML = '';
                    data.logs.forEach(log => {
                        const agente = log.sender || log.agente || "Sistema";
                        const mensaje = log.body || log.mensaje || "Info";
                        tbody.innerHTML += `<tr>
                            <td><span class="badge bg-secondary">${agente}</span></td>
                            <td>${mensaje}</td>
                        </tr>`;
                    });
                });
        }

        // CARGAR HISTORIALES (RECIBIDOS O ENVIADOS)
        function loadHistory(type) {
            const endpoint = (type === 'sent') ? '/api/history_sent' : '/api/history_received';
            const tbodyId = (type === 'sent') ? 'sent-table-body' : 'received-table-body';
            
            fetch(endpoint + '?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById(tbodyId);
                    tbody.innerHTML = '';
                    
                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No hay registros aún.</td></tr>';
                        return;
                    }

                    data.forEach(item => {
                        // Diferenciar estilo según tipo
                        const badgeClass = (type === 'sent') ? 'badge-sent' : 'badge-sender';
                        
                        tbody.innerHTML += `<tr>
                            <td><small>${item.date}</small></td>
                            <td><span class="${badgeClass} px-2 py-1 rounded">${item.person}</span></td>
                            <td class="fw-bold">${item.subject}</td>
                        </tr>`;
                    });
                })
                .catch(err => console.error("Error historial:", err));
        }

        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

# --- RUTAS ---
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    logs = list(common.system_logs)[-10:]
    logs.reverse()
    return jsonify({'disk_usage': common.current_disk_usage, 'logs': logs})

# LEER HISTORIAL RECIBIDOS
@app.route("/api/history_received")
def api_history_received():
    return read_csv_history("historial_correos.csv")

# LEER HISTORIAL ENVIADOS
@app.route("/api/history_sent")
def api_history_sent():
    return read_csv_history("historial_enviados.csv")

# FUNCIÓN GENÉRICA PARA LEER CSV
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
                        history_data.append({
                            "date": parts[0],
                            "person": parts[1], # Remitente o Destinatario
                            "subject": parts[2]
                        })
    except Exception as e:
        print(f"Error leyendo {filename}: {e}")
    return jsonify(history_data)

@app.route("/clean_disk", methods=['POST'])
def clean_disk():
    common.cleaning_requested = True
    return redirect(url_for('index'))

@app.route("/send_email", methods=['POST'])
def send_email():
    destinatario = request.form.get('to')
    asunto = request.form.get('subject')
    if destinatario and asunto:
        # Ponemos la orden en la cola para que el SenderAgent la tome
        common.email_outbox.append({'to': destinatario, 'subj': asunto})
    return redirect(url_for('index'))

@app.route("/simulate", methods=['POST'])
def simulate():
    simulation.run_mass_simulation()
    return redirect(url_for('index'))

def start_web_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_web_server()