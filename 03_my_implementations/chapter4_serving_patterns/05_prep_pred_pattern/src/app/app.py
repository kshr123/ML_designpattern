"""FastAPIアプリケーション

Prep-Pred Pattern の前処理サービス（Prep Service）。
画像の前処理を行い、推論サービス（Pred Service）にgRPCで推論リクエストを送信。

アーキテクチャ:
┌──────────────┐  HTTP   ┌──────────────┐  gRPC   ┌──────────────┐
│   ユーザー   │ ------> │ Prep Service │ ------> │ Pred Service │
│  (Client)    │         │ (このファイル)│         │(ONNX Runtime)│
└──────────────┘         └──────────────┘         └──────────────┘
"""

from logging import getLogger

from fastapi import FastAPI
from src.app.routers import routers
from src.configurations import APIConfigurations

logger = getLogger(__name__)

# ========================================
# FastAPIアプリケーションの作成
# ========================================
# FastAPIインスタンスの初期化
# - title: API名（Swagger UIに表示）
# - description: API説明（Swagger UIに表示）
# - version: APIバージョン（Swagger UIに表示）
#
# 自動生成されるドキュメント:
# - Swagger UI: http://localhost:8002/docs
# - ReDoc: http://localhost:8002/redoc
app = FastAPI(
    title=APIConfigurations.title,
    description=APIConfigurations.description,
    version=APIConfigurations.version,
)

# ========================================
# ルーターの登録
# ========================================
# APIエンドポイントをアプリケーションに登録
# - routers.router: src/app/routers/routers.py で定義したルーター
# - prefix="": エンドポイントにプレフィックスを付けない
#   - 例: "/predict" → そのまま "/predict"
#   - prefix="/api" とすると "/api/predict" になる
# - tags=["prediction"]: Swagger UIでのグループ化
app.include_router(routers.router, prefix="", tags=["prediction"])

# 起動ログ出力
logger.info(f"FastAPI app initialized: {APIConfigurations.title} v{APIConfigurations.version}")
