# Bug Bounty Platform

A modular full-stack platform for centralized bug bounty tooling.

## 🚀 Features

- **Backend**: FastAPI with modular architecture
- **Frontend**: Vue 3 with Vite
- **Containerization**: Docker + Docker Compose
- **Modules**: Recon, OSINT, Vulnerability Scanning, Reporting

## 📁 Project Structure

```
bb-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── core/           # Config and database
│   │   ├── modules/        # Functional modules
│   │   └── api/            # API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vue 3 frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml      # Container orchestration
├── Dockerfile.backend      # Backend container
└── Dockerfile.frontend     # Frontend container
```

## 🛠️ Setup & Usage

### With Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd bb-platform

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📦 Available Modules

- **Recon**: Reconnaissance and asset discovery tools
- **OSINT**: Open Source Intelligence gathering
- **VulnScan**: Vulnerability scanning and assessment
- **Reporting**: Report generation and dashboard
- **Exploitation**: Exploitation tools for testing vulnerabilities

## 🔧 Development

### Adding a New Module

1. Create a new folder in `backend/app/modules/`
2. Implement your module following the existing structure
3. Register the module in `backend/app/main.py`

### API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/modules` - List available modules
- `POST /api/v1/recon/scan` - Start a reconnaissance scan
- `POST /api/v1/osint/gather` - Gather OSINT information
- `POST /api/v1/vulnscan/scan` - Start a vulnerability scan
- `GET /api/v1/reporting/reports` - List generated reports

## 📄 License

MIT License 