import logging
from celery import Celery
import time
from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, MODEL_PATH
from .utils import get_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "recommendation_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60,
    task_soft_time_limit=45,
)

@celery_app.task(name="tasks.get_recommendations", bind=True)
def get_recommendations_task(self, movie_title: str, top_n: int = 5):
    """
    Celery задача для получения рекомендаций
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Запуск задачи для фильма: {movie_title}")
    
    self.update_state(
        state="PROCESSING",
        meta={"stage": "loading_model", "progress": 0.3}
    )
    
    try:
        time.sleep(1)
        
        self.update_state(
            state="PROCESSING",
            meta={"stage": "getting_recommendations", "progress": 0.7}
        )
        
        recommendations = get_recommendations(
            title=movie_title,
            model_path=MODEL_PATH,
            top_n=top_n
        )
        
        logger.info(f"[{task_id}] Получено {len(recommendations)} рекомендаций")
        
        return {
            "task_id": task_id,
            "movie_title": movie_title,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"[{task_id}] Ошибка: {str(e)}")
        raise self.retry(exc=e, countdown=5, max_retries=2)