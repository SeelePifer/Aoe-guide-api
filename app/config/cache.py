"""
Persistent cache system for performance improvement
"""

import sqlite3
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Persistent cache manager with SQLite"""
    
    def __init__(self, db_path: str = "cache.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize cache database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes for performance improvement
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache(last_accessed)")
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate unique key for cache"""
        key_string = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store value in cache with TTL"""
        try:
            # Serialize value
            serialized_value = pickle.dumps(value)
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache (key, value, expires_at)
                    VALUES (?, ?, ?)
                """, (key, serialized_value, expires_at))
            
            logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT value, expires_at FROM cache 
                    WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
                """, (key, datetime.now()))
                
                row = cursor.fetchone()
                if row:
                    value, expires_at = row
                    
                    # Update access statistics
                    conn.execute("""
                        UPDATE cache 
                        SET access_count = access_count + 1, 
                            last_accessed = CURRENT_TIMESTAMP
                        WHERE key = ?
                    """, (key,))
                    
                    logger.debug(f"Cache HIT: {key}")
                    return pickle.loads(value)
                else:
                    logger.debug(f"Cache MISS: {key}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting cache {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                deleted = cursor.rowcount > 0
                
            if deleted:
                logger.debug(f"Cache DELETE: {key}")
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM cache 
                    WHERE expires_at IS NOT NULL AND expires_at <= ?
                """, (datetime.now(),))
                
                deleted_count = cursor.rowcount
                logger.info(f"Cleared {deleted_count} expired cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        COUNT(CASE WHEN expires_at IS NULL OR expires_at > ? THEN 1 END) as active_entries,
                        AVG(access_count) as avg_access_count,
                        MAX(last_accessed) as last_accessed
                    FROM cache
                """, (datetime.now(),))
                
                row = cursor.fetchone()
                return {
                    "total_entries": row[0],
                    "active_entries": row[1],
                    "avg_access_count": row[2] or 0,
                    "last_accessed": row[3]
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


class BuildCache:
    """Build-specific cache with optimized methods"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.builds_key = "builds:all"
        self.builds_by_type_key = "builds:type"
        self.builds_by_difficulty_key = "builds:difficulty"
        self.search_key = "builds:search"
    
    def cache_builds(self, builds: List[Any], ttl: int = 3600) -> bool:
        """Cache complete builds list"""
        return self.cache.set(self.builds_key, builds, ttl)
    
    def get_cached_builds(self) -> Optional[List[Any]]:
        """Retrieve builds from cache"""
        return self.cache.get(self.builds_key)
    
    def cache_builds_by_type(self, build_type: str, builds: List[Any], ttl: int = 3600) -> bool:
        """Cache builds filtered by type"""
        key = f"{self.builds_by_type_key}:{build_type}"
        return self.cache.set(key, builds, ttl)
    
    def get_cached_builds_by_type(self, build_type: str) -> Optional[List[Any]]:
        """Retrieve builds by type from cache"""
        key = f"{self.builds_by_type_key}:{build_type}"
        return self.cache.get(key)
    
    def cache_builds_by_difficulty(self, difficulty: str, builds: List[Any], ttl: int = 3600) -> bool:
        """Cache builds filtered by difficulty"""
        key = f"{self.builds_by_difficulty_key}:{difficulty}"
        return self.cache.set(key, builds, ttl)
    
    def get_cached_builds_by_difficulty(self, difficulty: str) -> Optional[List[Any]]:
        """Retrieve builds by difficulty from cache"""
        key = f"{self.builds_by_difficulty_key}:{difficulty}"
        return self.cache.get(key)
    
    def cache_search_results(self, query: str, builds: List[Any], ttl: int = 1800) -> bool:
        """Cache search results"""
        key = f"{self.search_key}:{hashlib.md5(query.encode()).hexdigest()}"
        return self.cache.set(key, builds, ttl)
    
    def get_cached_search_results(self, query: str) -> Optional[List[Any]]:
        """Retrieve search results from cache"""
        key = f"{self.search_key}:{hashlib.md5(query.encode()).hexdigest()}"
        return self.cache.get(key)
    
    def invalidate_builds_cache(self) -> bool:
        """Invalidate all builds cache"""
        keys_to_delete = [
            self.builds_key,
            f"{self.builds_by_type_key}:*",
            f"{self.builds_by_difficulty_key}:*",
            f"{self.search_key}:*"
        ]
        
        success = True
        for key_pattern in keys_to_delete:
            if "*" in key_pattern:
                # For wildcard patterns, we would need a more complex implementation
                continue
            success &= self.cache.delete(key_pattern)
        
        return success


# Global cache instance
cache_manager = CacheManager()
build_cache = BuildCache(cache_manager)
