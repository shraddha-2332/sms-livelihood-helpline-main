import os
import redis


def get_redis_client(decode_responses=True):
    """Create a Redis client from REDIS_URL or host/port env vars."""
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        return redis.Redis.from_url(redis_url, decode_responses=decode_responses)

    host = os.environ.get('REDIS_HOST', 'localhost')
    port = int(os.environ.get('REDIS_PORT', 6379))
    db = int(os.environ.get('REDIS_DB', 0))
    return redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
