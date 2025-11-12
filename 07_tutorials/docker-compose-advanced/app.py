"""
環境変数を使用するFastAPIアプリケーション

環境変数で管理する項目:
- APP_NAME: アプリケーション名
- APP_VERSION: バージョン
- API_KEY: 外部サービスのAPIキー（機密情報）
- DATABASE_URL: データベース接続文字列（機密情報）
- DEBUG_MODE: デバッグモード（True/False）
"""

from fastapi import FastAPI, HTTPException, Header
import os

app = FastAPI()

# 環境変数から設定を読み込み
APP_NAME = os.getenv("APP_NAME", "MyApp")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
API_KEY = os.getenv("API_KEY")  # 必須: デフォルトなし
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


@app.get("/")
def read_root():
    """ルートエンドポイント - アプリ情報を返す"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "debug_mode": DEBUG_MODE,
        "message": "環境変数から設定を読み込みました"
    }


@app.get("/config")
def get_config():
    """設定情報を表示（機密情報はマスク）"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "database_url": DATABASE_URL.replace(
            DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL.split("//")[-1],
            "***masked***"
        ) if DATABASE_URL else None,
        "api_key_configured": API_KEY is not None,
        "debug_mode": DEBUG_MODE
    }


@app.get("/protected")
def protected_endpoint(x_api_key: str = Header(None)):
    """APIキーで保護されたエンドポイント"""
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API_KEY が設定されていません"
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="無効なAPIキー"
        )

    return {
        "message": "認証成功！",
        "data": "これは保護されたデータです"
    }


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    # 必須の環境変数がセットされているか確認
    is_healthy = API_KEY is not None

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "api_key_configured": API_KEY is not None,
        "database_configured": DATABASE_URL is not None
    }
