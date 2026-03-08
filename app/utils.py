import joblib
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

_model = None

def load_model(model_path: str):
    """Загружает модель рекомендаций (один раз)"""
    global _model
    if _model is None:
        try:
            logger.info(f"Загрузка модели из {model_path}")
            _model = joblib.load(model_path)
            logger.info("✅ Модель успешно загружена")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели: {e}")
            raise
    return _model

def get_recommendations(
    title: str, 
    model_path: str, 
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Получает рекомендации для фильма
    """
    data = load_model(model_path)
    
    if title not in data['indices']:
        return []
    
    idx = data['indices'][title]
    
    sim_scores = list(enumerate(data['cosine_sim'][idx]))
    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    sim_scores = sim_scores[1:top_n+1]
    
    recommendations = []
    for i, score in sim_scores:
        recommendations.append({
            'rank': len(recommendations) + 1,
            'title': data['titles'][i],
            'similarity_score': float(score)
        })
    
    return recommendations

def get_all_movies(model_path: str) -> List[str]:
    """Возвращает список всех фильмов"""
    data = load_model(model_path)
    return data['titles']