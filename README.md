# ⚙ DevOps Utility Hub

A lightweight, self-hosted Flask web dashboard for common DevOps tasks — system monitoring, log analysis, Docker container status, and Kubernetes pod health.

---
<img width="1078" height="586" alt="1" src="https://github.com/user-attachments/assets/26a0873a-bd7f-49c1-be76-6746631124fa" />



## Features

| Tool | Description |
|---|---|
| **Dashboard** | At-a-glance CPU, memory, disk and uptime overview |
| **System Monitor** | Real-time per-core CPU, memory breakdown, disk partitions, network I/O and top processes |
| **Log Analyzer** | Paste raw logs to parse by level, filter by severity or keyword, view summaries and detect anomaly bursts |
| **Docker Status** | Live container list with status, ports, networks, uptime and resource limits |
| **Kubernetes** | Pod listing across namespaces with phase, readiness, restart counts and clickable detail drawer |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/devops-utility-hub.git
cd devops-utility-hub
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Requirements

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `psutil` | CPU / memory / disk / network metrics |
| `docker` | Docker Engine SDK (requires Docker daemon running) |
| `kubernetes` | Kubernetes Python client (requires kubeconfig or in-cluster config) |

> **Docker & Kubernetes are optional.** The app runs fine without them — the relevant pages will display a friendly error message if the daemon / config is not found.

---

## Project Structure

```
devops-utility-hub/
├── app.py                  # Flask routes
├── requirements.txt
├── utils/
│   ├── log_analyzer.py     # Log parsing, filtering, summarisation
│   ├── system_monitor.py   # psutil wrappers
│   ├── docker_status.py    # Docker SDK wrapper
│   └── k8s_status.py       # Kubernetes client wrapper
├── templates/
│   ├── base.html           # Shared layout with sidebar
│   ├── index.html          # Dashboard
│   ├── system.html         # System monitor
│   ├── logs.html           # Log analyzer
│   ├── docker.html         # Docker containers
│   └── kubernetes.html     # K8s pods
└── static/
    └── style.css           # Full dark-theme CSS design system
```

---

## API Endpoints

### System
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/system/stats` | All system metrics |

### Logs
| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/api/logs/analyze` | `{log_text, level, keyword}` | Parse and filter entries |
| `POST` | `/api/logs/summary` | `{log_text}` | High-level summary |

### Docker
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/docker/containers` | All containers |

### Kubernetes
| Method | Path | Query Params | Description |
|---|---|---|---|
| `GET` | `/api/k8s/pods` | `namespace`, `all` | List pods |

---

## Kubernetes Setup

The app tries to load kube config in this order:

1. **In-cluster** (`KUBERNETES_SERVICE_HOST` env var present)
2. **`~/.kube/config`** file

If neither is available a clear error message is shown in the UI.

---

## Docker Setup

The Docker SDK connects to the local Docker daemon via the default socket (`unix:///var/run/docker.sock` on Linux/macOS, named pipe on Windows). Make sure the user running the app has permission to access the socket.

```bash
# Linux — add your user to the docker group
sudo usermod -aG docker $USER
```

---

## Customisation

- **Refresh intervals** — edit the `setInterval` calls in each template's `<script>` block.
- **Theme colours** — all colours are CSS variables in `static/style.css` under `:root`.
- **Port** — change `port=5000` in `app.py` or set the `PORT` environment variable.

---
## Output
Jenkins
<img width="1057" height="623" alt="2" src="https://github.com/user-attachments/assets/db6d4d22-193a-4b76-810b-613641c9b97a" />
Docker
<img width="1080" height="371" alt="3" src="https://github.com/user-attachments/assets/881bb1ed-8972-408f-b1fa-87e439c6d43b" />

K8s
<img width="1080" height="714" alt="4" src="https://github.com/user-attachments/assets/b13f43a4-2dfc-4503-9941-b79be7a635d1" />

Prometheus
<img width="1080" height="598" alt="5" src="https://github.com/user-attachments/assets/f560a2b8-9c13-4032-b3ff-679ce92adfb3" />

Grafana
<img width="1080" height="592" alt="WhatsApp Image 2026-07-04 at 11 19 02 PM" src="https://github.com/user-attachments/assets/d8b66da4-a263-48e5-81ed-88c9a69c9526" />

#Final outout
<img width="1080" height="555" alt="image" src="https://github.com/user-attachments/assets/701b24cc-bc3e-4ee3-96e3-d266d6f89166" />
<img width="1080" height="563" alt="image" src="https://github.com/user-attachments/assets/cec31e03-8468-428d-91db-0aeb4d9f3863" />
<img width="1080" height="584" alt="image" src="https://github.com/user-attachments/assets/fed181c7-73ee-4733-8fb0-8dddf70a5388" />
<img width="1080" height="605" alt="image" src="https://github.com/user-attachments/assets/21f748e5-3ae1-454d-a609-92a5b8721a65" />

## License

MIT
