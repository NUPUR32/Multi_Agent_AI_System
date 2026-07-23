# ⚡ NUPUR32® AI OPERATING SYSTEM

**Version 2035.0.0 • Codename: NOVA**  
*"An AI Company Inside Your Computer"*

[![CI/CD Pipeline](https://github.com/nupur32/nupur32-ai-os/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/nupur32/nupur32-ai-os/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

---

## 🌟 Overview

NUPUR32 AI OS is a **fully autonomous, self-improving, production-ready AI Operating System** that operates as an **AI company inside your computer**. It features:

- **40+ Specialized AI Agents** - From CEO to Emergency Recovery
- **14 Memory Types** - Complete cognitive architecture
- **10 Reasoning Frameworks** - CoT, ToT, GoT, Debate, Reflection, and more
- **3 Knowledge Systems** - RAG, Vector Search, Knowledge Graph
- **Enterprise Security** - Zero-trust, encryption, audit, threat detection
- **Production Infrastructure** - Docker, K8s, CI/CD, monitoring

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/nupur32/nupur32-ai-os.git
cd nupur32-ai-os

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run the System

```bash
# Interactive Mode (recommended first run)
python main.py

# Initialize System
python main.py --init

# Run a Mission
python main.py --mission "Research the latest trends in AI agents"

# Launch Futuristic Dashboard
python main.py --dashboard

# Check System Status
python main.py --status

# Start REST API
python main.py --api
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual stages
docker build --target production -t nupur32-core .
docker run -p 8000:8000 -p 8501:8501 nupur32-core
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NUPUR32® AI OS                            │
├─────────────────────────────────────────────────────────────┤
│                     🧠 ORCHESTRATOR                          │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  🤖 AGENTS  │  🧠 MEMORY   │  📚 KNOWLEDGE│  💡 REASONING  │
│  (40+)       │  (14 types)  │  (3 systems) │  (10 methods)  │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  🔌 PLUGINS │  🔒 SECURITY │  📊 MONITOR  │  🚀 DEPLOY    │
│  (hot-swap)  │  (zero-trust)│  (full obs)  │  (Docker/K8s)  │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                    EVENT BUS (Async Pub/Sub)                 │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
nupur32-ai-os/
├── ai_ecosystem/          # Core AI Ecosystem
│   ├── core/              # Infrastructure (Event Bus, DI, Plugins)
│   ├── config/            # Configuration & Model Registry
│   ├── agents/            # 40+ Specialized AI Agents
│   ├── memory/            # Cognitive Memory System
│   ├── knowledge/         # RAG, Knowledge Graph, Vector Search
│   ├── reasoning/         # Multi-framework Reasoning Engine
│   ├── monitoring/        # Observability & Metrics
│   ├── orchestrator.py    # Main System Orchestrator
│   └── api.py             # REST API Gateway
├── tests/                 # Comprehensive Test Suite
├── main.py                # Entry Point
├── dashboard_nova.py      # Futuristic Dashboard
├── Dockerfile             # Multi-stage Docker Build
├── docker-compose.yml     # Full Stack Deployment
└── .github/workflows/     # CI/CD Pipeline
```

---

## 🤖 Agent Ecosystem (40+)

| Category | Agents |
|----------|--------|
| **🧠 Executive** | CEO, Project Manager, Architect, Planner, Supervisor, Decision |
| **🔬 Intelligence** | Researcher, Internet, Reasoning, Analytics, Data Engineer, ML Engineer |
| **💻 Development** | Coding, Reviewer, Debugger, Testing, Documentation |
| **🛡️ Security** | Security, DevOps, Cloud, Risk Analysis, Ethics |
| **🎨 Creative** | Vision, Speech, Image, Video, Browser, Computer Control |
| **📋 Operations** | Email, Calendar, Finance, Legal, Monitoring |
| **🧠 Cognitive** | Memory, Knowledge, Reflection, Learning, Optimization |
| **⚙️ Core** | Consensus, Quality Assurance, Execution, Emergency Recovery |

Each agent has:
- ✅ Unique **personality** (Big 5 traits)
- ✅ Defined **goals** and **capabilities**
- ✅ Personal **memory** and **reflection**
- ✅ **Confidence scoring** and **performance metrics**
- ✅ **Self-learning** from experience

---

## 🧠 Memory System (14 Types)

| Type | Description | Duration |
|------|-------------|----------|
| **Working** | Current task context | Seconds |
| **Short-term** | Recent interactions | Minutes-Hours |
| **Long-term** | Consolidated knowledge | Indefinite |
| **Semantic** | Facts and concepts | Indefinite |
| **Episodic** | Personal experiences | Indefinite |
| **Procedural** | Skills and processes | Indefinite |
| **Conversation** | Chat history | Session |
| **Knowledge** | Learned information | Indefinite |
| **Skill** | Acquired capabilities | Indefinite |
| **Project** | Project-specific data | Project lifecycle |
| **User** | User preferences | Indefinite |
| **Emotional** | Affective context | Short-term |
| **Spatial** | Location awareness | Session |
| **Encrypted** | Secure data | Per policy |

---

## 💡 Reasoning Frameworks (10)

| Method | Description | Use Case |
|--------|-------------|----------|
| **Chain-of-Thought** | Step-by-step reasoning | Complex problem solving |
| **Tree-of-Thoughts** | Multiple reasoning paths | Creative exploration |
| **Graph-of-Thoughts** | Interconnected reasoning | System analysis |
| **Reflection** | Self-analysis & improvement | Quality assurance |
| **Self-Critique** | Error detection & correction | Code review |
| **Debate** | Multi-perspective analysis | Decision making |
| **Monte Carlo** | Probabilistic simulation | Risk assessment |
| **Goal Decomposition** | Hierarchical breakdown | Project planning |
| **Recursive** | Nested problem solving | Complex systems |
| **Hypothesis** | Generate & test | Research |

---

## 📊 System Capabilities

### Autonomous
- ✅ Self-planning and scheduling
- ✅ Independent task execution
- ✅ Automatic error recovery
- ✅ Continuous self-improvement
- ✅ Performance optimization

### Enterprise
- ✅ Multi-tenant support
- ✅ RBAC/ABAC security
- ✅ Audit logging
- ✅ Rate limiting
- ✅ Secrets management
- ✅ Encryption at rest/transit

### Integration
- ✅ REST API (FastAPI)
- ✅ WebSocket streaming
- ✅ Web search (Serper, Tavily)
- ✅ Browser automation
- ✅ Email/Calendar
- ✅ Cloud (AWS, Azure, GCP)
- ✅ Database (Postgres, MongoDB, Redis, Neo4j)
- ✅ File processing (PDF, DOCX, XLSX)

### Observability
- ✅ Prometheus metrics
- ✅ Grafana dashboards
- ✅ OpenTelemetry tracing
- ✅ Health checks
- ✅ GPU monitoring
- ✅ Alert system

---

## 🚦 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | System info |
| GET | `/health` | Health check |
| GET | `/status` | System status |
| POST | `/mission` | Execute mission |
| POST | `/reason` | Apply reasoning |
| POST | `/memory/store` | Store memory |
| GET | `/memory/search` | Search memories |
| GET | `/memory/stats` | Memory statistics |
| POST | `/knowledge/add` | Add knowledge |
| POST | `/knowledge/search` | Search knowledge |
| GET | `/agents` | List agents |
| GET | `/agents/{role}` | Get agent details |
| GET | `/metrics` | System metrics |
| GET | `/alerts` | Active alerts |

---

## 🐳 Deployment

### Docker
```bash
# Production build
docker build --target production -t nupur32-core .

# Development build
docker build --target development -t nupur32-dev .

# Dashboard
docker build --target dashboard -t nupur32-dashboard .

# Full stack
docker-compose up -d
```

### Kubernetes
```yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/configmap.yaml
```

### CI/CD Pipeline
The `.github/workflows/ci-cd.yml` includes:
- ✅ Code quality (Black, Ruff, MyPy)
- ✅ Unit & integration tests
- ✅ Security scanning (Bandit, Safety)
- ✅ Docker build & push
- ✅ Automated deployment

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_ecosystem --cov-report=html

# Run specific tests
pytest tests/test_event_bus.py -v
pytest tests/test_agents.py -v
pytest tests/test_memory.py -v
```

---

## 🔧 Configuration

Key environment variables (see `.env.example`):

```bash
# Models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
XAI_API_KEY=...

# Security
NUPUR32_MASTER_KEY=...
JWT_SECRET=...
ENCRYPTION_ENABLED=true

# Databases
POSTGRES_URL=postgresql://...
MONGODB_URL=mongodb://...
REDIS_URL=redis://...
```

---

## 📈 Performance

- **40+ agents** running concurrently
- **<100ms** event bus latency
- **99.97%** system uptime target
- **Horizontal scaling** via microservices
- **Auto-scaling** based on load
- **Distributed** task execution

---

## 🗺️ Future Roadmap

- [x] **v2035.0** - Core AI Ecosystem (Current)
- [ ] **v2035.1** - Federated multi-node deployment
- [ ] **v2035.2** - GUI agent (desktop automation)
- [ ] **v2035.3** - Voice interface & multimodal
- [ ] **v2035.4** - Marketplace & plugin ecosystem
- [ ] **v2036.0** - Self-evolving architecture

---

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Agent Development Guide](docs/AGENTS.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Guide](docs/SECURITY.md)

---

## 📄 License

Proprietary - NUPUR32® All Rights Reserved

---

<div align="center">
  <sub>Built with ❤️ by NUPUR32 • The Future of Autonomous AI</sub>
</div>