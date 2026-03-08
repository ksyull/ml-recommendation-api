FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir fastapi uvicorn[standard]
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p /app/app/models

ENV PORT=8080
ENV MODEL_PATH=/app/app/models/recommendation_model.pkl

CMD ["/usr/local/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]