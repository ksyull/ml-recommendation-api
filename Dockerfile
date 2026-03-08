FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn[standard]

COPY app/ ./app/

RUN mkdir -p /app/app/models

ENV PORT=8080
ENV MODEL_PATH=/app/app/models/recommendation_model.pkl

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}