"""FastAPIアプリケーション初期化モジュール

FastAPIアプリケーションのエントリーポイントです。
"""

import logging

from fastapi import FastAPI

from src.api import routers
from src.configurations import APIConfigurations
from src.db import models
from src.db.database import engine

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(
    title=APIConfigurations.title,
    description=APIConfigurations.description,
    version=APIConfigurations.version,
)

# ルーターの登録
app.include_router(routers.router)

# 起動時イベント


@app.on_event("startup")
def startup_event():
    """
    アプリケーション起動時の処理

    - データベーステーブルの作成
    - モデルの読み込み確認
    """
    logger.info("Starting Batch Pattern API...")

    # データベーステーブルの作成
    logger.info("Creating database tables if not exist...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")

    logger.info("Batch Pattern API started successfully!")


# シャットダウン時イベント
@app.on_event("shutdown")
def shutdown_event():
    """
    アプリケーションシャットダウン時の処理
    """
    logger.info("Shutting down Batch Pattern API...")
    logger.info("Batch Pattern API shutdown complete.")


if __name__ == "__main__":
    import uvicorn

    # 開発用サーバー起動
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
