"""環境変数管理"""
import os


class AppConfig:
    """アプリケーション設定"""

    # サーバー設定
    PORT: int = int(os.getenv("PORT", "8000"))

    # Redis設定
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # キュー設定
    QUEUE_NAME: str = os.getenv("QUEUE_NAME", "queue:jobs")

    # モデル設定
    SYNC_MODEL_PATH: str = os.getenv("SYNC_MODEL_PATH", "models/mobilenet_v2.onnx")
    ASYNC_MODEL_PATH: str = os.getenv("ASYNC_MODEL_PATH", "models/resnet50.onnx")

    # Worker設定
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "2"))

    # Redis TTL（秒）
    RESULT_TTL: int = 3600  # 1時間
