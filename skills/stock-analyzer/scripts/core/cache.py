"""File-based caching system with TTL support."""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional


class DataCache:
    """
    Simple file-based cache to avoid API rate limits.

    Cache keys are hashed from ticker + data_type + parameters.
    Each cache entry includes data and timestamp for TTL validation.
    """

    def __init__(self, cache_dir: str = './data/cache', ttl_minutes: int = 15):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_minutes: Time-to-live in minutes for cached data
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, *args) -> str:
        """Generate a unique cache key from arguments."""
        key_string = '_'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def get(self, *args) -> Optional[Any]:
        """
        Retrieve data from cache if not expired.

        Args:
            *args: Arguments to generate cache key

        Returns:
            Cached data if valid, None otherwise
        """
        key = self._generate_key(*args)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cache_entry = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, delete it
                cache_path.unlink()
                return None

            return cache_entry['data']

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, delete it
            cache_path.unlink()
            return None

    def set(self, *args, data: Any):
        """
        Store data in cache with timestamp.

        Args:
            *args: Arguments to generate cache key (last arg should be data)
            data: Data to cache
        """
        key = self._generate_key(*args[:-1]) if len(args) > 1 else self._generate_key(args[0])
        cache_path = self._get_cache_path(key)

        cache_entry = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_entry, f, indent=2)

    def invalidate(self, *args):
        """
        Remove specific cache entry.

        Args:
            *args: Arguments to generate cache key
        """
        key = self._generate_key(*args)
        cache_path = self._get_cache_path(key)

        if cache_path.exists():
            cache_path.unlink()

    def clear_old(self, days: int = 7):
        """
        Clear cache entries older than specified days.

        Args:
            days: Remove cache files older than this many days
        """
        cutoff = datetime.now() - timedelta(days=days)

        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    cache_entry = json.load(f)
                    cached_time = datetime.fromisoformat(cache_entry['timestamp'])

                    if cached_time < cutoff:
                        cache_file.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted file, delete it
                cache_file.unlink()

    def clear_all(self):
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
