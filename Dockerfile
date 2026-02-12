FROM python:3.11-slim

WORKDIR /app

# Minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY app.py .

EXPOSE 7860

ENV PYTHONUNBUFFERED=1
ENV GEVENT_RESOLVER=ares

CMD ["python", "app.py"]
