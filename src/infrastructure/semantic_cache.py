import hashlib
import json
import os
from typing import Any, Dict, Optional

import redis


class SemanticCache:
    """
    Redis-backed Semantic Cache for LLM responses and vector search queries.
    Provides an interface to cache exact matches or LLM outputs to reduce latency and cost.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            self.redis = redis.from_url(redis_url)
        else:
            self.redis = redis.Redis(host=host, port=port, db=db)

        self.ttl_seconds = int(
            os.environ.get("CACHE_TTL_SECONDS", 86400)
        )  # Default 24 hours

    def _generate_key(self, prompt: str, context: str = "") -> str:
        """Generates a deterministic hash for a given prompt and context."""
        payload = f"{prompt.strip()}||{context.strip()}"
        return f"semantic_cache:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

    def get_cached_response(
        self, prompt: str, context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a cached response if it exists."""
        key = self._generate_key(prompt, context)
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
        except redis.RedisError as e:
            import sys

            print(f"Redis cache read error: {e}", file=sys.stderr)
        return None

    def set_cached_response(
        self, prompt: str, response: Dict[str, Any], context: str = ""
    ) -> bool:
        """Caches an LLM response or query result."""
        key = self._generate_key(prompt, context)
        try:
            self.redis.setex(key, self.ttl_seconds, json.dumps(response))
            return True
        except redis.RedisError as e:
            import sys

            print(f"Redis cache write error: {e}", file=sys.stderr)
            return False
