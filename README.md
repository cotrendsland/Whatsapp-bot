🤖 WhatsApp AI Bot — Sistema de Ventas Completo
Asistente virtual inteligente para WhatsApp construido con FastAPI, Twilio, Groq (LLaMA), Supabase y Google Sheets. Atiende clientes, consulta catálogo en tiempo real, registra pedidos y notifica al vendedor automáticamente.

✨ Funcionalidades

💬 Respuestas automáticas con IA (LLaMA 3.3 70B via Groq)
📦 Consulta de catálogo en tiempo real desde Google Sheets
🛒 Registro automático de pedidos en Google Sheets
📲 Notificación al vendedor por WhatsApp y email cuando llega un pedido
🔔 Notificación al cliente cuando el vendedor cambia el estado del pedido
🧠 Memoria de conversación persistente en Supabase
👤 Handoff a agente humano con palabras clave
⚡ Comandos /bot-on y /bot-off para gestionar clientes sin tocar código
🚀 Desplegado en Railway — activo 24/7


📋 Requisitos previos
Crear las siguientes cuentas antes de empezar:
ServicioURLPlanTwiliotwilio.com/try-twilioGratis ($15 crédito inicial)Groqconsole.groq.comGratisSupabasesupabase.comGratis (500 MB)Railwayrailway.appGratis ($5/mes crédito)GitHubgithub.comGratis
Software necesario en tu computador:

Python 3.10+ — python.org/downloads
Git — git-scm.com
VS Code — code.visualstudio.com
ngrok — ngrok.com/download (solo para pruebas locales)


🗂️ Estructura del proyecto
whatsapp-bot/
├── main.py           # Servidor principal FastAPI
├── database.py       # Conexión y funciones de Supabase
├── ai_engine.py      # Lógica de Groq + LLaMA
├── config.py         # Carga de variables de entorno
├── prompts.py        # System prompt personalizable
├── sheets.py         # Integración con Google Sheets
├── requirements.txt  # Dependencias del proyecto
├── Procfile          # Configuración para Railway
├── .env              # Credenciales (NUNCA subir a GitHub)
└── .gitignore        # Excluye archivos sensibles

⚙️ Instalación paso a paso
1. Clonar el repositorio
bashgit clone https://github.com/TU_USUARIO/whatsapp-bot.git
cd whatsapp-bot
2. Crear y activar entorno virtual
bashpython -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
3. Instalar dependencias
bashpip install -r requirements.txt
4. Crear el archivo .env
En Windows:
bashnotepad .env
Pega con tus credenciales reales:
envTWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EMPRESA_NOMBRE=Nombre de la Empresa
MAX_HISTORIAL=20
PORT=8000
Al guardar: Archivo → Guardar como → Nombre: .env → Tipo: Todos los archivos

⚠️ NUNCA subas el .env a GitHub.


🔑 Cómo obtener cada credencial
Twilio: console.twilio.com → página principal → Account SID y Auth Token
Groq: console.groq.com → API Keys → Create API Key (empieza con gsk_)
Supabase: supabase.com → tu proyecto → Settings → API → Project URL y anon/public key

