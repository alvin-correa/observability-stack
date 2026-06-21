FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

#install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy the application code
COPY main.py .
COPY logging_config.py .

#create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

#expose ports
EXPOSE 8000 8001

#health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

 #start the application
 CMD ["python", "main.py"]