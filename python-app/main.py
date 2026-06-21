import time
import random
import logging
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import psutil
from logging_config import setup_logging
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    start_http_server
)

# Configure Logging
log = setup_logging()
logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('app_request_total', 'Total requests', ['method', 'endpoint', 'status'])
ACTIVE_CONNECTIONS = Gauge('app_active_connections', 'Number of Active connections')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
CPU_USAGE = Gauge('app_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('app_memory_usage_bytes', 'Memory usage in bytes')
DISK_USAGE = Gauge('app_disk_usage_percent', 'Disk usage percentage')

# Business logic metrics
HEART_RATE = Gauge('health_heart_rate_bpm', 'Simulated heart rate in bpm')
BLOOD_PRESSURE_SYS = Gauge('health_blood_pressure_systolic', 'Systolic BP')
BLOOD_PRESSURE_DIA = Gauge('health_blood_pressure_diastolic', 'Diastolic BP')
BODY_TEMP = Gauge('health_body_temperature_celsius', 'Body temperature')
STEPS_COUNT = Counter('health_steps_total', 'Total steps taken')
SLEEP_HOURS = Gauge('health_sleep_hours', 'Hours of sleep')


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start_time = time.time()
        ACTIVE_CONNECTIONS.inc()
        try:
            if self.path == '/metrics':
                self.send_response(200)
                self.send_header('Content-Type', CONTENT_TYPE_LATEST)
                self.end_headers()
                self.wfile.write(generate_latest())
                REQUEST_COUNT.labels('GET', '/metrics', '200').inc()

            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                health_data = {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "version": "1.0.0"
                }
                self.wfile.write(json.dumps(health_data).encode())
                REQUEST_COUNT.labels('GET', '/health', '200').inc()

            elif self.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Health Metrics App is running\n")
                REQUEST_COUNT.labels('GET', '/', '200').inc()

            else:
                self.send_response(404)
                self.end_headers()
                REQUEST_COUNT.labels('GET', self.path, '404').inc()

        except Exception as e:
            logger.error(f"Error handling request: {e}", extra={'path': self.path})
            self.send_response(500)
            self.end_headers()
            REQUEST_COUNT.labels('GET', self.path, '500').inc()

        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels('GET', self.path).observe(duration)
            ACTIVE_CONNECTIONS.dec()

    def log_message(self, format, *args):
        pass  # Override to prevent default HTTP logging


def generate_health_metrics():
    logger.info("Starting health metrics generator")
    while True:
        try:
            # Simulate health metrics
            heart_rate = random.gauss(72, 8)
            heart_rate = max(40, min(120, heart_rate))

            bp_sys = random.gauss(120, 15)
            bp_sys = max(90, min(180, bp_sys))

            bp_dia = random.gauss(80, 10)
            bp_dia = max(60, min(120, bp_dia))

            temp = random.gauss(36.5, 0.5)
            temp = max(35.0, min(40.0, temp))

            # Update Prometheus metrics
            HEART_RATE.set(heart_rate)
            BLOOD_PRESSURE_SYS.set(bp_sys)
            BLOOD_PRESSURE_DIA.set(bp_dia)
            BODY_TEMP.set(temp)

            # Increment steps occasionally
            if random.random() > 0.7:
                STEPS_COUNT.inc(random.randint(1, 10))

            # Update sleep hours (varies slowly)
            sleep = random.gauss(7, 1)
            sleep = max(4, min(10, sleep))
            SLEEP_HOURS.set(sleep)

            # Update system metrics
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().used
            disk = psutil.disk_usage('/').percent

            CPU_USAGE.set(cpu)
            MEMORY_USAGE.set(mem)
            DISK_USAGE.set(disk)

            logger.info(
                "Generated health metrics",
                extra={
                    'heart_rate': round(heart_rate, 1),
                    'bp_sys': round(bp_sys, 1),
                    'bp_dia': round(bp_dia, 1),
                    'temp': round(temp, 2),
                    'cpu': round(cpu, 1),
                    'mem': round(mem / (1024 ** 2), 2),  # Convert to MB
                    'disk': round(disk, 2)
                }
            )

            # Simulate warning conditions
            if heart_rate > 100:
                logger.warning("High heart rate detected", extra={'heart_rate': round(heart_rate, 1)})

            if temp > 37.2:
                logger.warning("High body temperature detected", extra={'temp': round(temp, 2)})

            time.sleep(5)

        except Exception as e:
            logger.error(f"Error generating health metrics: {e}", exc_info=True)
            time.sleep(5)


def run_http_server():
    server = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    logger.info("Started HTTP server on port 8000")
    server.serve_forever()


if __name__ == "__main__":
    # Start HTTP server in background thread
    server_thread = Thread(target=run_http_server, daemon=True)
    server_thread.start()

    # Start Prometheus metrics server
    start_http_server(8001)
    logger.info("Started Prometheus metrics server on port 8001")

    # Generate health metrics in main thread
    generate_health_metrics()