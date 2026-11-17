import redis
import json


redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=1,
    decode_responses=True
)


def get_cache(key):

    try:
        data = redis_client.get(key)

        if data:
            return json.loads(data)

        return None

    except redis.RedisError:
        return None


def set_cache(key, data, expiry=300):

    try:
        redis_client.setex(
            key,
            expiry,
            json.dumps(data)
        )

        return True

    except redis.RedisError:
        return False


def delete_cache(key):

    try:
        redis_client.delete(key)
        return True

    except redis.RedisError:
        return False


def clear_cache(key=None):

    try:
        if key:
            redis_client.delete(key)
        else:
            redis_client.flushdb()

        return True

    except redis.RedisError:
        return False