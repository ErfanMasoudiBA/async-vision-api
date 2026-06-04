import redis

r = redis.Redis(host="127.0.0.1", port="6379", db=0, decode_responses=True)

r.set("test_key", "salam")

value = r.get("test_key")
print(value, type(value))
