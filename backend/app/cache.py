import redis
import json
import pickle
from functools import wraps
from flask import current_app
import os
from datetime import timedelta

class RedisCache:
    def __init__(self, app=None):
        self.redis_client = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Redis cache with Flask app"""
        redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')  # Use DB 1 for cache

        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=False,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=False
            )
            self.redis_client.ping()

        except Exception:
            self.redis_client = None

        app.cache = self
    
    def get(self, key):
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key, value, timeout=300):
        """Set value in cache with timeout (default 5 minutes)"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, timeout, serialized_value)
        except Exception:
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.delete(key)
        except Exception:
            return False
    
    def clear_pattern(self, pattern):
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return False
    
    def flush_all(self):
        """Clear all cache"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            current_app.logger.error(f"Cache flush error: {e}")
            return False

# Cache decorator for functions
def cached(timeout=300, key_prefix=''):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            if hasattr(current_app, 'cache'):
                cached_result = current_app.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            if hasattr(current_app, 'cache'):
                current_app.cache.set(cache_key, result, timeout)
            
            return result
        return decorated_function
    return decorator

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'dashboard': 120,      # 2 minutes
    'quiz_list': 300,      # 5 minutes
    'subject_list': 600,   # 10 minutes
    'user_scores': 180,    # 3 minutes
    'quiz_questions': 900, # 15 minutes
    'user_profile': 300,   # 5 minutes
}

# Initialize cache instance
cache = RedisCache()
