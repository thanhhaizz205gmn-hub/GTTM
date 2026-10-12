# 🚅 Hanoi High-Speed Railway Station — 3D Digital Twin & AI Energy Optimization

[![Live Production](https://img.shields.io/badge/Production-Live%20Demo-success?style=for-the-badge&logo=cloudflare)](https://gamification.ink)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM-blue?style=for-the-badge)](https://lightgbm.readthedocs.io/)
[![Unity 6](https://img.shields.io/badge/Simulation-Unity%206%20WebGL-black?style=for-the-badge&logo=unity)](https://unity.com/)
[![Docker Compose](https://img.shields.io/badge/Deploy-Docker%20Compose-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

> **A real-time 4-tier Digital Twin ecosystem integrating AI-driven predictive control for HVAC, ventilation, and biological lighting at Hanoi High-Speed Railway Station.**

🌐 **Live Demo:** [https://gamification.ink](https://gamification.ink)  
📊 **Interactive Analytics Dashboard:** [https://gamification.ink/dashboard](https://gamification.ink/dashboard)  
📖 **Interactive Swagger Docs:** [https://gamification.ink/docs](https://gamification.ink/docs)

---

## 🏛️ System Architecture

The system operates on an automated 4-tier loop:

```
[ Tier 1: IoT & Environment Sensing ]
  ├── n8n Workflow (Polls OpenWeatherMap every 15 mins)
  └── Mock IoT Sensor (Simulates passenger influx & station climate every 3s)
                 │
                 ▼
[ Tier 2: Cloud Sync & Ingestion ]
  └── Supabase (PostgreSQL tables: sensor_logs, weather_logs, energy_history)
                 │
                 ▼
[ Tier 3: AI Inference Engine (FastAPI v2.0) ]
  ├── LightGBM Predictive Model (`digital_twin_hvac_model.pkl`)
  ├── 30-60 Min Rolling Forecast (5-min resolution) with Gaussian Passenger Surge Detection
  └── Ventilation & Lighting Adaptive Optimization (Standby / Normal / Boost / Emergency)
                 │
                 ▼
[ Tier 4: Interactive 3D Digital Twin ]
  ├── Unity 6 WebGL Simulation with real-time temperature heatmaps
  └── Dual Split-Screen Web Dashboard with Chart.js analytics & dynamic IoT overrides
```

---

## ⚡ Key Highlights & Benchmark Results

- **20% – 30% Cumulative Energy Savings**: Dynamically throttles HVAC power based on outdoor weather and real-time passenger loads compared to the static 85% full-load benchmark.
- **2,000,000 Time-Series Records Engineered**: Synthetic dataset based on realistic Hanoi seasonal climate conditions.
- **Microservices Deployment**: 4 containerized Docker services routed via Nginx reverse proxy (Gzip WebGL compression) and Cloudflare Tunnel.
- **High-Concurrency Resilience**: Validated under stress tests simulating 5,000+ virtual passengers with sub-50ms inference latency.

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.10+ for local development

### Launch with Docker Compose
```bash
docker-compose up -d --build
```

The stack starts 4 services:
1. `digital_twin_app`: FastAPI AI Backend (`:8000`)
2. `digital_twin_mock_sensor`: Background sensor emulator
3. `digital_twin_nginx`: Nginx reverse proxy serving WebGL & SSL
4. `digital_twin_cloudflared`: Automated Cloudflare Zero-Trust Tunnel

---

## 🛠️ Tech Stack

- **Backend / Inference:** Python 3.10, FastAPI, Uvicorn, Pydantic
- **Machine Learning:** LightGBM, scikit-learn, StandardScaler, NumPy, Pandas
- **3D Digital Twin:** Unity 6 WebGL, C#, Gzip decompression fallback
- **Frontend Dashboard:** HTML5, CSS3 Glassmorphism, Chart.js, Jinja2
- **Data Ingestion:** Supabase (PostgreSQL), n8n Workflow Automation
- **DevOps & Infrastructure:** Docker Compose, Nginx, Cloudflare Zero-Trust Tunnel

---

## 👤 Author

- **Do Thanh Hai** - *Lead Architect & AI Systems Engineer*
- **Institution:** University of Transport Technology (UTT)
- **GitHub:** [@thanhhaizz205gmn-hub](https://github.com/thanhhaizz205gmn-hub)
