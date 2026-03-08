import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

def create_sample_data():
    """Создает датасет с фильмами"""
    print("Создание датасета фильмов...")
    data = {
        'title': [
            'The Matrix', 
            'The Matrix Reloaded', 
            'The Matrix Revolutions',
            'Inception', 
            'Interstellar',
            'The Dark Knight', 
            'Pulp Fiction', 
            'Fight Club',
            'Forrest Gump', 
            'The Godfather',
            'The Godfather Part II',
            'The Dark Knight Rises',
            'Memento',
            'Django Unchained',
            'Kill Bill: Vol. 1'
        ],
        'overview': [
            'A computer hacker learns about the true nature of reality and his role in the war against its controllers.',
            'Freedom Fighters battle against the machines who have taken control of the world.',
            'The final battle for Zion begins as Neo discovers the truth about the Matrix.',
            'A thief who steals corporate secrets through dream-sharing technology must perform the perfect inception.',
            'A team of explorers travel through a wormhole in space in an attempt to ensure humanity survival.',
            'Batman fights the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.',
            'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence.',
            'An insomniac office worker and a devilish soap maker form an underground fight club that becomes much more.',
            'The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold.',
            'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his son.',
            'The early life and career of Vito Corleone in 1920s New York is portrayed.',
            'Eight years after the Jokers reign of chaos, Batman is forced out of exile to save Gotham.',
            'A man with short-term memory loss tries to track down his wifes murderer using a system of notes.',
            'With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal plantation owner.',
            'A former assassin seeks revenge on her former boss and his squad of assassins.'
        ]
    }
    return pd.DataFrame(data)

def main():
    print("=" * 60)
    print("НАЧАЛО ОБУЧЕНИЯ МОДЕЛИ РЕКОМЕНДАЦИЙ")
    print("=" * 60)
    
    print("\n1. Загрузка данных...")
    df = create_sample_data()
    print(f"   Загружено {len(df)} фильмов")
    
    print("\n2. Предобработка текста...")
    df['overview'] = df['overview'].fillna('')
    
    print("3. Создание TF-IDF матрицы...")
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = tfidf.fit_transform(df['overview'])
    print(f"   Размер матрицы: {tfidf_matrix.shape}")
    
    print("4. Вычисление схожести между фильмами...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"   Размер матрицы схожести: {cosine_sim.shape}")
    
    print("5. Создание индекса для поиска...")
    indices = pd.Series(df.index, index=df['title']).to_dict()
    
    print("6. Сохранение модели...")
    model_artifacts = {
        'cosine_sim': cosine_sim,
        'indices': indices,
        'titles': df['title'].tolist(),
        'tfidf_vectorizer': tfidf,
        'overviews': df['overview'].tolist()
    }
    
    os.makedirs('app/models', exist_ok=True)
    
    model_path = 'app/models/recommendation_model.pkl'
    joblib.dump(model_artifacts, model_path)
    print(f"   Модель сохранена в: {model_path}")
    
    print("\n7. Проверка модели...")
    test_model = joblib.load(model_path)
    print("   Ключи в модели:", list(test_model.keys()))
    print("   ✅ Модель работает!")
    
    print("\n" + "=" * 60)
    print("МОДЕЛЬ УСПЕШНО СОЗДАНА!")
    print("=" * 60)

if __name__ == "__main__":
    main()