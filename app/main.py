from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from celery.result import AsyncResult
from datetime import datetime
import os
import redis

from .config import APP_NAME, DEBUG, REDIS_HOST, REDIS_PORT, PORT
from .tasks import celery_app, get_recommendations_task
from .utils import get_all_movies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    description="Асинхронный API для рекомендации фильмов",
    version="1.0.0",
    debug=DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    movie_title: str = Field(..., min_length=1, description="Название фильма")
    top_n: int = Field(5, ge=1, le=20, description="Количество рекомендаций")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str = "Задача поставлена в очередь"

class RecommendationItem(BaseModel):
    rank: int
    title: str
    similarity_score: float

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в Movie Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Проверка работоспособности",
            "GET /movies": "Список всех фильмов",
            "POST /recommend": "Получить рекомендации",
            "GET /status/{task_id}": "Проверить статус задачи",
            "DELETE /task/{task_id}": "Отменить задачу"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    health_status = {
        "status": "healthy",
        "service": APP_NAME,
        "timestamp": datetime.now().isoformat(),
        "redis": "disconnected",
        "celery": "unknown"
    }
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)
        r.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"disconnected: {str(e)}"
    
    try:
        inspector = celery_app.control.inspect()
        stats = inspector.stats()
        workers = len(stats) if stats else 0
        health_status["celery"] = f"ok ({workers} workers)"
    except Exception as e:
        health_status["celery"] = f"error: {str(e)}"
    
    return health_status

@app.get("/movies")
async def get_movies_list():
    """Возвращает список всех фильмов"""
    try:
        movies = get_all_movies("app/models/recommendation_model.pkl")
        return {"count": len(movies), "movies": movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.post("/recommend", response_model=TaskResponse, status_code=202)
async def recommend_movies(request: RecommendationRequest):
    """Создает задачу на получение рекомендаций"""
    logger.info(f"Запрос: фильм '{request.movie_title}', top_n={request.top_n}")
    
    try:
        task = get_recommendations_task.delay(
            movie_title=request.movie_title,
            top_n=request.top_n
        )
        
        logger.info(f"Создана задача ID: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="processing",
            message=f"Задача создана. ID: {task.id}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=503, detail="Сервис временно недоступен")

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Проверяет статус задачи"""
    logger.info(f"Статус задачи: {task_id}")
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=task_result.state
    )
    
    if task_result.state == "SUCCESS":
        response.result = task_result.result
    elif task_result.state == "FAILURE":
        response.error = str(task_result.info)
    elif task_result.state == "PROCESSING" and task_result.info:
        response.result = task_result.info
    
    return response

@app.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """Отменяет задачу"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state in ["PENDING", "STARTED", "RETRY", "PROCESSING"]:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Задача {task_id} отменена", "status": "revoked"}
    else:
        return {"message": f"Задача {task_id} уже завершена", "status": task_result.state}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)