"""
FastAPI Application

Model DBのAPIアプリケーションのエントリーポイント。
"""

from fastapi import FastAPI

from src.api.routers import api, health

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Model DB API",
    description="機械学習モデルのライフサイクル管理システム",
    version="0.1.0",
)

# ルーターの登録
app.include_router(health.router, tags=["Health"])
app.include_router(api.router, tags=["API"])
