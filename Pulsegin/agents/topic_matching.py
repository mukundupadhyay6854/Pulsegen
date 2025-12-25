import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import Dict, List, Tuple, Optional
import sqlite3
from datetime import datetime

class TopicMatchingAgent:
    
    def __init__(self, db_path: str = 'db/trends.db', similarity_threshold: float = 0.75):
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded.")
    
    def find_or_create_topic(self, review_summary: str, description: str = "") -> Tuple[int, bool]:
        review_embedding = self.embedding_model.encode(review_summary, convert_to_numpy=True)
        
        existing_topics = self._get_all_topics()
        
        if not existing_topics:
            topic_id = self._create_new_topic(review_summary, description, review_embedding)
            return topic_id, True
        
        best_match_id, best_similarity = self._find_best_match(review_embedding, existing_topics)
        
        if best_similarity >= self.similarity_threshold:
            self._update_topic_last_seen(best_match_id)
            return best_match_id, False
        else:
            topic_id = self._create_new_topic(review_summary, description, review_embedding)
            return topic_id, True
    
    def _get_all_topics(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic_id, topic_name, embedding, description
            FROM topics
        """)
        
        topics = []
        for row in cursor.fetchall():
            topic_id, topic_name, embedding_blob, description = row
            embedding = pickle.loads(embedding_blob)
            topics.append({
                'topic_id': topic_id,
                'topic_name': topic_name,
                'embedding': embedding,
                'description': description
            })
        
        conn.close()
        return topics
    
    def _find_best_match(self, review_embedding: np.ndarray, existing_topics: List[Dict]) -> Tuple[Optional[int], float]:
        if not existing_topics:
            return None, 0.0
        
        best_match_id = None
        best_similarity = 0.0
        
        review_emb = review_embedding.reshape(1, -1)
        
        for topic in existing_topics:
            topic_emb = topic['embedding'].reshape(1, -1)
            similarity = cosine_similarity(review_emb, topic_emb)[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = topic['topic_id']
        
        return best_match_id, best_similarity
    
    def _create_new_topic(self, topic_name: str, description: str, embedding: np.ndarray) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        embedding_blob = pickle.dumps(embedding)
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO topics (topic_name, description, embedding, created_at, last_seen)
            VALUES (?, ?, ?, ?, ?)
        """, (topic_name, description, embedding_blob, now, now))
        
        topic_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return topic_id
    
    def _update_topic_last_seen(self, topic_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE topics SET last_seen = ? WHERE topic_id = ?
        """, (now, topic_id))
        
        conn.commit()
        conn.close()
    
    def get_topic_name(self, topic_id: int) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT topic_name FROM topics WHERE topic_id = ?", (topic_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
