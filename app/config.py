import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

MODEL_PATH = os.getenv("MODEL_PATH", "app/models/recommendation_model.pkl")

APP_NAME = "Movie Recommendation API"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

PORT = int(os.getenv("PORT", 8000))