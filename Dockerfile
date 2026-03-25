FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY worker/requirements.txt /app/worker/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir -r /app/worker/requirements.txt

COPY . /app

CMD ["python", "bot/main.py"]