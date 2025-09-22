"""
Caching utilities for performance optimization
"""
import time
from functools import wraps

# Simple in-memory cache
_cache = {}
_cache_times = {}

def timed_cache(seconds=300):
    """
    Function decorator that caches the result for a specified time period.
    
    Args:
        seconds: Number of seconds to cache the result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if result is in cache and not expired
            current_time = time.time()
            if key in _cache and current_time - _cache_times.get(key, 0) < seconds:
                return _cache[key]
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            _cache[key] = result
            _cache_times[key] = current_time
            
            return result
        return wrapper
    return decorator

# Cache cleanup function to prevent memory leaks
def cleanup_cache(max_age=3600):
    """
    Remove expired cache entries to prevent memory leaks
    
    Args:
        max_age: Maximum age in seconds before entry is removed
    """
    current_time = time.time()
    keys_to_delete = []
    
    for key, timestamp in _cache_times.items():
        if current_time - timestamp > max_age:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        if key in _cache:
            del _cache[key]
        if key in _cache_times:
            del _cache_times[key]
    
    return len(keys_to_delete)
