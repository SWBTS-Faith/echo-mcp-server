"""Database utilities for Echo Prayer MCP Server"""
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from src.logging import logger, log_error_with_context

class PrayerDatabase:
    """Manages prayer database operations and semantic search"""
    
    def __init__(self, db_path: str = "data/db/guided_prayers.db"):
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_random_prayer(self) -> Optional[Dict[str, Any]]:
        """Get a random prayer for one-minute prayer"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                "SELECT id, feed_title, prayer_title, prayer_description, prayer_steps FROM guided_prayers ORDER BY RANDOM() LIMIT 1"
            )
            
            prayer = c.fetchone()
            conn.close()
            
            if prayer:
                return {
                    "id": prayer[0],
                    "feed_title": prayer[1],
                    "prayer_title": prayer[2],
                    "prayer_description": prayer[3],
                    "prayer_steps": prayer[4]
                }
            return None
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_random_prayer"})
            return None
    
    def search_prayers_semantic(self, query: str, limit: int = 5, feed_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search prayers using semantic similarity"""
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode(query)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get all prayers with their embeddings
            if feed_title:
                c.execute(
                    "SELECT id, feed_title, prayer_title, prayer_description, prayer_steps, description_embedding FROM guided_prayers WHERE feed_title = ?",
                    (feed_title,)
                )
            else:
                c.execute(
                    "SELECT id, feed_title, prayer_title, prayer_description, prayer_steps, description_embedding FROM guided_prayers"
                )
            
            prayers = c.fetchall()
            conn.close()
            
            if not prayers:
                return []
            
            # Calculate similarities
            similarities = []
            for prayer in prayers:
                embedding_bytes = prayer[5]
                if embedding_bytes:
                    embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                    similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                    similarities.append((similarity, prayer))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, prayer in similarities[:limit]:
                results.append({
                    "id": prayer[0],
                    "feed_title": prayer[1],
                    "prayer_title": prayer[2],
                    "prayer_description": prayer[3],
                    "prayer_steps": prayer[4],
                    "similarity_score": float(similarity)
                })
            
            return results
            
        except Exception as e:
            log_error_with_context(e, {"operation": "search_prayers_semantic", "query": query})
            return []
    
    def get_prayer_by_id(self, prayer_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific prayer by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                "SELECT id, feed_title, prayer_title, prayer_description, prayer_steps FROM guided_prayers WHERE id = ?",
                (prayer_id,)
            )
            
            prayer = c.fetchone()
            conn.close()
            
            if prayer:
                return {
                    "id": prayer[0],
                    "feed_title": prayer[1],
                    "prayer_title": prayer[2],
                    "prayer_description": prayer[3],
                    "prayer_steps": prayer[4]
                }
            return None
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_prayer_by_id", "prayer_id": prayer_id})
            return None
    
    def get_feed_titles(self) -> List[str]:
        """Get all available feed titles"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("SELECT DISTINCT feed_title FROM guided_prayers ORDER BY feed_title")
            
            feeds = [row[0] for row in c.fetchall()]
            conn.close()
            
            return feeds
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_feed_titles"})
            return []
    
    def get_prayers_by_feed(self, feed_title: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get prayers from a specific feed"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                "SELECT id, feed_title, prayer_title, prayer_description, prayer_steps FROM guided_prayers WHERE feed_title = ? ORDER BY id LIMIT ?",
                (feed_title, limit)
            )
            
            prayers = c.fetchall()
            conn.close()
            
            return [
                {
                    "id": prayer[0],
                    "feed_title": prayer[1],
                    "prayer_title": prayer[2],
                    "prayer_description": prayer[3],
                    "prayer_steps": prayer[4]
                }
                for prayer in prayers
            ]
            
        except Exception as e:
            log_error_with_context(e, {"operation": "get_prayers_by_feed", "feed_title": feed_title})
            return []

# Global prayer database instance
prayer_db = PrayerDatabase()
