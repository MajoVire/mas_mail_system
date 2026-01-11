from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import common

app = Flask(__name__)

# --- PLANTILLA HTML CON JAVASCRIPT (AJAX) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Panel de Control - Sistema Multiagente</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding: 20px; }
        .card { margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .log-table { font-size: 0.9em; }
        /* Animación suave para la barra */
        .progress-bar { transition: width 0.6s ease; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4 text-center">🤖 Dashboard Interactivo Multiagente</h1>
        
        <div class="row">
            <div class="col-md-5">
                
                <div class="card p-3">
                    <h4>💾 Monitor de Disco</h4>
                    <p>Uso Actual: <strong id="disk-text">Cargando...</strong></p>
                    
                    <div class="progress mb-3" style="height: 25px;">
                        <div id="disk-bar" class="progress-bar bg-success" 
                             role="progressbar" style="width: 0%"></div>
                    </div>

                    <div id="clean-btn-container" style="display: none;">
                        <form action="/clean_disk" method="post">
                            <button type="submit" class="btn btn-warning w-100">🧹 Liberar Espacio (Limpiar)</button>
                        </form>
                    </div>
                    <div id="system-ok-msg" class="text-center text-muted">
                        <small>✅ Sistema Optimizado</small>
                    </div>
                </div>

                <div class="card p-3">
                    <h4>✉️ Redactar Nuevo Correo</h4>
                    <form action="/send_email" method="post" id="email-form">
                        <div class="mb-2">
                            <input type="email" name="to" class="form-control" placeholder="Destinatario (ej: profe@ucuenca.edu.ec)" required>
                        </div>
                        <div class="mb-2">
                            <input type="text" name="subject" class="form-control" placeholder="Asunto" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Enviar Orden al Agente</button>
                    </form>
                </div>
            </div>

            <div class="col-md-7">
                <div class="card p-3">
                    <h4>📜 Bitácora de Agentes</h4>
                    <table class="table table-striped log-table">
                        <thead class="table-dark">
                            <tr>
                                <th>Agente</th>
                                <th>Mensaje</th>
                            </tr>
                        </thead>
                        <tbody id="log-table-body">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateDashboard() {
            // Agregamos '?t=' + tiempo actual para que el navegador NO guarde caché
            fetch('/api/data?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    // 1. ACTUALIZAR DISCO
                    const usage = data.disk_usage;
                    document.getElementById('disk-text').innerText = usage + '%';
                    
                    const bar = document.getElementById('disk-bar');
                    bar.style.width = usage + '%';
                    
                    // Cambiar color si es crítico
                    if (usage > 90) {
                        bar.className = 'progress-bar bg-danger';
                        document.getElementById('clean-btn-container').style.display = 'block';
                        document.getElementById('system-ok-msg').style.display = 'none';
                    } else {
                        bar.className = 'progress-bar bg-success';
                        document.getElementById('clean-btn-container').style.display = 'none';
                        document.getElementById('system-ok-msg').style.display = 'block';
                    }

                    // 2. ACTUALIZAR TABLA DE LOGS
                    const tbody = document.getElementById('log-table-body');
                    tbody.innerHTML = ''; // Limpiamos tabla actual
                    
                    data.logs.forEach(log => {
                        const row = `<tr>
                            <td><span class="badge bg-info text-dark">${log.sender}</span></td>
                            <td>${log.body}</td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });
                })
                .catch(err => console.error("Error actualizando:", err));
        }

        // Ejecutar la actualización cada 2 segundos
        setInterval(updateDashboard, 2000);
        // Ejecutar una vez al inicio
        updateDashboard();
    </script>
</body>
</html>
"""

# --- RUTAS ---

@app.route("/")
def index():
    # Solo renderizamos la estructura base, JS se encarga del resto
    return render_template_string(HTML_TEMPLATE)

# NUEVA RUTA API: Entrega los datos en formato JSON (para JS)
@app.route("/api/data")
def api_data():
    return jsonify({
        'disk_usage': common.current_disk_usage,
        'logs': list(common.system_logs)
    })

@app.route("/clean_disk", methods=['POST'])
def clean_disk():
    common.cleaning_requested = True
    # Redirigir al inicio (pero ahora es rápido)
    return redirect(url_for('index'))

@app.route("/send_email", methods=['POST'])
def send_email():
    destinatario = request.form.get('to')
    asunto = request.form.get('subject')
    
    if destinatario and asunto:
        common.email_outbox.append({'to': destinatario, 'subj': asunto})
    
    return redirect(url_for('index'))

def start_web_server():
    # Importante: threaded=True permite manejar peticiones mientras corre el script
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)