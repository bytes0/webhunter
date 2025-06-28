# Bug Bounty Platform

Una piattaforma full-stack modulare per bug bounty toolkit centralizzata.

## 🚀 Caratteristiche

- **Backend**: FastAPI con architettura modulare
- **Frontend**: Vue 3 con Vite
- **Containerizzazione**: Docker + Docker Compose
- **Moduli**: Recon, OSINT, Vulnerability Scanning, Reporting

## 📁 Struttura del Progetto

```
bb-platform/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Entry point dell'applicazione
│   │   ├── core/           # Configurazione e database
│   │   ├── modules/        # Moduli funzionali
│   │   └── api/            # Endpoint API
│   └── requirements.txt    # Dipendenze Python
├── frontend/               # Applicazione Vue 3
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml      # Orchestrazione container
├── Dockerfile.backend      # Container backend
└── Dockerfile.frontend     # Container frontend
```

## 🛠️ Setup e Avvio

### Con Docker (Raccomandato)

```bash
# Clona il repository
git clone <repository-url>
cd bb-platform

# Avvia tutti i servizi
docker compose up -d

# Accedi all'applicazione
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Sviluppo Locale

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📦 Moduli Disponibili

- **Recon**: Strumenti di ricognizione e discovery
- **OSINT**: Open Source Intelligence gathering
- **VulnScan**: Vulnerability scanning e assessment
- **Reporting**: Generazione report e dashboard

## 🔧 Sviluppo

### Aggiungere un Nuovo Modulo

1. Crea una nuova cartella in `backend/app/modules/`
2. Implementa il modulo seguendo la struttura esistente
3. Registra il modulo in `backend/app/main.py`

### API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/modules` - Lista moduli disponibili
- `POST /api/v1/recon/scan` - Avvia scan di ricognizione
- `POST /api/v1/osint/gather` - Raccolta informazioni OSINT
- `POST /api/v1/vulnscan/scan` - Avvia vulnerability scan
- `GET /api/v1/reporting/reports` - Lista report generati

## 📄 Licenza

MIT License 