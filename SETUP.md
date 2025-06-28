# Setup e Utilizzo - Bug Bounty Platform

## 🚀 Avvio Rapido

### Prerequisiti
- Docker e Docker Compose installati
- Git

### 1. Clona il repository
```bash
git clone <repository-url>
cd bb-platform
```

### 2. Avvia la piattaforma
```bash
docker compose up -d
```

### 3. Accedi all'applicazione
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Celery Monitor**: http://localhost:5555

## 📁 Struttura del Progetto

```
bb-platform/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── core/           # Configurazione
│   │   ├── modules/        # Moduli funzionali
│   │   └── api/            # Endpoint API
│   ├── requirements.txt    # Dipendenze Python
│   └── init.sql           # Inizializzazione DB
├── frontend/               # Vue 3 App
│   ├── src/
│   │   ├── views/         # Pagine Vue
│   │   ├── router/        # Routing
│   │   └── components/    # Componenti
│   ├── package.json       # Dipendenze Node.js
│   └── vite.config.js     # Configurazione Vite
├── docker-compose.yml     # Orchestrazione container
├── Dockerfile.backend     # Container backend
└── Dockerfile.frontend    # Container frontend
```

## 🔧 Moduli Disponibili

### 1. Reconnaissance (Recon)
- **Scopo**: Scoperta di subdomini, porte e tecnologie
- **Strumenti**: subfinder, nmap, httpx, nuclei
- **Endpoint**: `/api/v1/recon/*`

### 2. OSINT
- **Scopo**: Raccolta informazioni da fonti aperte
- **Fonti**: WHOIS, DNS, GitHub, Wayback Machine
- **Endpoint**: `/api/v1/osint/*`

### 3. Vulnerability Scanner
- **Scopo**: Scansione vulnerabilità web e network
- **Strumenti**: nuclei, nmap, nikto
- **Endpoint**: `/api/v1/vulnscan/*`

### 4. Reporting
- **Scopo**: Generazione report e dashboard
- **Formati**: PDF, HTML, JSON
- **Endpoint**: `/api/v1/reporting/*`

## 🛠️ Sviluppo Locale

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints Principali

### Health Check
- `GET /health` - Stato del servizio
- `GET /ready` - Readiness check

### Moduli
- `GET /api/v1/modules` - Lista moduli disponibili
- `GET /api/v1/modules/{module_name}` - Info modulo specifico

### Recon
- `POST /api/v1/recon/scan` - Avvia scan
- `GET /api/v1/recon/scan/{scan_id}` - Stato scan
- `GET /api/v1/recon/scan/{scan_id}/results` - Risultati

### OSINT
- `POST /api/v1/osint/gather` - Avvia raccolta
- `GET /api/v1/osint/gather/{task_id}` - Stato task
- `GET /api/v1/osint/gather/{task_id}/results` - Risultati

### Vulnerability Scanner
- `POST /api/v1/vulnscan/scan` - Avvia scan
- `GET /api/v1/vulnscan/scan/{scan_id}` - Stato scan
- `GET /api/v1/vulnscan/scan/{scan_id}/results` - Risultati

### Reporting
- `POST /api/v1/reporting/generate` - Genera report
- `GET /api/v1/reporting/reports` - Lista report
- `GET /api/v1/reporting/reports/{report_id}` - Dettagli report
- `GET /api/v1/reporting/dashboard` - Dati dashboard

## 🔒 Sicurezza

### Variabili d'Ambiente
Crea un file `.env` nel backend con:
```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://bb_user:bb_password@postgres:5432/bb_platform
REDIS_URL=redis://redis:6379
DEBUG=false
```

### Strumenti di Sicurezza
- **subfinder**: Scoperta subdomini
- **nmap**: Scansione porte e servizi
- **nuclei**: Scansione vulnerabilità
- **nikto**: Scansione web server
- **httpx**: HTTP probe

## 📈 Monitoraggio

### Celery Tasks
- **Worker**: Esegue task in background
- **Beat**: Scheduler per task periodici
- **Flower**: Monitoraggio task (porta 5555)

### Logs
```bash
# Logs backend
docker logs bb-platform-backend

# Logs frontend
docker logs bb-platform-frontend

# Logs database
docker logs bb-platform-postgres
```

## 🚀 Deployment

### Produzione
1. Modifica le variabili d'ambiente
2. Configura SSL/TLS
3. Imposta firewall
4. Configura backup database
5. Monitoraggio e alerting

### Scaling
```bash
# Scale workers
docker compose up -d --scale celery-worker=3

# Scale backend
docker compose up -d --scale backend=2
```

## 🐛 Troubleshooting

### Problemi Comuni

1. **Porte già in uso**
   ```bash
   # Cambia porte in docker-compose.yml
   ports:
     - "8001:8000"  # Backend
     - "3001:3000"  # Frontend
   ```

2. **Database non si connette**
   ```bash
   # Riavvia servizi
   docker compose down
   docker compose up -d
   ```

3. **Strumenti non disponibili**
   ```bash
   # Verifica nel container
   docker exec -it bb-platform-backend which subfinder
   ```

## 📚 Risorse Aggiuntive

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 🤝 Contribuire

1. Fork il repository
2. Crea un branch per la feature
3. Implementa le modifiche
4. Aggiungi test
5. Crea Pull Request

## 📄 Licenza

MIT License - vedi file LICENSE per dettagli. 