🗄️ Configurar Supabase
SQL Editor → New query → ejecutar:
sqlCREATE TABLE conversations (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  phone      TEXT NOT NULL,
  role       TEXT NOT NULL CHECK (role IN ('user','assistant')),
  content    TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_phone ON conversations(phone);
CREATE INDEX idx_time  ON conversations(created_at);

CREATE TABLE users (
  phone     TEXT PRIMARY KEY,
  is_human  BOOLEAN DEFAULT FALSE,
  last_seen TIMESTAMPTZ DEFAULT NOW()
);

📊 Configurar Google Sheets
Estructura de la hoja Catalogo
Los encabezados deben ser exactamente:
IDCategoriaProductoDescripcionTallas DisponiblesColoresPrecioStock TotalReferenciaEstado

IDs deben empezar con R (R001, R002...)
Columna Estado debe decir exactamente Activo
Precios con formato $89.000

Estructura de la hoja Pedidos
# PedidoFechaHoraTelefonoNombre ClienteReferenciaProductoTallaColorCantidadPrecio Unit.TotalEstado
Hacer el Sheet público
Compartir → Cualquier persona con el enlace → Lector
Obtener el Sheet ID
https://docs.google.com/spreadsheets/d/AQUI_EL_ID/edit
Actualizar sheets.py
pythonSHEET_ID = "TU_SHEET_ID_AQUI"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/TU_URL/exec"

📱 Configurar Apps Script

En el Sheet: Extensiones → Apps Script
Pega el codigo del Apps Script
Actualiza las variables:

javascriptvar VENDEDOR_WHATSAPP = "+57XXXXXXXXXX";
var VENDEDOR_EMAIL    = "correo@gmail.com";
var TWILIO_SID        = "ACxxxxxxxx...";
var TWILIO_TOKEN      = "xxxxxxxx...";
var TWILIO_NUMBER     = "+14155238886";

Implementar → Nueva implementación → Aplicación web → Cualquier persona
Copia la URL /exec y pégala en sheets.py
Activar trigger: ícono reloj ⏰ → Agregar activador → onEdit → Al editar


🎨 Personalizar el bot
En prompts.py actualiza la info de la empresa.
En main.py actualiza el número del vendedor:
pythonVENDEDOR = "whatsapp:+57XXXXXXXXXX"

🧪 Probar en local
bash# Terminal 1
python main.py

# Terminal 2
ngrok http 8000
Verificar: https://TU-URL.ngrok-free.app/health
En Twilio → Sandbox Settings → When a message comes in:
https://TU-URL.ngrok-free.app/webhook

🚀 Desplegar en Railway
bashgit init
git add .
git commit -m "WhatsApp AI Bot v1"
git remote add origin https://github.com/TU_USUARIO/whatsapp-bot.git
git branch -M main
git push -u origin main

railway.app → New Project → Deploy from GitHub repo
Agregar todas las variables del .env en la pestaña Variables
Settings → Domains → Generate Domain
Actualizar webhook en Twilio con la URL de Railway


👤 Comandos del vendedor
ComandoFunción/bot-on +57XXXXXXXXXXReactiva el bot para ese cliente/bot-off +57XXXXXXXXXXDesactiva el bot para ese cliente
Flujo de atención humana

Cliente escribe "humano" → bot se desactiva y avisa al vendedor
Vendedor atiende al cliente directamente
Vendedor escribe /bot-on +57XXXXXXXXXX → bot se reactiva


🔔 Sistema de notificaciones automáticas
EventoNotificaciónPedido nuevoWhatsApp + email al vendedorEstado → ConfirmadoWhatsApp al clienteEstado → En procesoWhatsApp al clienteEstado → EntregadoWhatsApp al clienteEstado → CanceladoWhatsApp al clienteCliente pide asesorWhatsApp al vendedor con comando /bot-on

📊 Consultas útiles en Supabase
sql-- Conversaciones de hoy
SELECT * FROM conversations WHERE created_at >= CURRENT_DATE;

-- Usuarios en modo humano
SELECT phone, last_seen FROM users WHERE is_human = TRUE;

-- Reactivar bot manualmente
UPDATE users SET is_human = FALSE WHERE phone = 'whatsapp:+57XXXXXXXXXX';

-- Usuarios más activos
SELECT phone, COUNT(*) as mensajes FROM conversations
WHERE role = 'user' GROUP BY phone ORDER BY mensajes DESC LIMIT 10;

🔄 Actualizar el bot
bashgit add .
git commit -m "descripcion del cambio"
git push
Railway despliega automáticamente en 1-2 minutos.

❗ Errores comunes
ErrorCausaSoluciónsupabase_url is required.env vacío o mal guardadoVerifica el archivo .envURL supabase.comURL incorrectaCambia .com por .coHTTP 401 TwilioAuth Token incorrectoCopia token fresco desde TwilioBot no respondeWebhook mal configuradoVerifica URL en Twilio Sandbox SettingsModuleNotFoundErrorEntorno virtual no activoEjecuta venv\Scripts\activateCatálogo vacíoSheet no público o ID incorrectoVerifica Sheet público y Sheet ID

📄 Licencia
Este proyecto es de uso privado. No está permitida su redistribución sin autorización expresa del autor.
