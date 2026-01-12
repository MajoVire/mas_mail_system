# 📧 Sistema Multiagente de Gestión de Correos y Monitoreo

Este proyecto implementa un sistema inteligente basado en la arquitectura **PEAS** (Performance, Environment, Actuators, Sensors) utilizando Python y la plataforma **SPADE**. El sistema simula la gestión de correos electrónicos, monitorea recursos del servidor y envía alertas SMS en tiempo real.

![Estado del Proyecto](https://img.shields.io/badge/Estado-Terminado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Framework](https://img.shields.io/badge/SPADE-3.x-orange)

## 🚀 Características Principales

* **Arquitectura Distribuida:** 5 Agentes inteligentes comunicándose vía protocolo XMPP/FIPA-ACL.
* **Dashboard Interactivo:** Interfaz web en tiempo real (Flask + AJAX) para visualizar eventos y controlar agentes.
* **Monitoreo de Infraestructura:** El `DiskMonitorAgent` vigila el espacio en disco y alerta si supera el 90%.
* **Notificaciones SMS:** Integración con la API de **Twilio** para alertas críticas al celular del administrador.
* **Simulación de Usuarios:** Generación de tráfico de correos simulado hacia destinatarios aleatorios.

## 🤖 Arquitectura de Agentes

1.  **ReceptorAgent:** Analiza correos entrantes y valida destinatarios.
2.  **SenderAgent:** Gestiona la cola de envío de correos (manuales y automáticos).
3.  **NotificationAgent:** Pasarela de comunicación con Twilio para enviar SMS.
4.  **DiskMonitorAgent:** Sensor que verifica el estado del disco duro del servidor.
5.  **CoordinatorAgent:** Centraliza logs y auditoría del sistema.

## 🛠️ Requisitos Previos

* Python 3.9 o superior.
* Cuentas XMPP (ej: en [Jabbim](https://www.jabb.im/)) para cada agente.
* Cuenta en [Twilio](https://www.twilio.com/) (SID, Token y Número) para los SMS.

## 📦 Instalación y Configuración

Sigue estos pasos para poner el sistema en marcha:

### 1. Clonar el repositorio

    git clone <URL_DE_TU_REPOSITORIO>
    cd mas_mail_system

### 2. Instalar dependencias
Se recomienda usar un entorno virtual.

    pip install -r requirements.txt

### 3. Configurar Credenciales (IMPORTANTE ⚠️)
Por seguridad, las contraseñas no están incluidas en el código fuente.

1.  Busca el archivo `config_example.py`.
2.  **Cámbiale el nombre** a `config.py`.
3.  Abre `config.py` y coloca tus propias credenciales:

    # config.py
    # Credenciales XMPP (Jabbim u otro servidor)
    NOTIF_USER   = "tu_agente_notif@jabb.im"
    NOTIF_PASS   = "tu_password"
    # ... (repetir para los demás agentes según el archivo)

    # Credenciales Twilio (SMS)
    TWILIO_SID    = "ACxxxxxxxxxxxxxxxx"
    TWILIO_TOKEN  = "xxxxxxxxxxxxxxxxxx"

## ▶️ Ejecución

Para iniciar el sistema completo (Backend de Agentes + Servidor Web):

    python main.py

Una vez iniciado:
1.  Verás en la consola los logs de inicio de los 5 agentes.
2.  Abre tu navegador en: **`http://localhost:5000`**
3.  Interactúa con el Dashboard (puedes limpiar el disco o enviar correos manuales).

## 📂 Estructura del Proyecto

    mas_mail_system/
    ├── agents/                 # Código fuente de los agentes SPADE
    │   ├── coordinator_agent.py
    │   ├── disk_monitor_agent.py
    │   ├── notification_agent.py
    │   ├── receptor_agent.py
    │   └── sender_agent.py
    ├── web/                    # Interfaz Web (Flask)
    │   └── dashboard.py
    ├── common.py               # Memoria compartida (interfaz Agente-Web)
    ├── config_example.py       # Plantilla de configuración (¡RENOMBRAR!)
    ├── main.py                 # Punto de entrada
    └── requirements.txt        # Librerías necesarias
