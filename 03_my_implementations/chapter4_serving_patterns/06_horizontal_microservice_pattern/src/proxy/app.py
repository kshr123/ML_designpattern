"""ProxyサービスのFastAPIアプリ

3つの専門サービスに並列リクエストを送信
"""

from fastapi import FastAPI

from src.configurations import AppConfig
from src.proxy import routers

app = FastAPI(
    title=f"{AppConfig.title} - Proxy",
    version=AppConfig.version,
)

# ルーターを登録
app.include_router(routers.router)
