"""各専門サービスのFastAPIアプリ

Setosa/Versicolor/Virginicaの各サービス
"""

from fastapi import FastAPI

from src.configurations import AppConfig, ServiceConfig
from src.services import routers

app = FastAPI(
    title=f"{AppConfig.title} - {ServiceConfig.mode.capitalize()} Service",
    version=AppConfig.version,
)

# ルーターを登録
app.include_router(routers.router)
