# Observability Stack

A containerized Python application that generates simulated health metrics, paired with a complete observability sidecar stack using **Prometheus**, **Loki**, and **Grafana**. All services run via Docker Compose with health checks and pre-configured dashboards.

---

## Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Python App │  │   Sidecar    │  │  Sidecar         │   │
│  │  (Main App)  │  │  Prometheus  │  │  Loki            │   │
│  │  Port: 8000  │  │  Port: 9090  │  │  Port: 3100      │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                   │             │
│         │  metrics/logs   │  scrape           │  push       │
│         └─────────────────┴───────────────────┘             │
│                           │                                 │
│                    ┌──────┴──────┐                          │
│                    │   Grafana   │                          │
│                    │  Port: 3000 │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘


| Service | Role | Port |
|---------|------|------|
| **Python App** | Generates health metrics & structured JSON logs | 8000, 8001 |
| **Prometheus** | Metrics collection & time-series database | 9090 |
| **Loki** | Log aggregation & indexing | 3100 |
| **Promtail** | Log shipper (reads Docker logs → Loki) | 9080 |
| **Grafana** | Visualization & dashboards | 3000 |
| **cAdvisor** | Container resource metrics | 8080 |
| **Node Exporter** | Host system metrics | 9100 |

---

## Features

- **Simulated Health Metrics**: Heart rate, blood pressure, body temperature, steps, sleep hours
- **System Metrics**: CPU, memory, disk usage via `psutil`
- **Structured JSON Logging**: All logs are JSON-formatted with parseable fields
- **Prometheus Metrics**: Custom metrics exposed on `/metrics` endpoint
- **Pre-built Grafana Dashboard**: Health metrics, application performance, and live logs
- **Health Checks**: Every service has Docker health checks configured
- **LogQL Support**: Search and filter logs by level, container, timestamp, or custom fields

---

## Project Structure
observability-stack/
├── docker-compose.yml
├── grafana
│   ├── dashboards
│   │   └── health-metrics.json
│   └── provisioning
│       ├── dashboards
│       │   └── dashboard.yml
│       └── datasources
│           └── datasources.yml
├── loki
│   └── loki-config.yml
├── prometheus
│   └── prometheus.yml
├── promtail
│   └── promtail-config.yml
├── python-app
│   ├── Dockerfile
│   ├── logging_config.py
│   ├── main.py
│   └── requirements.txt
└── Readme.md


---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- ~2 GB free RAM

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/observability-stack.git
cd observability-stack
```

### 2. Start the stack
```bash
docker compose up -d --build
```

### 3. Verify services
```bash
docker compose ps
```

All services should show healthy (except Promtail on some systems — this is cosmetic, logs still flow).

### 4. Access the services

| Service         | URL                             | Default Credentials  |
| --------------- | ------------------------------- | -------------------- |
| **Grafana**     | <http://localhost:3000>         | `admin` / `admin123` |
| **Prometheus**  | <http://localhost:9090>         | —                    |
| **Python App**  | <http://localhost:8000>         | —                    |
| **App Metrics** | <http://localhost:8001/metrics> | —                    |
| **Loki**        | <http://localhost:3100/ready>   | —                    |

### 5. View the Dashboard
- Open Grafana → http://localhost:3000
- Login with admin / admin123
- Navigate to Dashboards → Browse → Health Metrics Dashboard

### 6. Searching Logs in Grafana

- Go to Explore (compass icon in left sidebar)
- Select Loki as datasource
- Use LogQL queries:
```bash

# All logs
{job="docker-logs"}

# Filter by level
{job="docker-logs"} |= "level=WARNING"

# Parse JSON and filter
{job="docker-logs"} | json | level="ERROR"

# Search for specific events
{job="docker-logs"} |= "Elevated heart rate"

# Live tail (click "Live" button)
{job="docker-logs"} | json | heart_rate > 100

```
### Health Metrics Generated

| Metric                            | Description                       | Type      |
| --------------------------------- | --------------------------------- | --------- |
| `health_heart_rate_bpm`           | Simulated heart rate (50-120 BPM) | Gauge     |
| `health_blood_pressure_systolic`  | Systolic BP (90-160 mmHg)         | Gauge     |
| `health_blood_pressure_diastolic` | Diastolic BP (60-100 mmHg)        | Gauge     |
| `health_body_temperature_celsius` | Body temp (35.5-37.5 °C)          | Gauge     |
| `health_steps_total`              | Total steps taken                 | Counter   |
| `health_sleep_hours`              | Hours of sleep (4-10 hrs)         | Gauge     |
| `app_cpu_usage_percent`           | System CPU usage                  | Gauge     |
| `app_memory_usage_bytes`          | System memory used                | Gauge     |
| `app_disk_usage_percent`          | Disk usage percentage             | Gauge     |
| `app_requests_total`              | HTTP request count                | Counter   |
| `app_request_duration_seconds`    | Request latency                   | Histogram |


### Stopping the Stack

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clears all data)
docker compose down -v

```

### Troubleshooting

## No Logs in Grafana
```bash

# Check if Python app is logging
docker compose logs --tail=50 python-app

# Check Promtail status
docker compose logs --tail=50 promtail

# Check Loki labels
curl -s "http://localhost:3100/loki/api/v1/label/job/values" | python3 -m json.tool

# Restart promtail
docker compose restart promtail

Service Unhealthy
bash

# Check specific service logs
docker compose logs <service-name>

# Restart a service
docker compose restart <service-name>

# Rebuild and restart
docker compose up -d --build <service-name>
```

## Port Already in Use
```bash

# Find what's using port 3000
sudo lsof -i :3000

# Or change ports in docker-compose.yml
```

### Technologies Used

- Python 3.11 with prometheus-client, python-json-logger, psutil
- Prometheus v2.47.0
- Loki v3.0.0
- Promtail v2.9.0
- Grafana v10.1.0
- cAdvisor v0.47.2
- Node Exporter v1.6.1