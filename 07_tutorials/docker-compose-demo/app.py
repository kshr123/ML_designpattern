from fastapi import FastAPI
import redis
import os

app = FastAPI()

# Redisに接続（docker-composeで定義されたサービス名で接続）
redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

@app.get("/")
def read_root():
    return {"message": "Auto-reload is working! 🔥", "status": "hot reload enabled"}

@app.get("/count")
def get_count():
    """アクセスカウンターを表示"""
    count = r.incr("visit_count")
    return {"visit_count": count}

@app.get("/reset")
def reset_count():
    """カウンターをリセット"""
    r.set("visit_count", 0)
    return {"message": "Counter reset", "visit_count": 0}
