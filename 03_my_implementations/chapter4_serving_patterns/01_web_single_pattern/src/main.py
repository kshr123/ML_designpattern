"""
FastAPIアプリケーション

Iris分類APIのメインアプリケーション。
"""

from fastapi import FastAPI

from src.api.routers import prediction
from src.configurations.constants import APIConfigurations

app = FastAPI(
    title=APIConfigurations.title,
    description=APIConfigurations.description,
    version=APIConfigurations.version,
)

# ルーターを登録
app.include_router(prediction.router, prefix="", tags=["prediction"])
