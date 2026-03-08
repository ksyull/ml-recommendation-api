FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn[standard] && \
    pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/start.sh 2>/dev/null || true

ENV PORT=8080

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}