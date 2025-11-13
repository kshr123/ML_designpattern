"""設定管理

環境変数から設定を読み込む
"""

import os
from typing import Dict


class RedisConfig:
    """Redis設定"""

    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    queue_name: str = os.getenv("QUEUE_NAME", "predict_queue")


class TFServingConfig:
    """TensorFlow Serving設定"""

    host: str = os.getenv("TF_SERVING_HOST", "localhost")
    grpc_port: int = int(os.getenv("TF_SERVING_GRPC_PORT", "8500"))
    rest_port: int = int(os.getenv("TF_SERVING_REST_PORT", "8501"))
    model_name: str = os.getenv("MODEL_NAME", "iris")
    signature_name: str = os.getenv("SIGNATURE_NAME", "serving_default")


class IrisConfig:
    """Iris分類設定"""

    # クラス名
    class_names: Dict[int, str] = {
        0: "setosa",
        1: "versicolor",
        2: "virginica",
    }

    # テストデータ
    test_data = [
        [5.1, 3.5, 1.4, 0.2],  # setosa
        [6.3, 3.3, 6.0, 2.5],  # virginica
        [5.5, 2.4, 3.8, 1.1],  # versicolor
    ]


class WorkerConfig:
    """Worker設定"""

    num_workers: int = int(os.getenv("NUM_WORKERS", "2"))
    brpop_timeout: int = int(os.getenv("BRPOP_TIMEOUT", "1"))  # BRPOPタイムアウト（秒）
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    prediction_timeout: int = int(os.getenv("PREDICTION_TIMEOUT", "10"))  # 推論タイムアウト（秒）


class CacheConfig:
    """キャッシュ設定"""

    job_ttl: int = int(os.getenv("JOB_TTL", "86400"))  # 24時間
