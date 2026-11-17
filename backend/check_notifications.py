import redis

client = redis.Redis(
    host='localhost',
    port=6379,
    db=1,
    decode_responses=True
)

print("Redis Database 1 Keys:")

keys = client.keys("*")

for key in keys:
    print(key)
    print("TTL:", client.ttl(key))