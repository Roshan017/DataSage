import redis, json
from redis.exceptions import ConnectionError, TimeoutError
from app.core.settings import get_settings

settings = get_settings()

_redis_client = None

def get_redis_client():
    global _redis_client
    if not settings.REDIS_ENABLED:
        return None
        
    if _redis_client is None:
        if settings.REDIS_URL and settings.REDIS_URL.strip() != "":
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        else:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            
    try:
        _redis_client.ping()
        return _redis_client
    except (ConnectionError, TimeoutError) as e:
        print(f"❌ Could not connect to Redis: {e}")
        return None


def cache_key(db_id: str, schema_name: str) -> str:
    return f"schema:{db_id}:{schema_name}"

def get_cached_schema(key: str):

    if not settings.REDIS_ENABLED:
        return None
    try:
        client = get_redis_client()
        val = client.get(key)
        return json.loads(val) if val else None
    except (ConnectionError, TimeoutError, json.JSONDecodeError):
        return None

def set_cached_schema(key: str, schema: dict, ttl: int | None = None):
    if not settings.REDIS_ENABLED:
        return None
    try:
        client = get_redis_client()
        client.setex(
            key,
            ttl or settings.REDIS_CACHE_TTL,
            json.dumps(schema)
        )
    except (ConnectionError, TimeoutError):
        pass
