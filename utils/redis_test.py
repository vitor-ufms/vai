import redis
# r = redis.Redis()
r = redis.Redis(host = '192.168.0.13', port = 6379, db = 0)
# r.mset({"Croatia":"Zagreb", "Bahamas":"Nassau"})
print(r.get("Bahamas"))
