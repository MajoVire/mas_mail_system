from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import common
import math
import simulation 

app = Flask(__name__)

# --- CONFIGURACIÓN DE PAGINADO ---
LOGS_PER_PAGE = 5 

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
        .progress-bar { transition: width 0.6s ease; }
        
        .pagination-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #dee2e6;
        }

        /* --- NUEVO ESTILO: ALTURA FIJA PARA EVITAR SALTOS --- */
        .log-fixed-height {
            /* Calculado aprox: 
               Header (~50px) + 5 filas (~50px c/u) + Paginación (~50px) 
            */
            min-height: 400px; 
            display: flex;
            flex-direction: column;
            justify-content: space-between; /* Empuja la paginación al fondo */
        }
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
                        <div id="disk-bar" class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
                    </div>
                    <div id="clean-btn-container" style="display: none;">
                        <form action="/clean_disk" method="post">
                            <button type="submit" class="btn btn-warning w-100">🧹 Liberar Espacio</button>
                        </form>
                    </div>
                    <div id="system-ok-msg" class="text-center text-muted"><small>✅ Sistema Optimizado</small></div>
                </div>

                <div class="card p-3">
                    <h4>✉️ Redactar Nuevo Correo</h4>
                    <form action="/send_email" method="post">
                        <div class="mb-2">
                            <input type="email" name="to" class="form-control" placeholder="Destinatario" required>
                        </div>
                        <div class="mb-2">
                            <input type="text" name="subject" class="form-control" placeholder="Asunto" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Enviar Orden</button>
                    </form>
                </div>

                <div class="card p-3 border-danger">
                    <h4 class="text-danger">🔥 Simulación de Carga</h4>
                    <p class="small text-muted">Generar tráfico concurrente de 10 usuarios.</p>
                    <form action="/simulate" method="post">
                        <button type="submit" class="btn btn-outline-danger w-100">🚀 Lanzar 10 Usuarios Virtuales</button>
                    </form>
                </div>
            </div>

            <div class="col-md-7">
                <div class="card p-3">
                    <h4>📜 Bitácora de Agentes</h4>
                    
                    <div class="log-fixed-height">
                        
                        <table class="table table-striped log-table mb-0">
                            <thead class="table-dark">
                                <tr><th>Agente</th><th>Mensaje</th></tr>
                            </thead>
                            <tbody id="log-table-body">
                                </tbody>
                        </table>

                        <div class="pagination-container">
                            <button class="btn btn-sm btn-secondary" onclick="changePage(-1)" id="btn-prev">Anterior</button>
                            <span id="page-info" class="fw-bold">Cargando...</span>
                            <button class="btn btn-sm btn-secondary" onclick="changePage(1)" id="btn-next">Siguiente</button>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        let totalPages = 1;

        function updateDashboard() {
            fetch('/api/data?page=' + currentPage + '&t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    // Monitor de Disco
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

                    // Logs Paginados
                    const tbody = document.getElementById('log-table-body');
                    tbody.innerHTML = ''; 
                    
                    // Si no hay logs, podríamos mostrar un mensaje vacío para mantener altura,
                    // pero el CSS min-height ya se encarga de mantener la caja grande.
                    data.logs.forEach(log => {
                        const row = `<tr>
                            <td><span class="badge bg-info text-dark">${log.sender}</span></td>
                            <td>${log.body}</td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });

                    // Paginación
                    totalPages = data.total_pages; 
                    document.getElementById('page-info').innerText = `Página ${data.current_page} de ${data.total_pages}`;
                    document.getElementById('btn-prev').disabled = (data.current_page <= 1);
                    document.getElementById('btn-next').disabled = (data.current_page >= data.total_pages);
                })
                .catch(err => console.error(err));
        }

        function changePage(delta) {
            const newPage = currentPage + delta;
            if (newPage > 0 && newPage <= totalPages) {
                currentPage = newPage;
                updateDashboard();
            }
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
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    all_logs = list(common.system_logs)
    total_items = len(all_logs)
    
    total_pages = math.ceil(total_items / LOGS_PER_PAGE)
    if total_pages == 0: total_pages = 1 
    
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * LOGS_PER_PAGE
    end = start + LOGS_PER_PAGE
    
    sliced_logs = all_logs[start:end]

    return jsonify({
        'disk_usage': common.current_disk_usage,
        'logs': sliced_logs,
        'current_page': page,
        'total_pages': total_pages
    })

@app.route("/clean_disk", methods=['POST'])
def clean_disk():
    common.cleaning_requested = True
    return redirect(url_for('index'))

@app.route("/send_email", methods=['POST'])
def send_email():
    destinatario = request.form.get('to')
    asunto = request.form.get('subject')
    if destinatario and asunto:
        common.email_outbox.append({'to': destinatario, 'subj': asunto})
    return redirect(url_for('index'))

@app.route("/simulate", methods=['POST'])
def simulate():
    simulation.run_mass_simulation()
    return redirect(url_for('index'))

def start_web_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)